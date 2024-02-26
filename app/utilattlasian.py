try:
    import logging
    import sys
    import os
    import time
    import pymysql.cursors
    from datetime import datetime
    from flask import jsonify
    #from atlassian import Jira
    from atlassian import Confluence
    #from atlassian import ServiceDesk

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[UtilAttlasian] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class UtilAttlasian() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD','None')
    password = os.environ.get('PASS_BD','None')
    database = 'gral-purpose'
    environment = None
    jira_api_token = os.environ.get('ATTLASIAN_TOKEN','None')
    attlasian_user = os.environ.get('ATTLASIAN_USER','None')
    attlasian_url = os.environ.get('ATTLASIAN_URL','None')
    confluence = None

    def __init__(self) :
        try:
            self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
            self.confluence = Confluence(  url=self.attlasian_url, username=self.attlasian_user, password=self.jira_api_token, cloud=True)
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None
            self.confluence = None

    def __del__(self):
        if self.db != None:
            self.db.close()
        if self.confluence != None :
            del self.confluence
            self.confluence = None

    def connect( self ) :
        try:
            if self.db == None :
                self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,cursorclass=pymysql.cursors.DictCursor)
                self.confluence = Confluence(  url=self.attlasian_url, username=self.attlasian_user, password=self.jira_api_token, cloud=True)
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None
            self.confluence = None

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

    # Procesa la llamada a cualqueri servicio que tenga que ver con attlasian
    def requestProcess(self, request, subpath ) :
            logging.info('########################## ' + str(request.method) + ' ###################################')
            logging.info("Reciv Header : " + str(request.headers) )
            logging.info("Contex: " + str(subpath) )
            logging.info("Reciv Data: " + str(request.data) )

            # valores por defecto
            response = {'statusCode': 404, 'statusDescription': 'Servicio no exite' }
            errorCode = 404
            request_data = request.get_json()
            m1 = time.monotonic()

            if subpath == None :
                logging.info('Sin path adicional')
            elif subpath.find('info') >= 0 :
                try :
                    name_space = ''
                    key_space = ''
                    title_space = ''
                    description_space = ''
                    id_space = ''

                    cfnc = self.confluence
                    key_space = str(request_data['space'])
                    detail = cfnc.get_all_spaces(start=0, limit=500, expand=None)
                    pages_info = []

                    for page in detail['results'] :
                        if str(page['type']) == 'global' : 
                            if str(page['key']) == key_space :
                                name_space = str(page['name'])
                                id_space = str(page['id'])
                                description = cfnc.get_space(key_space, expand='description.plain,homepage')
                                page_id = str(description['homepage']['id'])
                                logging.info('ID Homepage[' + page_id + ']')
                                description_space = str(description['description']['plain']['value'])
                                logging.info('Descripción Espacio: [' + description_space + ']')

                                properties = cfnc.get_page_by_id(page_id, status='current', version=None)
                                title_space = str(properties['title'])
                                logging.info('Title: ' + title_space )
                                base_url = str(properties['_links']['base'])
                                logging.info('Base URL: ' + base_url )

                                sub_pages = cfnc.get_all_pages_from_space(key_space, start=None, limit=None, status = None, expand = None, content_type = 'page')
                                for sub_page in sub_pages :
                                    pages_info.append({
                                        'title': str(sub_page['title']), 
                                        'id_page': str(sub_page['id']),
                                        'url': str(base_url) + str(sub_page['_links']['webui']) 
                                    })
                    
                    response = {
                            'title': title_space,
                            'name': name_space,
                            'identify': id_space,
                            'key': key_space,
                            'description': description_space,
                            'pages' : pages_info
                    }
                    errorCode = 200
                except Exception as e:
                    print("ERROR POST:", e)
            else :
                logging.info('No hay accion para :' + str(subpath) )

            diff = time.monotonic() - m1;
            logging.info("Time Response in " + str(diff) + " sec." )
            
            return jsonify(response), errorCode
