try:
    import logging
    import sys
    import os
    import time
    from flask import jsonify
    from jose import jwt

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[dernede] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class Dernede() :
    public_start  = '-----BEGIN PUBLIC KEY-----'
    public_end    = '-----END PUBLIC KEY-----'
    private_start = '-----BEGIN PRIVATE KEY-----'
    private_end   = '-----END PRIVATE KEY-----'
    public_key = None
    private_key = None
    aes_key = os.environ.get('AES_KEY','None')

    def __init__(self, root='./') :
        # se leen ambos certificados
        try:
            file_path = os.path.join(root, 'static/certificates/public_server.pem')
            #logging.info("Archivo Publico: " + file_path )
            with open(file_path) as file:
                self.public_key = file.read()
                file.close()
            if self.public_key != None :
                self.public_key = self.public_key.replace(self.public_start,'')
                self.public_key = self.public_key.replace(self.public_end,'')
                self.public_key = self.public_key.replace('\n','')
            #logging.info("Public Key: " + str(self.public_key) )
            file_path = os.path.join(root, 'static/certificates/private_112233445.pem')
            #logging.info("Archivo Privado: " + file_path )
            with open(file_path) as file:
                self.private_key = file.read()
                file.close()
            if self.private_key != None :
                self.private_key = self.private_key.replace(self.private_start,'')
                self.private_key = self.private_key.replace(self.private_end,'')
                self.private_key = self.private_key.replace('\n','')
            #logging.info("Private Key: " + str(self.private_key) )
        except Exception as e :
            print("ERROR File:", e)

    def aes_encrypt(self, data ) :
        data_cipher = None
        try :
            key = self.aes_key.encode('utf-8')[:32]
            protected = {'alg': 'HS256'}
            payload = {'message': data }
            data_cipher = jwt.encode(payload, key, algorithm=protected['alg'])
        except Exception as e:
            print("ERROR Cipher:", e)
            data_cipher = None
        return data_cipher

    def aes_decrypt(self, message ) :
        data_clear = None
        try :
            key = self.aes_key.encode('utf-8')[:32]
            protected = {'alg': 'HS256'}
            data_clear = jwt.decode(str(message), key, algorithms=[protected['alg']])
        except Exception as e:
            print("ERROR Decipher:", e)
            data_clear = None
        return data_clear

    def requestProcess(self, request, subpath ) :
            data_response = jsonify({'statusCode': 500, 'statusDescription': 'Error interno Gw' })
            errorCode = 500
            logging.info("Reciv " + str(request.method) + " Contex: /" + str(subpath) )
            logging.info("Reciv Data: " + str( request.get_json()) )
            if str(subpath).find('timeout') >= 0 : 
                time.sleep(50)
                data_response = jsonify({'statusCode': 200, 'statusDescription': 'OK' }) 
                errorCode = 200    
            else :
                logging.info("Cifro...")
                data_cipher = self.aes_encrypt( request.get_json() )
                if data_cipher != None :
                    logging.info("Encrypt Ok")
                    data_clear = self.aes_decrypt(data_cipher)
                    if data_clear != None :
                        logging.info("Decript Ok: " + str(data_clear))

                if data_cipher != None:
                    data_response = jsonify({'jwt' : data_cipher})
                    errorCode = 200

            return data_response, errorCode
