try:
    import logging
    import sys
    import os
    import json
    import requests
    from flask import request, jsonify

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[UtilChatbot] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class UtilGeo() :
    x_api_key : str = str(os.environ.get('GEO_API_KEY','None'))
    url : str = str(os.environ.get('GEO_API_URL','None'))
    def send_request(self, request, path: str ) :
        http_code : int = 401
        data_response : dict = None
        payload : dict = None
        if request.data != None and len(request.data) > 0:
            payload = request.get_json()
            logging.info(f"Payload : {payload}")
        url_request : str = f"{self.url}{path}"
        try :
            headers = {
                'Content-Type': 'application/json', 
                'x-api-key': str(self.x_api_key),
                'Accept': 'application/json'
            }

            if request.method == 'GET' :
                response = requests.get(url_request, headers = headers, timeout = 20)
                data_response = response.json()
                http_code = response.status_code
            elif request.method == 'POST' :
                response = requests.post(url_request, data = json.dumps(payload), headers = headers, timeout = 20)
                data_response = response.json()
                http_code = response.status_code
            elif request.method == 'PUT' :
                response = requests.put(url_request, data = json.dumps(payload), headers = headers, timeout = 20)
                data_response = response.json()
                http_code = response.status_code
            else :
                logging.error(f"Metodo no soportado : {method}") 
        except Exception as e:
            print("ERROR Llamando a API Geo", e)
        logging.info(f"Response : {data_response}")
        return data_response, http_code
