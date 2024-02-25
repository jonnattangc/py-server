try:
    import logging
    import sys
    import os
    import time
    import json
    import requests
    import pymysql.cursors
    from datetime import datetime, timedelta
    from otp import Otp
    from utilchatbot import UtilChatbot
    from flask import Flask, render_template, abort, make_response, request, redirect, jsonify, send_from_directory
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class UtilWaza() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD','None') 
    password = os.environ.get('PASS_BD','None')
    waza_token = os.environ.get('WAZA_BEARER_TOKEN','None')
    waza_phone_id = os.environ.get('PHONE_ID','None')
    waza_api_version = os.environ.get('WAZA_API_VERSION','None')
    database = 'gral-purpose'
    environment = None
    bearer_token = 'Bearer ' + str(waza_token)
    headers = None

    def __init__(self) :
        try:
            self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
            self.headers = {'Content-Type': 'application/json', 'Authorization': str(self.bearer_token) }
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def __del__(self):
        if self.db != None:
            self.db.close()

    def connect( self ) :
        try:
            if self.db == None :
                self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def isConnect(self) :
        return self.db != None

    def saveMsgs( self, msg_rx, msg_tx, user, mobile ) :
        try :
            if self.db != None :
                now = datetime.now()
                cursor = self.db.cursor()
                sql = """INSERT INTO whatsapp_messages (msg_rx, msg_tx, users, mobiles, create_at, update_at) VALUES(%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (str(msg_rx), str(msg_tx), str(user), str(mobile), now.strftime("%Y/%m/%d %H:%M:%S"), now.strftime("%Y/%m/%d %H:%M:%S") ))
                self.db.commit()
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()


    def buildResponse(self, user, number, text_rx ) :
        response = ''
        try :
            chat = UtilChatbot()
            response = chat.sendQuestion(text_rx)
            response = response.replace('Hola', ('Hola ' + str(user)))
            self.saveMsgs( text_rx, response, user, number )
            del chat
        except Exception as e:
            print("ERROR Fabricando Respuesta:", e)
        return response

    def markasReader( self, msg_id, number_id ) :
        data_read_json = {
            'messaging_product' : 'whatsapp',
            'status'            : 'read',
            'message_id'        : str(msg_id)
        }
        url = 'https://graph.facebook.com/' + str(self.waza_api_version) + '/' + str(number_id) + '/messages'
        logging.info("URL : " + url )

        try :
            response = requests.post(url, data = json.dumps(data_read_json), headers = self.headers, timeout = 40)
            data_response = response.json()
            if response.status_code != None and response.status_code == 200 :
                data_response = response.json()
                logging.info("Response Status Read: " + str( data_response['success'] ) )

        except Exception as e:
            print("ERROR Read Response:", e)
        
    def responseTextMessage(self, phone_number, msg_id, msg_tx, number_id ) :
        data_json = {
            'messaging_product' : 'whatsapp',
            'recipient_type'    : 'individual',
            'to'                : str(phone_number),
            'context'           : { 'message_id': str(msg_id) },
            'type'              : 'text',
            'text'              : { 'preview_url': False, 'body': str(msg_tx), }
        }

        # logging.info("Request Trx " + str(data_json) )
        url = 'https://graph.facebook.com/' + str(self.waza_api_version) + '/' + str(number_id) + '/messages'
        logging.info("URL : " + url )

        try :
            response = requests.post(url, data = json.dumps(data_json), headers = self.headers, timeout = 40)
            data_response = response.json()
            if response.status_code != None and response.status_code == 200 :
                data_response = response.json()
                logging.info("Response : " + str( data_response ) )
            else:
                logging.error("ErrorResponse : " + str( data_response ) )
        except Exception as e:
            print("ERROR POST:", e)

    def responseWazaMessage(self, change ) :

        contacts = None
        statuses = None
        messages = None

        response = "Ok"
        code = 200

        field = str(change['field'])

        if field == 'messages' :
            meta_msg = change['value']

            try :
                contacts = meta_msg['contacts']
            except Exception as e:
                # print("ERROR contacts:", e)
                contacts = None
            try :
                statuses = meta_msg['statuses']
            except Exception as e:
                # print("ERROR statuses:", e)
                statuses = None
            try :
                messages = meta_msg['messages']
            except Exception as e:
                # print("ERROR messages:", e)
                messages = None

            if str(meta_msg['messaging_product']) == 'whatsapp' and statuses != None :
                logging.info("Un mensaje fue liberado a: " + str(statuses[0]['recipient_id']) )

            if str(meta_msg['messaging_product']) == 'whatsapp' and contacts != None :

                number_id = meta_msg['metadata']['phone_number_id']

                name_wsuser = contacts[0]['profile']['name']
                name_wsuser = contacts[0]['profile']['name']

                name_wsuser = contacts[0]['profile']['name']
                name_wsnumber = contacts[0]['wa_id']

                msg_id = messages[0]['id']
                self.markasReader(msg_id, number_id )
                msg_type = messages[0]['type']
                if str(msg_type) == 'text'  :
                    msg_rx = messages[0]['text']['body']
                    msg_tx = self.buildResponse( name_wsuser, name_wsnumber, msg_rx )
                    self.responseTextMessage( name_wsnumber, msg_id, msg_tx, number_id )
                elif str(msg_type) == 'image' :
                    obj_rx_type = messages[0]['image']['mime_type']
                    obj_rx_id = messages[0]['image']['id']
                    logging.info("Se recibio una imagen " + str(obj_rx_id) + " del tipo " + str(obj_rx_type) )
                elif str(msg_type) == 'audio' :
                    obj_rx_type = messages[0]['audio']['mime_type']
                    obj_rx_id = messages[0]['audio']['id']
                    logging.info("Se recibio un audio " + str(obj_rx_id) + " del tipo " + str(obj_rx_type) )
                else :
                    logging.error('No procesado !!!!')

                
        elif field != None :
            response = "No hay procesamiento para este tipo de mensaje: " + field
            code = 200
        else :
            response = "No hay procesamiento para este tipo de mensaje"
            code = 200
        return response, code

    def generateAndSendOtp(self, data_rx ) :
        number = str(data_rx['number_mobile'])
        number = number.replace(' ', '')
        number = number.replace('+', '')
        duration = str(data_rx['duration_min'])
        length = str(data_rx['length_otp'])

        otpProccesor = Otp()
        otp, ref = otpProccesor.createOtp( whatsapp = number, duration_min = int(duration), len = int(length) )
        del otpProccesor

        logging.info("OTP : " + str(otp) )

        data = {'statusCode': 402, 'statusDescription': 'Error en generacion de OTP' }
        code = 402

        try :
            data_json = {
                'messaging_product' : 'whatsapp',
                'recipient_type'    : 'individual',
                'to'                : str(number),
                'type'              : 'template',
                'template': {
                   'name': "otp_dicode",
                   'language': {
                       'code': 'es_MX',
                       'policy': 'deterministic'
                    },
                    'components': [
                          {
                            'type': 'BODY',
                            'parameters': [
                              {
                                'type': 'text',
                                'text': str(otp)
                              }
                            ]
                          },
                          {
                            'type': 'BUTTON',
                            'sub_type': 'url',
                            'index': 0,
                            'parameters': [
                              {
                                'type': 'text',
                                'text': str(otp)
                              }
                            ]
                          }
                    ]
                }
            }
            # logging.info("Request Trx " + str(data_json) )
            url = 'https://graph.facebook.com/v17.0/107854109079987/messages'
            logging.info("URL : " + url )
            response = requests.post(url, data = json.dumps(data_json), headers = self.headers, timeout = 40)
            data_response = response.json()
            if response.status_code != None :
                code = response.status_code
                if response.status_code == 200 :
                    data_response = response.json()
                    logging.info("Response JSON: " + str( data_response ) )
                    data = {
                        'ref'   : str(ref),
                        'channel' : 'whatsapp',
                        'duration_min': str(duration)
                    }
        except Exception as e:
            print("ERROR SENT OTP:", e)

        return jsonify(data), code

    def validateOtp(self, data_rx ) :
        reference = str(data_rx['reference'])
        otp = str(data_rx['otp'])
        otpProccesor = Otp()
        isValid, reason = otpProccesor.validateOtp( reference, otp )
        del otpProccesor
        dataTx = {
            'success' : isValid,
            'statusDescription' : reason
        }
        logging.info("######### RESPONSE : " + str(dataTx) )
        return jsonify(dataTx), 200

    def requestProcess(self, request, subpath ) :
            logging.info('########################## ' + str(request.method) + ' ###################################')
            logging.info("Reciv Header : " + str(request.headers) )
            logging.info("Contex: " + str(subpath) )
            logging.info("Reciv Data: " + str(request.data) )
            logging.info("Reciv Params: " + str(request.args) )
            logging.info('################################################################')
            # valores por defecto
            data_response = jsonify({'statusCode': 500, 'statusDescription': 'Error en la ejecucion del servicio' })
            errorCode = 500
            try :
                m1 = time.monotonic()
                if str(request.method) == 'GET' :
                    if str(request.args.get('hub.mode')) == 'subscribe' :
                        data_response = str(request.args.get('hub.challenge'))
                        errorCode = 200
                elif str(request.method) == 'POST' :
                    request_data = request.get_json()
                    if subpath != None :
                        if str(subpath) == 'generate' :
                            data_response, errorCode = self.generateAndSendOtp( request_data )
                        elif str(subpath) == 'validate' :
                            data_response, errorCode = self.validateOtp( request_data )
                        else :
                            data_response = jsonify({'statusCode': 404, 'statusDescription': 'Servicio no encontrado' })
                            errorCode = 404
                    else :
                        if str(request_data['object']) == 'whatsapp_business_account' :
                            entries = request_data['entry']
                            message, errorCode = self.responseWazaMessage( entries[0]['changes'][0] )
                            data_response = jsonify({'statusCode': errorCode, 'statusDescription': str(message) })
                        # Esto responde a la inscriopcion de un webhook de whatsapp
                        value = str(request.args.get('hub.challenge', '-1'))
                        if value != '-1' :
                            data_response = str(value)
                            logging.info("hub.challenge: " + str(data_response) )
                else :
                    data_response = jsonify({'statusCode': 404, 'statusDescription': 'Metodo no disponible' })
                    errorCode = 404
                diff = time.monotonic() - m1;
                logging.info("Time Response in " + str(diff) + " sec." )
            except Exception as e:
                print("ERROR POST:", e)
            return data_response, errorCode
    
