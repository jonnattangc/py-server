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

    def send_question(self, question : str, father_name : str = None, son_name : str = None, parent_name : str = None ) -> str :

        txt_response = 'No tengo esa respuesta, intentalo más tarde por favor'
        logging.info(f"##################### Question: {question} hecha por Father: {father_name}, Son: {son_name}, Parent: {parent_name}")
        context : str = 'chat'
        if (father_name != None) and (son_name != None and parent_name != None) :
            context = f"Eres el Tesorero del curso tercero básico del Colegio Saint Peter's, el curso tiene 40 alumno. \
            Utilizas el archivo excel para mantener actualizada la información de tesorería.  \
            Los nombres de los 40 alumnos están en la Hoja llamada Cuotas, en la comlumna A desde la fila 2 a la 41. \
            Las columnas B a la K representan los 10 meses que se deben pagar las cuotas, de Marzo a Diciembre. \
            Cada celda corresponde al pago del mes para el alumno de la fila. La Columna M es el resumen de los 10 meses para cada alumno. \
            Cada celda vacia significa mes no pagado para el alumno. La otra Hoja llamada \"Otros Pagos\" corresponde a pagos adicionales, donde cada columna de la fila 2 indica el concepto \
            y las las filas de la 3 a la 42 son los 40 alumnos, la fila 43 es el total pagado del items, cada columna corresponde a un items distinto. \
            Quien pregunta es {parent_name} de {son_name} llamado {father_name}. \
            Responde con un tono divertido y preciso agregado un poco de humor."

        data_question = {
            'type': 'clear',
            'data': {
                'prompt': 'respondeme en español el siguiente mensaje: ' + question,
                'assistantType': context
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
