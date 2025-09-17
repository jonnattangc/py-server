try:
    import logging
    import sys
    import os
    import json
    import requests
    from utils import Cipher

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[UtilChatbot] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class UtilLlm() :
    x_api_key : str = str(os.environ.get('LLM_API_KEY','None'))
    aes_key : str = str(os.environ.get('LLM_AES_KEY','None')) 
    url : str = str(os.environ.get('LLM_URL','None'))
    name : str = str(os.environ.get('LLM_NAME','None'))
    model : str = str(os.environ.get('LLM_MODEL','None'))
    cipher : Cipher = Cipher(aes_key)

    def sendQuestion(self, question : str ) :
        txt_response = 'No tengo esa respuesta'
        
        data_question = {
            'type': 'clear',
            'data': {
                'prompt': question
            }
        }

        url_question: str = self.url + '/' + str(self.name) + '/' + str(self.model)
        logging.info("URL : " + url_question )

        try :
            headers = {'Content-Type': 'application/json', 'x-api-key': str(self.x_api_key) }
            response = requests.post(url_question, data = json.dumps(data_question), headers = headers, timeout = 20)
            data_response = response.json()
            if response.status_code != None and response.status_code == 200 :
                data_response = response.json()
                logging.info("Response Status Read: " + str( data_response['result'] ) )
                txt_response = str(data_response['result'])
            else:
               logging.error("Response Status Read: " + str(response) ) 
               logging.error("Response Status Data: " + str(response.json()) ) 

        except Exception as e:
            print("ERROR Llamando a API:", e)

        return txt_response
