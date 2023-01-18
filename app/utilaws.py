try:
    import logging
    import sys
    import os
    import time
    import boto3
    import json

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class AwsUtil() :
    url_base = 'https://s3.__AWS_REGION__.amazonaws.com/'

    def __init__(self, region='us-east-2') :
        self.url_base = self.url_base.replace('__AWS_REGION__', region)

    def __del__(self):
        self.url_base = 'https://s3.__AWS_REGION__.amazonaws.com/'

    def getPhotos( self ) :
        elements = []
        m1 = time.monotonic_ns()
        time.sleep(1)
        try :
            s3 = boto3.resource('s3')
            for bucket in s3.buckets.all():
                #logging.info('Bucket: ' + bucket.name)
                #contents = s3.Bucket(bucket.name)
                for obj in bucket.objects.filter(Prefix='photos/') :
                    #logging.info('Bucket: ' + obj.bucket_name + ' Key: ' + obj.key)
                    elements.append({'url' : self.url_base + obj.bucket_name + '/' + obj.key })

        except Exception as e:
            print("ERROR TEST AWS:", e)
            elements = []

        diff = time.monotonic_ns() - m1
        logging.info("AWS S3 Photos Time Response in " + str(diff) + " nsec." )
        return elements 

    def getDocs( self ) :
        elements = []
        m1 = time.monotonic_ns()
        time.sleep(2)
        try :
            s3 = boto3.resource('s3')
            for bucket in s3.buckets.all():
                #logging.info('Bucket: ' + bucket.name)
                #contents = s3.Bucket(bucket.name)
                for obj in bucket.objects.filter(Prefix='docs/') :
                    logging.info('Bucket: ' + obj.bucket_name + ' Key: ' + obj.key)
                    elements.append({'url' : self.url_base + obj.bucket_name + '/' + obj.key })
        except Exception as e:
            print("ERROR TEST AWS:", e)
            elements = []

        diff = time.monotonic_ns() - m1
        logging.info("AWS Time S3 Docs Response in " + str(diff) + " nsec." )
        return elements

    def test_2( self ) :
        message = 'Error de acceso a AWS'
        http_code = 409
        access_key_id = 'AKIAVRN7PMCDDBVYGBXO'
        secret_access_key = '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'

        try :
            session = boto3.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                #region_name='us-east-2'
            )
            s3 = session.resource('s3')
            i = 0
            for bucket in s3.buckets.all():
                logging.info('Bucket: ' + bucket.name)
                i = i + 1 
            message = 'Hay ' + str(i) + ' bucket(s) en AWS'
            http_code = 200

        except Exception as e:
            print("ERROR TEST AWS:", e)

        return message, http_code 