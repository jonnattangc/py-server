try:
    import logging
    import sys
    import os
    from flask import jsonify
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)


class Edenred() :
    public_start  = '-----BEGIN PUBLIC KEY-----'
    public_end    = '-----END PUBLIC KEY-----'
    private_start = '-----BEGIN PRIVATE KEY-----'
    private_end   = '-----END PRIVATE KEY-----'
    public_key = None
    private_key = None

    def __init__(self, root='./') :
        # se leen ambos certificados
        try:
            file_path = os.path.join(root, 'static/certificates/public_server.pem')
            logging.info("Archivo Publico: " + file_path )
            with open(file_path) as file:
                self.public_key = file.read()
                file.close()
            if self.public_key != None :
                self.public_key = self.public_key.replace(self.public_start,'')
                self.public_key = self.public_key.replace(self.public_end,'')
                self.public_key = self.public_key.replace('\n','')
            logging.info("Public Key: " + str(self.public_key) )
            file_path = os.path.join(root, 'static/certificates/private_112233445.pem')
            logging.info("Archivo Privado: " + file_path )
            with open(file_path) as file:
                self.private_key = file.read()
                file.close()
            if self.private_key != None :
                self.private_key = self.private_key.replace(self.private_start,'')
                self.private_key = self.private_key.replace(self.private_end,'')
                self.private_key = self.private_key.replace('\n','')
            logging.info("Private Key: " + str(self.private_key) )
        except Exception as e :
            print("ERROR File:", e)

    def cipher(self, payload ) :
        data_cipher = None
        try :
            logging.info("Realizo TEST en Python")
            # aca se debe hacer algo
        except Exception as e:
            print("ERROR Cipher:", e)
        return data_cipher

    def requestProcess(self, request, subpath ) :
            logging.info("Reciv " + str(request.method) + " Contex: /" + str(subpath) )
            # logging.info("Reciv Header : " + str(request.headers) )

            logging.info("Reciv Data: " + str(request.data) )
            data_cipher = self.cipher( str(request.data) )

            data_response = jsonify({'statusCode': 500, 'statusDescription': 'Error interno Gw' })
            errorCode = 500

            if data_cipher != None :
                data_response = data_cipher
                errorCode = 200

            return data_response, errorCode
