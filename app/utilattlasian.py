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

    from atlassian import Jira
    from atlassian import Confluence
    from atlassian import Crowd
    from atlassian import Bitbucket
    from atlassian import ServiceDesk
    from atlassian import Xray


except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
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

    def requestProcess(self, request, subpath ) :
            logging.info('########################## ' + str(request.method) + ' ###################################')
            logging.info("Reciv Header : " + str(request.headers) )
            logging.info("Contex: " + str(subpath) )
            logging.info("Reciv Data: " + str(request.data) )
            # valores por defecto
            data_response = {'statusCode': 500, 'statusDescription': 'Error en la ejecucion del servicio' }
            errorCode = 200
            request_data = request.get_json()
            try :
                m1 = time.monotonic()
                cfnc = self.confluence
                space_name = str(request_data['space'])
                detail = cfnc.get_all_spaces(start=0, limit=500, expand=None)
                pages_info = []

                for page in detail['results'] :
                    if str(page['type']) == 'global' : 
                        if str(page['key']) == space_name :

                            logging.info('Page: ' + str(page['name']) + ' Id: ' +  str(page['id']) + ' Key: ' +  str(page['key'])  )
                            description = cfnc.get_space(str(page['key']), expand='description.plain,homepage')
                            
                            page_id = str(description['homepage']['id'])
                            logging.info('ID Homepage[' + page_id + ']')

                            childs = cfnc.get_page_child_by_type(page_id, type='page', start=None, limit=None, expand=None)
                            
                            logging.info('Child: ' + str(childs) )
                            # properties = cfnc.get_page_properties(page['id'])

                            properties = cfnc.get_page_by_id(page_id, status='current', version=None)
                            logging.info('Title: ' + str(properties['title']) )

                            pages_info.append({
                                'page': page, 
                                'description': description, 
                                'properties': properties
                            })
                
                data_response = {
                    'pages' : pages_info,
                    'len': len(pages_info)
                }

                if subpath == None :
                    logging.info('Sin path adicional')
                else :
                    logging.info('Path adicional:' + str(subpath) )

                diff = time.monotonic() - m1;
                logging.info("Time Response in " + str(diff) + " sec." )
            except Exception as e:
                print("ERROR POST:", e)
            return jsonify(data_response), errorCode
