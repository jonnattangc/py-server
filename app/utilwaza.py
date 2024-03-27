try:
    import logging
    import sys
    import os
    import time
    import json
    import requests
    import base64
    import random
    import pymysql.cursors
    from datetime import datetime
    from otp import Otp
    from utilchatbot import UtilChatbot
    from flask import jsonify
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[UtilWaza] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
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
    root = './'

    def __init__(self, root = './'):
        self.root = root
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

    def getCurrentAndNextState( self, user, mobile ) : 
        state = None
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = """select * from user where name = %s and mobile = %s """
                cursor.execute(sql, (user, mobile))
                results = cursor.fetchall()
                for row in results:
                    state = str(row['state'])
        except Exception as e:
            print("ERROR BD:", e)

        return state, self.getNextState( state )
    
    def getNextState( self, state ) :
        next_state = 'RECIVING_IMAGE_CI'
        if state == None :
            return next_state
        elif state == 'RECIVING_IMAGE_CI' :
            next_state = 'RECIVING_IMAGE_FACE' 
        elif state == 'RECIVING_IMAGE_FACE' :
            next_state = 'RECIVING_IMAGE_ACTION' 
        elif state == 'RECIVING_IMAGE_ACTION' :
            next_state = 'VALIDATING_IDENTITY' 
        else :
            next_state = 'RECIVING_IMAGE_CI'
        return next_state   

    def getRandomAction(self) :
        action = 'close_the_eyes'
        action_description = 'con los ojos cerrados'
        index = random.randrange(1, 5)
        if index == 1 :
            action = 'face_to_the_left'
            action_description = 'con la cara levemente a la izquierda'
        elif index == 2 : 
            action = 'face_to_the_right'
            action_description = 'con la cara levemente a la derecha'
        elif index == 3 :
            action = 'close_the_eyes'
            action_description = 'con los ojos cerrados'
        elif index == 4 :
            action = 'smile'
            action_description = 'con una sonrisa'
        elif index == 5 :
            action = 'face_from_far_to_near'
            action_description = 'con la cara lejos de la camara'
        else :
            action = "close_the_eyes"
            action_description = 'con los ojos cerrados'
        return action, action_description

    def getAction( self, user, mobile ) :
        action, action_description = self.getRandomAction()
        try :
            if self.db != None :
                cursor = self.db.cursor()
                now = datetime.now()
                sql = """UPDATE user SET action = %s, update_at = %s WHERE mobile = %s and name = %s"""
                cursor.execute(sql, (action, now.strftime("%Y/%m/%d %H:%M:%S"), str(mobile), str(user) ))
                self.db.commit()
        except Exception as e:
            print("ERROR BD:", e)
        return action_description
    
    def initValidate( self, user, mobile ) :
        try :
            if self.db != None :
                current_state, next_state = self.getCurrentAndNextState( user, mobile )
                now = datetime.now()
                cursor = self.db.cursor()
                if current_state == None :
                    sql = """INSERT INTO user (name, mobile, state, create_at, update_at) VALUES(%s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (str(user), str(mobile), str(next_state), now.strftime("%Y/%m/%d %H:%M:%S"), now.strftime("%Y/%m/%d %H:%M:%S") ))
                else:
                    sql = """UPDATE user SET state = %s, update_at = %s, ci_front = %s , photo = %s, action = %s, action_img = %s, ci_data = %s, life_test_data = %s, rut = %s, sex = %s, nationality = %s, serie = %s, birth = %s, full_name = %s WHERE mobile = %s and name = %s"""
                    cursor.execute(sql, ('RECIVING_IMAGE_CI', now.strftime("%Y/%m/%d %H:%M:%S"), None, None, None, None, None, None, None, None, None, None, None, None, str(mobile), str(user) ))
                self.db.commit()
        except Exception as e:
            print("ERROR BD initValidate():", e)
            self.db.rollback()

    def cleanLeters( self, text ):
        ret = ''
        for leter in text :
            if (leter >= '0' and leter <= '9') or leter == '-' or leter == '.' :
                ret = ret + leter
        return ret
    
    def cleanNumbers( self, text):
        text = text.replace('0', '')
        text = text.replace('1', '')
        text = text.replace('2', '')
        text = text.replace('3', '')
        text = text.replace('4', '')
        text = text.replace('5', '')
        text = text.replace('6', '')
        text = text.replace('7', '')
        text = text.replace('8', '')
        text = text.replace('9', '')
        return text
    
    def getDocNumber( self, doc_num ) :
        if doc_num == None or doc_num == '' :
            return None
        doc_num = self.cleanLeters( str(doc_num) )
        if len(doc_num) >= 11:
            doc_num = doc_num[0:11]
        return doc_num
    
    def getNationality( self, nationality ) :
        if nationality == None or nationality == '' :
            return None
        nationality = self.cleanNumbers( str(nationality) )
        return nationality
    
    def getSex( self, sex ) :
        if sex == None or sex == '' :
            return None
        if str(sex) == 'M' :
            return 'Masculino'
        elif str(sex) == 'F' :
            return 'Femenino'
        else :
            return 'DESCONOCIDO'
    
    def getName( self, name ) :
        full_name = ''
        if name == None or name == '' :
            return None
        name = self.cleanNumbers( str(name) )
        for word in name.split(' ') :
            full_name = full_name + ' ' + word.capitalize()
        return full_name
    
    def getRut( self, rut ) :
        if rut == None or rut == '' :
            return None
        rut = self.cleanLeters(str(rut))
        return rut
    
    def getBirthDate( self, born ) :
        if born == None or born == '' :
            return None
        if len(born) == 3 :
            str_birth = str(born[0])+"/"+str(born[1])+"/"+str(born[2])
            date = datetime.strptime(str_birth, "%d/%m/%Y")
            return date.strftime("%Y/%m/%d %H:%M:%S")
        else :
            return None
    
    def changeDocumentVerificationData( self, user, mobile, data ) :
        state = 'DOCUMENT_VERIFICATION'
        sql = None
        try :
            if self.db != None :
                now = datetime.now()
                cursor = self.db.cursor()
                if data != None:
                    ci_data = data['ci_report']
                    if ci_data != None:
                        full_name = self.getName(ci_data['name'])
                        rut = self.getRut(ci_data['run'])
                        doc_num = self.getDocNumber(ci_data['doc_num'])
                        nationality = self.getNationality(ci_data['nationality'])
                        sex = self.getSex(ci_data['sex'])
                        birdth_date = self.getBirthDate(ci_data['born'])
                        sql = """UPDATE user SET state = %s, update_at = %s, birth = %s, full_name = %s, rut = %s, nationality = %s, sex = %s, serie = %s, ci_data = %s WHERE mobile = %s and name = %s"""
                        cursor.execute(sql, (str(state), now.strftime("%Y/%m/%d %H:%M:%S"), birdth_date, full_name, rut, nationality, sex, doc_num, json.dumps(data), str(mobile), str(user) ))
                        self.db.commit()
        except Exception as e:
            print("ERROR BD changeDocumentVerificationData():", e)
            self.db.rollback()

    def changeUserVerificationData( self, user, mobile, data ) :
        state = 'PROCESS_FINISHED'
        try :
            if self.db != None :
                now = datetime.now()
                cursor = self.db.cursor()
                if data != None:
                    sql = """UPDATE user SET state = %s, life_test_data = %s, update_at = %s WHERE mobile = %s and name = %s"""
                    cursor.execute(sql, ( str(state), json.dumps(data), now.strftime("%Y/%m/%d %H:%M:%S"), str(mobile), str(user) ))
                    self.db.commit()
        except Exception as e:
            print("ERROR BD changeUserVerificationData():", e)
            self.db.rollback()

    def updatedUserImage( self, img, user, mobile ) :
        success = False
        try :
            if self.db != None :
                state, next_state = self.getCurrentAndNextState( user, mobile )
                now = datetime.now()
                cursor = self.db.cursor()
                sql = None
                if state == 'RECIVING_IMAGE_CI' :
                    sql = """UPDATE user SET ci_front = %s, update_at = %s, state = %s WHERE mobile = %s and name = %s"""
                elif state == 'RECIVING_IMAGE_FACE' :
                    sql = """UPDATE user SET photo = %s, update_at = %s, state = %s WHERE mobile = %s and name = %s"""
                elif state == 'RECIVING_IMAGE_ACTION' :
                    sql = """UPDATE user SET action_img = %s, update_at = %s, state = %s WHERE mobile = %s and name = %s"""
                else :
                    sql = None
                    success = False
                if sql != None :
                    cursor.execute(sql, (img , now.strftime("%Y/%m/%d %H:%M:%S"), str(next_state), str(mobile), str(user) ))
                    self.db.commit()
                    success = True
        except Exception as e:
            print("ERROR BD updatedUserImage():", e)
            self.db.rollback()
            success = False
        return success

    def buildResponse(self, user, number, text_rx ) :
        response = ''
        try :
            if text_rx == "/validar" :
                response = 'Hola ' + str(user) + '. Para iniciar el proceso primero toma una fotografia clara y nitida del frente de tu Carnet de Identidad'
                self.initValidate( user, number )
            else :
                chat = UtilChatbot()
                response = chat.sendQuestion(text_rx)
                response = response.replace('Hola', ('Hola ' + str(user)))
                del chat
            self.saveMsgs( text_rx, response, user, number )
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
        # logging.info("URL : " + url )
        try :
            response = requests.post(url, data = json.dumps(data_read_json), headers = self.headers, timeout = 40)
            data_response = response.json()
            if response.status_code != None and response.status_code == 200 :
                data_response = response.json()
                logging.info("Message Marked: " + str( data_response['success'] ) )

        except Exception as e:
            print("ERROR Mark(): ", e)
        
    def responseTextMessage(self, phone_number, msg_id, msg_tx, number_id ) :
        data_json = {
            'messaging_product' : 'whatsapp',
            'recipient_type'    : 'individual',
            'to'                : str(phone_number),
            'context'           : { 'message_id': str(msg_id) }, 
            'type'              : 'text',
            'text'              : { 'preview_url': False, 'body': str(msg_tx), }
        }
        url = 'https://graph.facebook.com/' + str(self.waza_api_version) + '/' + str(number_id) + '/messages'
        try :
            response = requests.post(url, data = json.dumps(data_json), headers = self.headers, timeout = 40)
            data_response = response.json()
            if response.status_code != None and response.status_code == 200 :
                data_response = response.json()
                # logging.info("Response : " + str( data_response ) )
            else:
                logging.error("ErrorResponse : " + str( data_response ) )
        except Exception as e:
            print("ERROR responseTextMessage(): ", e)

    def getComponents(self, client, template) :
       if str(template) == 'init_validation' :
           return [ 
                {
                'type': 'HEADER',
                'parameters': [ { 'type': 'text', 'text': str(client['name'])},] 
                }
            ]
       else :
           return [ 
                {
                'type': 'HEADER',
                'parameters': [ { 'type': 'text', 'text': str(client['company'])},] 
                },
                {
                'type': 'BODY',
                'parameters': [{'type': 'text', 'text': str(client['name'])}] 
                },
            ]
       
    def processMarketingMessage(self, request ) :
        clients = []
        count = 0
        data_rx = {'status':'success', 'statusDescription':'Ok'}
        code = 200
        template = None
        try :
            clients = request['clients']
            count = int(str(request['count']))
            template = str(request['template'])
        except Exception as e:
            print("ERROR Marketing:", e)
            code = 400
            data_rx = {'status':'error', 'statusDescription':'Payload incorrecto'}
        i = 0
        for client in clients :
            logging.info( str(client) )
            data_json = {
                'messaging_product' : 'whatsapp',
                'recipient_type'    : 'individual',
                'to'                : str(client['phone']),
                'type'              : 'template',
                'template': {
                    'name': str(template),
                    'language': {
                        'code': 'es_ES',
                        'policy': 'deterministic'
                    }, 
                    'components': self.getComponents(client, template)
                }
            }
            url = 'https://graph.facebook.com/' + str(self.waza_api_version) + '/' + str(self.waza_phone_id) + '/messages'
            try :
                response = requests.post(url, data = json.dumps(data_json), headers = self.headers, timeout = 40)
                data_response = response.json()
                if response.status_code != None and response.status_code == 200 :
                    data_response = response.json()
                    logging.info("Response : " + str( data_response ) )
                    i = i + 1
                else:
                    logging.error("ErrorResponse : " + str( data_response ) )
            except Exception as e:
                print("ERROR POST:", e)

        if count == i :
            data_rx = {'status':'success', 'statusDescription': 'Mensaje enviado a ' + str(i) + ' clientes'}
        else :
            data_rx = {'status':'warning', 'statusDescription': 'Mensaje enviado a ' + str(i) + ' clientes'}

        return jsonify(data_rx), code
    
    def getValidationStatus(self, user, mobile  ) :
        text = 'Identidad no validada, si quiere iniciar un nuevo proceso ingresa comando /validar'
        send_otp = False
        state = rut = name = sex = birth_date = data_ci = data_life_test = None
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = """select * from user where name = %s and mobile = %s """
                cursor.execute(sql, (user, mobile))
                results = cursor.fetchall()
                for row in results:
                    state = row['state']
                    rut = row['rut']
                    name = row['full_name']
                    sex = row['sex']
                    birth_date = row['birth']
                    # data de los procesos
                    data_ci = row['ci_data'] 
                    data_life_test = row['life_test_data']
                if state != None and str(state) == 'PROCESS_FINISHED' :
                    if data_ci != None and data_life_test != None :
                        text = 'Hola '
                        if name != None :
                            text = text + str(name)
                        if rut != None :
                            text = text + ', Rut ' + str(rut) 
                        if sex != None :
                            text = text + ', Sexo ' + str(sex)
                        if birth_date != None :
                            birth = datetime.strptime(str(birth_date), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                            logging.info("Cumple: " + str( birth ) )
                            text = text + ', Nacido el ' + str(birth)
                        # json_ci = json.loads(data_ci)
                        # json_lt = json.loads(data_life_test)
                        # value_ci_recognition = float(json_ci['face_recognition']['confidence'])
                        # value_life_recognition = float(json_lt['face_recognition']['confidence'])
                        #value = (value_ci_recognition * value_life_recognition) * 100.0
                        send_otp = True
                        text = text + '. Tu Identidad fue validada con exito. En breve recibirás un código de verificación para terminar el proceso'

        except Exception as e:
            print("ERROR getValidationStatus():", e)
        return text, send_otp
    
    def processValidation(self, user, mobile  ) :
        success = False
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = """select * from user where name = %s and mobile = %s """
                cursor.execute(sql, (user, mobile))
                results = cursor.fetchall()
                for row in results:
                    state = str(row['state'])
                    photo = row['photo']
                    ci_front = row['ci_front']
                    action_img = row['action_img']
                    action_str = str(row['action'])

                if state == 'VALIDATING_IDENTITY' and photo != None and ci_front != None and action_img != None and action_str != None :
                    ci = 'image/jpeg,' + base64.b64encode(ci_front).decode('utf-8')
                    face = 'image/jpeg,' + base64.b64encode(ci_front).decode('utf-8')
                    face_action = 'image/jpeg,' + base64.b64encode(action_img).decode('utf-8')

                    data_document_verification = {
                        'document_photo': ci,
                        'face_photo': face,
                        'names': 'A',
                        'lastnames': 'A',
                        'rut': '1',
                        'nationality': 'C',
                        'birth_day': '1',
                        'birth_month': '2',
                        'birth_year': '3'
                    }
                    url_verification = 'http://192.168.0.2:8001/document_verification'
                    try :
                        logging.info('Etapa 1: Verificando documento...')
                        response = requests.post(url_verification, data = json.dumps(data_document_verification), headers = self.headers, timeout = 180)
                        if response.status_code != None and response.status_code == 200 :
                            data_response = response.json()
                            self.changeDocumentVerificationData( user, mobile, data_response )
                            # cara de la persona
                            photos = []
                            photos.append(face)
                            # al menos 2 fotos donde se vea la accion
                            actions_photos = []
                            actions_photos.append(face)
                            actions_photos.append(face_action)
                            data_user_verification = {
                                'known_faces': photos,
                                'faces_to_check': actions_photos,
                                'action': str(action_str)
                            }
                            url_verification = 'http://192.168.0.2:8001/user_verification'
                            logging.info('Etapa 2: Verificando la accion de la persona...')
                            respons_action = requests.post(url_verification, data = json.dumps(data_user_verification), headers = self.headers, timeout = 180)
                            if respons_action.status_code != None and respons_action.status_code == 200 :
                                data_response_action = respons_action.json()
                                self.changeUserVerificationData( user, mobile, data_response_action )
                                success = True
                        else:
                            logging.error("ErrorResponse : " + str( data_response ) )
                            success = False
                    except Exception as e:
                        print("ERROR Verificando Identidad: ", e)
                        success = False
        except Exception as e:
            print("ERROR Procesando CI:", e)
        return success

    def processMultiMediaMessage(self, type, id, number_id, wsnumber, wsuser ) :
        logging.info('Recibiendo objeto multimedia ' + str(type) + ' con Id: ' + str(id) )
        url = 'https://graph.facebook.com/' + str(self.waza_api_version) + '/' + str(id)
        # logging.info("URL : " + url )
        try :
            response = requests.get(url, headers = self.headers, timeout = 30)
            data_response = response.json()
            if response.status_code != None and response.status_code == 200 :
                data_response = response.json()
                logging.info("Response : " + str( data_response ) )
                if str(type) == str(data_response['mime_type']) and str(type) == 'image/jpeg' :
                    media_url = data_response['url']
                    media_response = requests.get(media_url, headers = self.headers, timeout = 30)
                    if media_response.status_code != None and media_response.status_code == 200 :
                        img = media_response.content
                        current_state, next = self.getCurrentAndNextState( wsuser, wsnumber )
                        if current_state != None :
                            if current_state == 'RECIVING_IMAGE_CI' :
                                self.responseTextMessage( wsnumber, -1, "Procesando fotografia de CI", number_id )
                                if self.updatedUserImage( img, wsuser, wsnumber ) :
                                    self.responseTextMessage( wsnumber, -1, "Ahora toma una fotografia de tu rostro, recuerda que debe ser clara y nítida", number_id )
                            elif current_state == 'RECIVING_IMAGE_FACE' :
                                self.responseTextMessage( wsnumber, -1, "Procesando fotografia de tu rostro", number_id )
                                if self.updatedUserImage( img, wsuser, wsnumber ) :
                                    action = self.getAction( wsuser, wsnumber )
                                    self.responseTextMessage( wsnumber, -1, "Finalmente toma una fotografia " + str(action), number_id )   
                            elif current_state == 'RECIVING_IMAGE_ACTION' :
                                self.responseTextMessage( wsnumber, -1, "Espera un momento, ya estamos validando tu identidad... Este proceso puede durar de 10 a 20 segundos.", number_id )
                                if self.updatedUserImage( img, wsuser, wsnumber ) :
                                    if self.processValidation( wsuser, wsnumber ) :
                                        msg, send = self.getValidationStatus( wsuser, wsnumber )         
                                        self.responseTextMessage( wsnumber, -1, msg, number_id )
                                        if send :
                                            data_for_otp = {
                                                'number_mobile' : wsnumber,
                                                'duration_min' : 5,
                                                'length_otp': 6
                                            }
                                            self.generateAndSendOtp( data_for_otp )
                                    else :
                                        self.responseTextMessage( wsnumber, -1, "El proceso ha fallado, por favor inicia nuevamente usando comando /validar", number_id )
                            elif current_state == 'VALIDATING_CI' :
                                self.responseTextMessage( wsnumber, -1, "Validando tu identidad...", number_id )
                            else :
                                self.responseTextMessage( wsnumber, -1, "Proceso ya ha finalizado, espera un momento más...", number_id )
                                
                                    
                    else:
                        logging.error("CodeResponse : " + str( img.status_code ) )
            else:
                logging.error("ErrorResponse : " + str( data_response ) )
        except Exception as e:
            print("ERROR Rescatando processMultiMediaMessage():", e)

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
                wsuser = contacts[0]['profile']['name']
                wsnumber = contacts[0]['wa_id']
                msg_id = messages[0]['id']
                self.markasReader( msg_id, number_id )
                msg_type = messages[0]['type']
                if str(msg_type) == 'text'  :
                    msg_rx = messages[0]['text']['body']
                    msg_tx = self.buildResponse( wsuser, wsnumber, msg_rx )
                    self.responseTextMessage( wsnumber, msg_id, msg_tx, number_id )
                elif str(msg_type) == 'request_welcome'  :
                    code = 200
                else :
                    logging.info("Mensajes Multimedia: Tipo[" + str(msg_type) + "] number_id[" + str(number_id) + "] name_wsuser[" + str(wsuser) + "] wsnumber[" + str(wsnumber) + "]")
                    state, next = self.getCurrentAndNextState( wsuser, wsnumber)
                    if state == None :
                        self.responseTextMessage( wsnumber, msg_id, 'Para procesar imagenes debes iniciar la validación. Escribe comando /validar', number_id )
                    else :
                        obj_rx_type = messages[0][str(msg_type)]['mime_type']
                        obj_rx_id = messages[0][str(msg_type)]['id']
                        self.processMultiMediaMessage( obj_rx_type, obj_rx_id, number_id, wsnumber, wsuser )
                
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
        otp, ref = otpProccesor.createOtp( mobile = number, whatsapp = True, duration_min = int(duration), len = int(length) )
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
            # logging.info("Reciv Header : " + str(request.headers) )
            # logging.info("Contex: " + str(subpath) )
            # logging.info("Reciv Data: " + str(request.data) )
            # logging.info("Reciv Params: " + str(request.args) )
            # valores por defecto
            data_response = jsonify({'statusCode': 500, 'statusDescription': 'Error en la ejecucion del servicio' })
            errorCode = 500
            m1 = time.monotonic()
            try :
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
                        elif str(subpath) == 'marketing' :
                            data_response, errorCode = self.processMarketingMessage( request_data )
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
            except Exception as e:
                print("ERROR requestProcess(): ", e)
            diff = time.monotonic() - m1;
            logging.info('================================== Time Response in ' + str(diff) + ' sec. ===============================================')
            
            return data_response, errorCode
    
