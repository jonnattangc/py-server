try:
    import logging
    import sys
    import os
    import pymysql.cursors
    from datetime import datetime
    from flask import render_template

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['[UCC] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class Ucc() :
    db = None
    api_key = None

    def __init__(self) :
        try:
            host = str(os.environ.get('HOST_BD','dev.jonnattan.com'))
            port = int(os.environ.get('PORT_BD', 3306))
            user_bd = str(os.environ.get('USER_BD','----'))
            pass_bd = str(os.environ.get('PASS_BD','*****'))
            eschema = str(os.environ.get('SCHEMA_BD','*****'))
            self.db = pymysql.connect(host=host, port=port, 
                user=user_bd, password=pass_bd, database=eschema, 
                cursorclass=pymysql.cursors.DictCursor)
            self.api_key = str(os.environ.get('UCC_API_KEY','None'))
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None
            self.api_key = None

    def __del__(self):
        if self.db != None:
            self.db.close()
        self.api_key = None

    def isConnect(self) :
        return self.db != None

    def get_info(self, rut) :
        logging.info("Information to rut: " + str(rut) )
        data = None
        if self.isConnect() : 
            try :
                if self.db != None :
                    cursor = self.db.cursor()
                    sql = """select * from user where rut = %s"""
                    cursor.execute(sql, (rut))
                    results = cursor.fetchall()
                    for row in results:
                        date_bd = str(row['birth'])
                        date_send = datetime.strptime(date_bd, '%Y-%m-%d %H:%M:%S')
                        date_birth = date_send.strftime('%Y-%m-%d')
                        data = {
                            'rut'  : str(row['rut']),
                            'name'  : str(row['name']),
                            'adrs'  : str(row['address']),
                            'adrcom'  : str(row['comercial_address']),
                            'mobile'  : str(row['mobile']),
                            'phone'  : str(row['mobile']),
                            'commune'  : str(row['commune']),
                            'mail'  : str(row['mail']),
                            'birth'  : str(date_birth),
                        }
            except Exception as e:
                print("ERROR BD:", e)
        return data
    
    def request_process(self, request, subpath: str ) :        
        data_response = {"message" : "No autorizado", "code": 401, "data": None}
        http_code  = 401
        json_data = None

        #logging.info("Reciv " + str(request.method) + " Contex: /ucc/" + str(subpath) )
        #logging.info("Reciv Header :\n" + str(request.headers) )
        #logging.info("Reciv Data: " + str(request.data) )

        rx_api_key = request.headers.get('x-api-key')
        if (rx_api_key == None) or (str(rx_api_key) != str(self.api_key)) :
            return  data_response, http_code
        
        request_data = None 
        request_type = None
        data_rx = None
        if request.data != None and len(request.data) > 0:
            request_data = request.get_json()
            try :
                request_type = request_data['type']
            except Exception as e :
                request_type = None
            try :
                data_rx = request_data['data']
            except Exception as e :
                data_rx = None

        if request_type != None :
            if data_rx != None and str(request_type) == 'encrypted' and request.method == 'POST' :
                data_cipher = str(data_rx)
                #logging.info('Data Encrypt: ' + str(data_cipher) )
                data_clear = self.cipher.aes_decrypt(data_cipher)
                #logging.info('Data EnClaro: ' + str(data_clear) )
                json_data = json.dumps(data_clear)
            else: 
                json_data = data_rx
        else: 
                json_data = data_rx

        logging.info("JSON: " + str(json_data) )

        if request.method == 'POST' :
            if subpath.find('documents/sign') >= 0 :
                document = json_data['document']
                data_response = {
                    "responseCode": 0,
                    "description":"Emulador Jonna Firma Ok",
                    "document": document
                }
                http_code  = 200
            elif subpath.find('document/contract') >= 0 :
                strName = subpath.replace('document/contract/', '')
                strContent = str(json_data['content'])
                strType = str(json_data['contentType'])
                strId = str(json_data['identifier'])
                strDoc = str(json_data['documentId'])
                strRef = str(json_data['referenceId'])
                http_code  = 200
                return render_template( 'contract.html', type=strType, name=strName, content=strContent, id=strId, docId=strDoc, refId=strRef), http_code
            else :
                data_response = {"message" : "Servicio POST /ucc/" + subpath + " no encontrado", "code": 404, "data": None}
                http_code  = 404
        elif request.method == 'GET' :
            if subpath.find('-') >= 0 :
                data = self.get_info(subpath)
                http_code  = 200
                return render_template( 'ucc.html', user=data ), http_code
        else :
            data_response = {"message" : "Servicio GET no encontrado", "code": 404, "data": None}
            http_code  = 404

        return data_response, http_code
