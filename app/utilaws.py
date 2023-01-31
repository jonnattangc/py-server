try:
    import logging
    import sys
    import os
    import time
    import boto3

except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class AwsUtil() :
    url_base = 'https://s3.__AWS_REGION__.amazonaws.com/'

    access_key = os.environ.get('AWS_ACCESS_KEY','None')
    secret_key = os.environ.get('AWS_SECRET_KEY','None')
    session = None

    def __init__(self, region='us-east-2') :
        self.url_base = self.url_base.replace('__AWS_REGION__', region)
        try :
            self.session = boto3.Session(
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    # region_name=region
                )
            logging.info("Session Available Resources: " + str(self.session.get_available_resources()) )
        except Exception as e:
            self.session = None
            print("[__init__] ERROR AWS:", e)
        
    def __del__(self):
        self.url_base = 'https://s3.__AWS_REGION__.amazonaws.com/'

    def getPhotos( self ) :
        elements = []
        m1 = time.monotonic_ns()
        try :
            if self.session != None :
                s3 = self.session.resource('s3')
                logging.info('[Photos] s3: ' + s3 )
                for bucket in s3.buckets.all():
                    logging.info('[Photos] Bucket: ' + bucket.name)
                    #contents = s3.Bucket(bucket.name)
                    for obj in bucket.objects.filter(Prefix='photos/') :
                        logging.info('[Photos] Bucket: ' + obj.bucket_name + ' Key: ' + obj.key)
                        elements.append({'url' : self.url_base + obj.bucket_name + '/' + obj.key })
        except Exception as e:
            print("[Photos] ERROR TEST AWS:", e)
            elements = []

        diff = time.monotonic_ns() - m1
        logging.info("[Photos] AWS Time S3 Photos Response in " + str(diff) + " nsec." )
        return elements 

    def getDocs( self ) :
        elements = []
        m1 = time.monotonic_ns()
        try :
            if self.session != None :
                s3 = self.session.resource('s3')
                logging.info('[Photos] s3: ' + s3 )
                for bucket in s3.buckets.all():
                    logging.info('[Docs] Bucket: ' + bucket.name)
                    #contents = s3.Bucket(bucket.name)
                    for obj in bucket.objects.filter(Prefix='docs/') :
                        logging.info('[Docs] Bucket: ' + obj.bucket_name + ' Key: ' + obj.key)
                        elements.append({'url' : self.url_base + obj.bucket_name + '/' + obj.key })
        except Exception as e:
            print("[Docs] ERROR TEST AWS:", e)
            elements = []

        diff = time.monotonic_ns() - m1
        logging.info("[Docs] AWS Time S3 Docs Response in " + str(diff) + " nsec." )
        return elements
