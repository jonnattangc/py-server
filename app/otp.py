#!/usr/bin/python

try:
    import logging
    import sys
    import os
    import pymysql.cursors
    import uuid
    import math
    from datetime import datetime, timedelta
    import random
    from werkzeug.security import generate_password_hash, check_password_hash

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[Otp] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class Otp() :
    db = None
    host = os.environ.get('HOST_BD','None')
    user = os.environ.get('USER_BD','None')
    password = os.environ.get('PASS_BD','None')
    database = 'gral-purpose'
    duration_min = 10
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

    def getRandomOtp(self, len ) :
        izq = math.pow(10, len - 1)
        der = math.pow(10, len) - 1
        otp = int(random.uniform(izq, der))
        ref = uuid.uuid4()
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
                cursor.close()
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

    def validateOtp( self, reference, otpToValidate ) :
        logging.info("Verifico OTP" )
        valid = False
        otp_saved = None
        otp_state = None
        otp_expirate = True
        reason = 'OTP Completamente valida'
        try :
            if self.db != None :
                cursor = self.db.cursor()
                sql = """select * from Otp where ref = %s"""
                cursor.execute(sql, (str(reference)))
                results = cursor.fetchall()
                for row in results:
                    otp_saved = str(row['otp']).strip()
                    otp_state = str(row['status']).strip()
                    exp = str(row['expirate_at']).strip()
                date_exp = datetime.strptime(exp,"%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                otp_expirate = now > date_exp
                logging.info("Verifico expiracion: " + str(now.strftime("%Y-%m-%d %H:%M:%S")) + " > " + str(date_exp.strftime("%Y-%m-%d %H:%M:%S")) + " ?? ==>> " +  str(otp_expirate) )
                logging.info("Status OTP: " +  otp_state )
            if otp_saved != None :
                valid = check_password_hash( otp_saved, str(otpToValidate).strip() )
                if valid == True :
                    if otp_expirate == True : 
                        reason = 'La otp está expirada, no se puede validar'
                        valid = False
                    if otp_state == 'PENDING' : 
                        self.burnOtp( reference, valid )
                    else :
                        reason = 'La otp ya fue validada anteriormente'
                        valid = False
                else :
                    reason = 'La otp no coincide con la enviada al móvil'
        except Exception as e:
            print("ERROR BD:", e)
        return valid, reason


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

    def createOtp(self, mobile = '', mail = '', whatsapp = '', duration_min = 0, len = 6 ) :
        logging.info("Genera nueva instancia de OTP")
        otp = None
        ref = None
        try :
            if self.db != None :
                cursor = self.db.cursor()
                otp, ref = self.getRandomOtp( len )
                sql = """INSERT INTO Otp (create_at, expirate_at, otp, ref, mail, mobile, status, channel ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
                now = datetime.now()

                channel = 'mail'
                if mobile != '' : channel = 'sms'
                if whatsapp != '' : channel = 'whatsapp'

                if duration_min == 0 :
                    duration_min = self.duration_min

                exp = now + timedelta( minutes=duration_min )
                cursor.execute(sql, (now.strftime("%Y-%m-%d %H:%M:%S"), exp.strftime("%Y-%m-%d %H:%M:%S"), generate_password_hash(otp), str(ref), str(mail), str(mobile), 'PENDING', str(channel) ))
                self.db.commit()

        except Exception as e:
            print("ERROR BD:", e)
            self.db.rollback()

        return otp, ref
