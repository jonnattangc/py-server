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
    database = 'gral-purpose'
    environment = None
    bearer_token = 'Bearer EAAYptQZApMksBOZC2a5N8bX4ybT1g1iZBcB632MF0hNnqfy56mjcHY8b7WOc2AijVUsvgW7yFlIR6h5E9YcKEV9N5ZAiRdYvu6SRJ4gud7oRhMcbi9mZBCykrhMRzboMcXgX9qmUYvkLGd9tb2dq9k8XAT7d2WxXWlBTvZBTBdnZB7lKkXiKelmUZARGx748XMccSNHMepFwAlU7EmVZB3XeeohMBnNYcNdoD1gZDZD'
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
        response = 'Hola ' + str(user) + '!!, cómo puedo ayudarte ?'
        self.saveMsgs( text_rx, response, user, number )
        return response

    def responseWazaMessage(self, change ) :

        contacts = None
        statuses = None
        messages = None

        if str(change['field']) == 'messages' :
            meta_msg = change['value']

            try :
                contacts = meta_msg['contacts']
            except Exception as e:
                print("ERROR contacts:", e)
                contacts = None
            try :
                statuses = meta_msg['statuses']
            except Exception as e:
                print("ERROR statuses:", e)
                statuses = None
            try :
                messages = meta_msg['messages']
            except Exception as e:
                print("ERROR messages:", e)
                messages = None

            if str(meta_msg['messaging_product']) == 'whatsapp' and statuses != None :
                logging.info("Mensaje liberado a: " + str(statuses[0]['recipient_id']) )

            if str(meta_msg['messaging_product']) == 'whatsapp' and contacts != None :

                name_id_number = meta_msg['metadata']['phone_number_id']

                name_wsuser = contacts[0]['profile']['name']
                name_wsuser = contacts[0]['profile']['name']

                name_wsuser = contacts[0]['profile']['name']
                name_wsnumber = contacts[0]['wa_id']

                msg_id = messages[0]['id']
                msg_text = messages[0]['text']['body']

                logging.info("ID   : " + str(msg_id) )

                msgTx = self.buildResponse( name_wsuser, name_wsnumber, msg_text )

                data_read_json = {
                    'messaging_product' : 'whatsapp',
                    'status'            : 'read',
                    'message_id'        : str(msg_id)
                }

                data_json = {
                    'messaging_product' : 'whatsapp',
                    'recipient_type'    : 'individual',
                    'to'                : str(name_wsnumber),
                    'context'           : { 'message_id': str(msg_id) },
                    'type'              : 'text',
                    'text'              : { 'preview_url': False, 'body': str(msgTx), }
                }

                # logging.info("Request Trx " + str(data_json) )
                url = 'https://graph.facebook.com/v17.0/' + str(name_id_number) + '/messages'
                logging.info("URL : " + url )

                try :
                    response = requests.post(url, data = json.dumps(data_read_json), headers = self.headers, timeout = 40)
                    data_response = response.json()
                    if response.status_code != None and response.status_code == 200 :
                        data_response = response.json()
                        logging.info("Response Status Read: " + str( data_response['success'] ) )

                except Exception as e:
                    print("ERROR Status:", e)

                try :
                    response = requests.post(url, data = json.dumps(data_json), headers = self.headers, timeout = 40)
                    logging.info("Response : " + str( response ) )
                    data_response = response.json()
                    logging.info("Response JSON : " + str( data_response ) )

                    if response.status_code != None and response.status_code == 200 :
                        data_response = response.json()
                        logging.info("Response : " + str( data_response ) )

                except Exception as e:
                    print("ERROR POST:", e)

        return 'ok', 200


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
        isValid, code = otpProccesor.validateOtp( reference, otp )
        del otpProccesor
        data = {
            'success' : isValid
        }
        return jsonify(data), code

    def requestProcess(self, request, subpath ) :
            logging.info('########################## ' + str(request.method) + ' ###################################')
            logging.info("Reciv Header : " + str(request.headers) )
            logging.info("Contex: " + str(subpath) )
            logging.info("Reciv Data: " + str(request.data) )
            # valores por defecto
            data_response = jsonify({'statusCode': 200, 'statusDescription': 'Servicio ejecutado exitosamente' })
            errorCode = 200
            request_data = request.get_json()
            try :
                m1 = time.monotonic()
                if subpath == None :
                    if str(request_data['object']) == 'whatsapp_business_account' :
                        entries = request_data['entry']
                        data_response, errorCode = self.responseWazaMessage( entries[0]['changes'][0] )
                    value = str(request.args.get('hub.challenge', '-1'))
                    if value != '-1' :
                        data_response = str(value)
                        logging.info("hub.challenge: " + str(data_response) )
                else :
                    if str(subpath) == 'generate' :
                        data_response, errorCode = self.generateAndSendOtp( request_data )
                    elif str(subpath) == 'validate' :
                        data_response, errorCode = self.validateOtp( request_data )
                    else :
                        data_response = jsonify({'statusCode': 404, 'statusDescription': 'Servicio no encontrado' })
                        errorCode = 404
                diff = time.monotonic() - m1;
                logging.info("Time Response in " + str(diff) + " sec." )
            except Exception as e:
                print("ERROR POST:", e)
            return data_response, errorCode
