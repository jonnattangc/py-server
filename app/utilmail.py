try:
    import logging
    import sys
    import os
    import time
    import base64
    import uuid
    import imaplib
    import email

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[AwsUtil] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

ROOT_DIR = os.path.dirname(__file__)

class MailProcess() :
    root = '.'

    def __init__(self, root = str(ROOT_DIR) ) :
        try :
            self.root = str(root)
        except Exception as e:
            print("[__init__] ERROR UtilMail:", e)

    def __del__(self):
        self.root = None

    def request_process(self, request, action ) :
        logging.info("=============================== INIT ===============================" )
        logging.info("Reciv " + str(request.method) + " Acción: " + str(action) )
        logging.info("Reciv Data: " + str(request.data) )
        logging.info("Reciv Header : " + str(request.headers) )
        
        data = {'status':'Error ocurrido'}
        status = 409
        if action != None :   
            if str(action) == 'read' : 
                data = self.read()
                status = 200
            elif str(action) == 'search' :
                data = {'status':'Ok search'}
                status = 200
            else :
                data = {'status':'No Implementedo'}
                status = 409
        logging.info("=============================== END ===============================" )
        return data, status

    def read(self, user = "jonnattan@gmail.com", password = 'gjsd inrp fwok kfcr') :
        data_rx = {
            "status" : "Ok",
            "transfers" : None
        }
        transfers = []
        try:
            # Conexión al servidor IMAP de Gmail
            imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            logging.info("Conectando al servidor IMAP...")

            # Iniciar sesi'on
            imap.login(user, password)
            logging.info("Sesión iniciada con éxito.")

            # Seleccionar la bandeja de entrada (Inbox)
            imap.select("Bancos")
            logging.info("Bandeja de entrada seleccionada.")

            # Buscar todos los correos en la bandeja
            status, messages = imap.search(None, '(FROM "no-reply@tenpo.cl")')
            if str(status) != 'OK':
                logging.error("Error al buscar correos.")
                return data_rx
            # El resultado 'messages' es una lista de IDs de correos
            message_ids = messages[0].split()
            logging.info(f"Total de correos encontrados: {len(message_ids)}")
            # Leer los 5 correos más recientes (los IDs vienen en orden ascendente)
            count = 0
            for msg_id in message_ids[-2000:]:
                status_mail, data = imap.fetch(msg_id, "(RFC822)")
                #logging.info("=============================== [" + str(msg_id) + "] " + str(status_mail) + " ===============================")
                if str(status_mail) != 'OK':
                    logging.error(f"Error al obtener el correo con ID {msg_id}.")
                    continue
                # logging.info("Data:" + str(data))
                raw_email = data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                sender : str = ''
                if email_message["Sender"] != None :
                    sender = str(email_message["Sender"])
                else :
                    sender = sender + ' ' + str(email_message["From"])
                subject : str = ''
                if email_message["Subject"] != None :
                    subject = str(email_message["Subject"])
                
                #logging.info("From: " + str(email_message["From"]))
                if sender.find('no-reply@tenpo.cl') >= 0 and subject.find('Comprobante de transferencia - Tenpo') >= 0 :
                    pos_ini : int = str(email_message).find('>La transferencia de ') + 1
                    pos_end : int = str(email_message).find('fue exitosa') + 11
                    if pos_ini < 0 or pos_end < 0 :
                        continue
                    if pos_end <= pos_ini :
                        continue
                    text : str = str(email_message)[pos_ini:pos_end]
                   
                    pos_ini : int = str(email_message).find('Monto transferencia:')
                    pos_end : int = str(email_message).find('digo de transferencia:') + 35
                    textw : str = str(email_message)[pos_ini:pos_end]
                    
                    text = text + '. ' + textw
                    text = text.replace('\n\n', ',').replace('\n', ',').replace('\t', ' ')
                    text = text.replace(',,', ',').replace(':,', ': ')
                    text = text.replace('N=C2=BA', 'Número').replace(',', ', ').replace('C=C3=B3', 'Có')
                    #logging.info('[' + str(text) + ']')
                    if text != None :
                        count = count + 1
                        logging.info("Count: " + str(count) )
                        transfers.append( {
                            "msg_id" : str(email_message["Message-ID"]),
                            "date" : str(email_message["Date"]),
                            "from" : str(sender),
                            "subject" : str(subject),
                            "text" : text
                        } )
            # Cerrar la conexión
            imap.close()
            imap.logout()
            logging.info("Conexión cerrada. Count: " + str(count) )
        except Exception as e:
            logging.error("Ocurrió un error", e)
            transfers = []
            data_rx['status'] = "Error: " + str(e)
        data_rx['transfers'] = transfers
        return data_rx
