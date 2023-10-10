try:
    import logging
    import sys
    import os
    import time
    import boto3
    import base64
    import uuid
    from otp import Otp
    from werkzeug.utils import secure_filename
    from botocore.exceptions import ClientError

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class AwsUtil() :
    url_base = 'https://s3.__AWS_REGION__.amazonaws.com/'
    access_key = os.environ.get('AWS_ACCESS_KEY','None')
    secret_key = os.environ.get('AWS_SECRET_KEY','None')
    app_id = os.environ.get('AWS_PINPOINT_APP_ID','None')
    bucket_name = os.environ.get('AWS_S3_BUCKET','None')
    s3_resource = None
    s3 = None
    sns = None
    pinpoint = None 
    ses = None
    root = '.'

    # ==============================================================================
    # Constructor
    # ==============================================================================
    def __init__(self, root = '.', region='us-east-1') :
        self.url_base = self.url_base.replace('__AWS_REGION__', region)
        try :
            self.root = str(root)
            self.sns = boto3.client('sns', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name=region)
            self.pinpoint = boto3.client('pinpoint', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name=region)
            self.ses = boto3.client('ses', aws_access_key_id=self.access_key,aws_secret_access_key=self.secret_key, region_name=region)
            session = boto3.Session(aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
            self.s3_resource = session.resource('s3')
            self.s3 = boto3.client('s3')
            logging.info("Session Available Resources: " + str(session.get_available_resources()) )
        except Exception as e:
            print("[__init__] ERROR AWS:", e)

    # ==============================================================================
    # Destructor
    # ==============================================================================
    def __del__(self):
        self.url_base = 'https://s3.__AWS_REGION__.amazonaws.com/'
        del self.s3_resource
        del self.sns
        del self.pinpoint
        del self.ses
        self.s3_resource = None
        self.sns = None
        self.pinpoint = None
        self.ses = None

    # ==============================================================================
    # Procesa todos los request 
    # ==============================================================================
    def requestProcess(self, request, action ) :
        logging.info("############################ AWS Util ##############################" )
        logging.info("Reciv " + str(request.method) + " Acción: " + str(action) )
        logging.info("Reciv Data: " + str(request.data) )
        logging.info("Reciv Header : " + str(request.headers) )
        
        data = {'status':'Error ocurrido'}
        status = 409
        if action != None :   
            if str(action) == 's3/list' :
                return self.s3ObjectList()
            elif str(action) == 'pinpoint/info' :
                return self.pinpointInfo()
            elif str(action) == 'ses/info' :
                return self.sesInfo()
            elif str(action) == 'ses/sendmail' :
                request_data = request.get_json()
                mail = str(request_data['mail'])
                return self.sendMailOtp( mail )
            elif str(action) == 'pinpoint/sendotp' :
                request_data = request.get_json()
                mobile = str(request_data['mobile'])
                if mobile != None and request.method == 'POST' :
                    return self.sendSmsOtp( mobile )
            elif str(action) == 'sns/sendsms' : 
                request_data = request.get_json()
                mobile = str(request_data['mobile'])
                if mobile != None and request.method == 'POST' :
                    return self.sendSMS( mobile )
            elif str(action) == 'pinpoint/validateotp' :
                request_data = request.get_json()
                channel = str(request_data['channel'])
                otp = str(request_data['otp'])
                if channel != None and request.method == 'POST' :
                    return self.validateOtp( channel, otp, )
            elif str(action) == 'contents' :
                return self.testAws()
            elif str(action) == 'file/upload' :
                return self.s3Uploader( request )
            else :
                data = {'status':'No Implementedo'}
                status = 409
        return data, status
    
    def s3Uploader( self, request ) :
        data = {'ref': 'Servicio Ejecutado exitosamente'}
        code = 200
        m1 = time.monotonic_ns()
        try :
            request_data = request.get_json()
            name_file = str(request_data['name'])
            name_file = 'photos/' + str(uuid.uuid4()) + '-' + name_file

            data = str(request_data['data'])
            data = data.replace('data:image/png;base64,','')

            name = 'test.png'
            file_path = os.path.join(self.root, 'static')
            file_path = os.path.join(file_path, 'images')
            file_path = os.path.join(file_path, str(name))

            file = open(file_path, 'wb')
            file.write( base64.b64decode((data) ))
            file.close()

            logging.info('[S3] Archivo a subir: ' + str(file_path))
            logging.info('[S3] Nombre: ' + str(name_file))
            
            s3_bucket = self.s3_resource.Bucket(name=self.bucket_name)
            s3_bucket.upload_file( Filename=file_path, Key=name_file )
            data = { 
                'url': str(self.url_base) + str(self.bucket_name) + '/' + str(name_file),
                'msg': 'Servicio ejecutado exitosamente',
                'code': 0
            }


        except Exception as e:
            print("[S3] ERROR AWS:", e)
            code = 403
            data = { 'ref': 'Error: ' + str(e) }

        diff = time.monotonic_ns() - m1
        logging.info("[S3] Servicio Ejecutado en " + str(diff) + " nsec." )
        return data, code 


    # ==============================================================================
    # Envia mail a trav'es de SES de AWS
    # ==============================================================================
    def sendMailOtp( self, mail ) :
        retorno = {'ref': ''}
        status = 200
        otpGenerator = Otp()
        otp, ref = otpGenerator.createOtp(mail = mail)
        del otpGenerator
        m1 = time.monotonic_ns()
        response = {}
        try :
            logging.info("[SES] Send mail to: " + str(mail) + " ref: " + str(ref))
            if self.ses != None :
                data = 'From: soporte@jonnattan.com\nTo: ' + str(mail) + '\nSubject: Jonnattan SpA OTP\nMIME-Version: 1.0\nContent-type: Multipart/Mixed; boundary="NextPart"\n\n--NextPart\nContent-Type: text/plain\n\nLa OTP para sistema es: ' + str(otp) + '.\n\n'
                response = self.ses.send_raw_email(Destinations=[str(mail),], RawMessage={ 'Data': data,  },)
                logging.info("[SES] Send Email: " + str(response) )
                retorno = {'ref': str(ref) }
        except Exception as e:
            print("[SES] ERROR AWS:", e)
            status = 500
            retorno = { 'ref': 'Error: ' + str(e) }
        diff = time.monotonic_ns() - m1
        logging.info("[SES] Servicio Ejecutado en " + str(diff) + " msec." )
        return retorno, status 
    # ==============================================================================
    # Envia OTP por SMS con Servicio Pinpoint
    # ==============================================================================
    def sendSmsOtp( self, mobile ) :
        retorno = {'ref': ''}
        status = 200
        m1 = time.monotonic_ns()
        otpProccesor = Otp()
        otp, ref = otpProccesor.createOtp(mobile = mobile)
        try :
            logging.info("[PINTPOINT] Send sms to: " + str(mobile) + " ref: " + str(ref))
            if self.pinpoint != None :
                solicitude = {
                        'AllowedAttempts': otpProccesor.getAttempts(),
                        'BrandName': 'Jonnattan SpA',
                        'Channel': 'SMS',
                        'CodeLength':  otpProccesor.getLengthCode(),
                        'DestinationIdentity': str(mobile),
                        'Language': 'es-ES',
                        'OriginationIdentity': 'OrigenJonna',
                        'ReferenceId': str(ref),
                        'ValidityPeriod': otpProccesor.getDuration()
                }
                response = self.pinpoint.send_otp_message(
                    ApplicationId=str(self.app_id), SendOTPMessageRequestParameters= solicitude)
                logging.info("[PINTPOINT] Response Send OTP: " + str(response) )
                retorno = {'ref': str(ref) }
        except Exception as e:
            print("[PINTPOINT] ERROR AWS:", e)
            status = 500
            retorno = { 'ref': 'Error: ' + str(e) }
        del otpProccesor
        diff = time.monotonic_ns() - m1
        logging.info("[PINTPOINT] Servicio Ejecutado en " + str(diff) + " nsec." )
        return retorno, status 
    # ==============================================================================
    # Muestra la informaci'on del servicio
    # ==============================================================================
    def pinpointInfo( self ) :
        retorno = {'status': 'ok'}
        status = 200
        m1 = time.monotonic()
        try :
            logging.info( "[PINTPOINT] Info de servicio" )
            if self.pinpoint != None :
                logging.info("[PINTPOINT] ==============================get_email_channel==============================================" )
                response = self.pinpoint.get_email_channel(ApplicationId=str(self.app_id))
                logging.info("Response: " + str(response) )
                logging.info("[PINTPOINT] ============================================================================" )

                logging.info("[PINTPOINT] ================================get_app============================================" )
                response = self.pinpoint.get_app(ApplicationId=str(self.app_id))
                logging.info("Response: " + str(response) )
                logging.info("[PINTPOINT] ============================================================================" )

                logging.info("[PINTPOINT] ================================get_channels============================================" )
                response = self.pinpoint.get_channels(ApplicationId=str(self.app_id))
                logging.info("Response: " + str(response) )
                logging.info("[PINTPOINT] ============================================================================" )
                
        except Exception as e:
            print("[PINTPOINT] ERROR AWS:", e)
            status = 500
            retorno = { 'status': 'Salto una excepcion !' }
        diff = time.monotonic() - m1
        logging.info("[PINTPOINT] Servicio Ejecutado en " + str(diff) + " msec." )
        return retorno, status 
    # ==============================================================================
    # Muestra la informaci'on del servicio
    # ==============================================================================
    def sesInfo( self ) :
        retorno = {'status': 'ok'}
        status = 200
        m1 = time.monotonic()
        try :
            logging.info( "[SES] Info de servicio" )
            if self.ses != None :
                logging.info("[SES] ==============================get_send_quota==============================================" )
                response = self.ses.get_send_quota()
                logging.info("Response: " + str(response) )
                logging.info("[SES] ============================================================================" )
                
        except Exception as e:
            print("[SES] ERROR AWS:", e)
            status = 500
            retorno = { 'status': 'Salto una excepcion !' }
        diff = time.monotonic() - m1
        logging.info("[SES] Servicio Ejecutado en " + str(diff) + " msec." )
        return retorno, status 
    
    def testAws( self ) :
        retorno = {'valid': False }
        status = 200
        m1 = time.monotonic()
        try :
            retorno = {'valid': self.s3_resource != None and self.pinpoint != None and self.ses != None and self.sns != None } 
        except Exception as e:
            print("[STATUS] ERROR AWS:", e)
            status = 500
        diff = time.monotonic() - m1
        logging.info("[STATUS] Servicio Ejecutado en " + str(diff) + " msec." )
        return retorno, status 
    # ==============================================================================
    # Valida la OTP
    # ==============================================================================
    def validateOtp( self, channel, otp ) :
        retorno = {'valid': False }
        status = 403
        m1 = time.monotonic()
        try :
            otpProcess = Otp()
            valid, ref = otpProcess.mailOtpValidate( channel, otp )
            logging.info( "[PINTPOINT] Se valida OTP[" + str(otp) + "] Recibida por " + str(channel) )
            if self.pinpoint != None :
                if valid == None and ref != None:
                    validation = {
                            'DestinationIdentity': str(channel),
                            'Otp':  str(otp),
                            'ReferenceId': str(ref)
                    }
                    response = self.pinpoint.verify_otp_message(ApplicationId=str(self.app_id), VerifyOTPMessageRequestParameters= validation)
                    logging.info("[PINTPOINT] Valid: " + str(response['VerificationResponse']['Valid']) )
                    valid = response['VerificationResponse']['Valid']
            otpProcess.burnOtp( ref, valid )
            del otpProcess
            retorno = { 'valid': valid }
            if valid : status = 200

        except Exception as e:
            print("[PINTPOINT] ERROR AWS:", e)
            status = 500
        diff = time.monotonic() - m1
        logging.info("[PINTPOINT] Servicio Ejecutado en " + str(diff) + " msec." )
        return retorno, status 
    # ==============================================================================
    # Envia OTP por SMS con Servicio SNS
    # ==============================================================================
    def sendSMS( self, mobile ) :
        retorno = {
            'status': 'ok'
        }
        status = 200
        m1 = time.monotonic_ns()
        try :
            logging.info("[SNS] Trabajo con " + str(mobile) )
            if self.sns != None :
                # falta cosas aca
                resp = self.sns.create_sms_sandbox_phone_number(PhoneNumber = str(mobile), LanguageCode = 'es-ES')
                logging.info("[SNS] Create SMS " + str(resp) )
                resp = self.sns.get_sms_sandbox_account_status()
                logging.info("[SNS] Estado de la cuenta " + str(resp) )
        except Exception as e:
            print("[SNS] ERROR AWS:", e)
            status = 500
            retorno = { 'status': 'Salto una excepcion !' }
        diff = time.monotonic_ns() - m1
        logging.info("[SNS] Cliente creado " + str(diff) + " nsec." )
        return retorno, status 
    # ==============================================================================
    # Lista de cosas en s3
    # ==============================================================================
    def s3ObjectList( self ) :
        http_code = 409
        data = {}
        m1 = time.monotonic_ns()
        try :
            photos = self.getPhotos()
            docs = self.getDocs()
            data = {
                'photos' : str(photos),
                'docs' : str(docs)
            }
            http_code = 200
        except Exception as e:
            print("ERROR AWS:", e)
            http_code = 500
            data = { 'status': 'Salto una excepcion !' }

        diff = time.monotonic_ns() - m1
        logging.info('Service Time Response in ' + str(diff) + ' nsec' )
        return data, http_code 
    # ==============================================================================
    # Lista de fotos en s3
    # ==============================================================================
    def getPhotos( self ) :
        elements = []
        m1 = time.monotonic_ns()
        try :
            if self.s3_resource != None :
                logging.info('[Photos] s3_resource: ' + str(self.s3_resource) )
                for bucket in self.s3_resource.buckets.all():
                    logging.info('[Photos] Bucket: ' + bucket.name)
                    #contents = s3.Bucket(bucket.name)
                    for obj in bucket.objects.filter(Prefix='photos/') :
                        logging.info('[Photos] Bucket: ' + obj.bucket_name + ' Key: ' + obj.key)
                        elements.append({'url' : self.url_base + obj.bucket_name + '/' + obj.key })
        except Exception as e:
            print("[Photos] ERROR AWS:", e)
            elements = []

        diff = time.monotonic_ns() - m1
        logging.info("[Photos] AWS Time S3 Photos Response in " + str(diff) + " nsec." )
        return elements 
    # ==============================================================================
    # Lista de documentos en s3
    # ==============================================================================
    def getDocs( self ) :
        elements = []
        m1 = time.monotonic_ns()
        try :
            if self.s3_resource != None :
                logging.info('[Photos] s3_resource: ' + str(self.s3_resource) )
                for bucket in self.s3_resource.buckets.all():
                    logging.info('[Docs] Bucket: ' + bucket.name)
                    #contents = s3_resource.Bucket(bucket.name)
                    for obj in bucket.objects.filter(Prefix='docs/') :
                        logging.info('[Docs] Bucket: ' + obj.bucket_name + ' Key: ' + obj.key)
                        elements.append({'url' : self.url_base + obj.bucket_name + '/' + obj.key })
        except Exception as e:
            print("[Docs] ERROR AWS:", e)
            elements = []

        diff = time.monotonic_ns() - m1
        logging.info("[Docs] AWS Time S3 Docs Response in " + str(diff) + " nsec." )
        return elements
