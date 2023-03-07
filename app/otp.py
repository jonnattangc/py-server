try:
    import logging
    import sys
    import os
    import pymysql.cursors
    import uuid
    from datetime import datetime, timedelta
    import random
    from werkzeug.security import generate_password_hash, check_password_hash

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class Otp() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD','None')
    password = os.environ.get('PASS_BD','None')
    database = 'gral-purpose'
    # caracteristica de la OTP
    # esto puede salir de la configuraci'on de un cliente X cualquiera
    duration_min = 15
    attempts = 1
    length_code = 8

    def __init__(self) :
        try:
            self.db = pymysql.connect(host=self.host,user=self.user,password=self.password,database=self.database,cursorclass=pymysql.cursors.DictCursor)
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def __del__(self):
        if self.db != None:
            self.db.close()

    def connect( self ) :
        try:
            if self.db == None :
                self.db = pymysql.connect(host=self.host,user=self.user,password=self.password,database=self.database,cursorclass=pymysql.cursors.DictCursor)
        except Exception as e :
            print("ERROR BD:", e)
            self.db = None

    def isConnect(self) :
        return self.db != None
    
    def getLengthCode(self) :
        return self.length_code
    
    def getDuration(self) :
        return self.duration_min
    
    def getAttempts(self) :
        return self.attempts

    def getRandomOtp(self) :
        ref = uuid.uuid4()
        otp = int(random.uniform(10000000, 99999999))
        return str(otp) , str(ref)

    def mailOtpValidate( self, channel, otpToValidate ) :
        logging.info("Verifico OTP de Mail u Obtengo Referencia" )
        valid = None
        ref = None
        otp = None 
        otp_expirate = True
        isMail = str(channel).find('@') > 0 and str(channel).find('.') > 0 
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = ''
                if isMail :
                    sql = """select * from Otp where mail = %s and status = %s"""
                else :
                    sql = """select * from Otp where mobile = %s and status = %s"""
                cursor.execute(sql, (str(channel), 'PENDING'))
                results = cursor.fetchall()
                for row in results:
                    otp = str(row['otp']).strip()
                    ref = str(row['ref']).strip()   
                    exp = str(row['expirate_at']).strip()

                date_exp = datetime.strptime(exp,"%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                otp_expirate = now > date_exp
                logging.info("Verifico expiracion: " + str(now.strftime("%Y-%m-%d %H:%M:%S")) + " > " + str(date_exp.strftime("%Y-%m-%d %H:%M:%S")) + " ?? ==>> " +  str(otp_expirate) )

            # Si la OTP se envio por mail, se valida inmediatamente
            if otp != None and ref != None and isMail :
                valid = check_password_hash( otp, str(otpToValidate).strip() ) and not otp_expirate
            
        except Exception as e:
            print("ERROR BD:", e)
        return valid, ref

    def burnOtp(self, ref = '', valid = False , attempt = 1 ) :
        logging.info("Quemo la OTP de Ref " + str(ref))
        try :
            if self.db != None and ref != '':
                status = 'ERROR'
                if valid : status = 'BURN'
                cursor = self.db.cursor()
                now = datetime.now()
                sql = """UPDATE Otp SET status = %s, validate_at = %s, attempt = %s WHERE ref = %s"""
                cursor.execute(sql, (status, now.strftime("%Y-%m-%d %H:%M:%S"), attempt, str(ref) ))
                self.db.commit()
        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()

    def createOtp(self, mobile = '', mail = '') :
        logging.info("Genera nueva instancia de OTP")
        otp = None
        ref = None
        try :
            if self.db != None :
                cursor = self.db.cursor()
                otp, ref = self.getRandomOtp()
                sql = """INSERT INTO Otp (create_at, expirate_at, otp, ref, mail, mobile, status ) VALUES(%s, %s, %s, %s, %s, %s, %s)"""
                now = datetime.now()
                exp = now + timedelta( minutes=self.duration_min ) 
                cursor.execute(sql, (now.strftime("%Y-%m-%d %H:%M:%S"), exp.strftime("%Y-%m-%d %H:%M:%S"), 
                        generate_password_hash(otp), str(ref), str(mail), str(mobile), 'PENDING' ))
                self.db.commit()

        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()
        
        return otp, ref
