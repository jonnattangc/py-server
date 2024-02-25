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


class UtilChatbot() :
    x_api_key = os.environ.get('CHATBOT_API_KEY','None')
    doc = os.environ.get('FILE_CHAT_KEY','None')

    def sendQuestion(self, question ) :
        txt_response = 'No tengo esa respuesta'
        data_question = {
            'sourceId' : str(self.doc),
            'messages' : [{
                'role'  : 'assistant',
                'content'  : str(question)
            }]
        }
        url = 'https://api.chatpdf.com/v1/chats/message'
        logging.info("URL : " + url )

        try :
            headers = {'Content-Type': 'application/json', 'x-api-key': str(self.x_api_key) }
            response = requests.post(url, data = json.dumps(data_question), headers = headers, timeout = 40)
            data_response = response.json()
            if response.status_code != None and response.status_code == 200 :
                data_response = response.json()
                logging.info("Response Status Read: " + str( data_response['content'] ) )
                txt_response = data_response['content']
            else:
               logging.error("Response Status Read: " + str(response) ) 

        except Exception as e:
            print("ERROR Llamando a API:", e)

        return txt_response
