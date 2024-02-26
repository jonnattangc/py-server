try:
    import logging
    import sys
    import os
    import time
    import requests
    import geopandas as gpd
    from shapely.geometry import Point
except ImportError:
    logging.error(ImportError)
    print((os.linesep * 2).join(['[GeoPosUtil] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

class GeoPosUtil() :
    file_name = None
    map = None
    # ==============================================================================
    # Constructor
    # ==============================================================================
    def __init__(self, root = '.', name = 'Sudamérica.shp') :
        try :
            file_path = os.path.join(root, 'static')
            file_path = os.path.join(file_path, 'shapes')
            self.file_name = file_path + '/' + str(name)
            logging.info('GeoPos Test, Carga: ' + str(self.file_name))
            self.map = gpd.read_file(str(self.file_name))
        except Exception as e:
            print("[GeoPosUtil] ERROR GEO:", e)

    # ==============================================================================
    # Destructor
    # ==============================================================================
    def __del__(self):
        self.file_name = None
        self.map = None

    # ==============================================================================
    # Metodo que pregunta si un punto est'a dentro de un pa'is
    # por una posici'on dentro del mapa
    # ==============================================================================
    def pointInside(self, request ) :
        code = 409
        data = {}
        try :
            request_data = request.get_json()
            lat = float(request_data['latitude'])
            lon = float(request_data['longitude'])
            country = str(request_data['country'])
            point = Point(lon,lat)
            if self.inside(point, country) : 
                code = 200
                data = {'inside': True}
            else :
                code = 200 
                data = {'inside': False}
        except Exception as e:
            print("ERROR GeoPosUtil:", e)
        return data, code
    

    # ==============================================================================
    # Busca si un punto geografico pertenece a un Shape
    # ==============================================================================
    def inside(self, point, country ) :
        inside = False
        coordenadas = None
        try :
            length = len(self.map.head())
            i = 0
            while i < length : 
                pais, coordenadas = self.map.iloc[i]
                if pais == country : 
                    break
                i += 1
            if coordenadas != None :
                inside = point.within( coordenadas )
            
        except Exception as e:
            print("ERROR GeoPosUtil:", e)
        return inside
    # ==============================================================================
    # Busca la cordenada de una direcci'on en Chile
    # ==============================================================================
    def searchAddress(self, request ) :
        code = 409
        data = {}
        try :
            request_data = request.get_json()
            address = str(request_data['address'])
            address = address.replace('pob', 'población')
            address = address.replace('depto', 'departamento')
            address = address.replace('block', 'edificio')
            address = address.replace('.', ' ')
            address = address.replace('  ', ' ')
            address = address.replace(' ', '+')
            logging.info("data_cipher: " + address )
            url = 'https://nominatim.openstreetmap.org/search?q=' + address
            #url += '&country=Chile'
            url += '&format=jsonv2'
            #url += '&polygon_geojson=1'
            #url += '&addressdetails=1'
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json' }
            m1 = time.monotonic_ns()
            logging.info("URL : " + url )
            resp = requests.get(url, headers = headers, timeout = 40)
            diff = time.monotonic_ns() - m1
            if( resp.status_code == 200 ) :
                data_response = resp.json()
                logging.info("Response: " + str( data_response ) )
                data = {
                    'latitude'  : str( data_response[0]['lat'] ),
                    'longitude' : str( data_response[0]['lon'] ),
                    'name'      : str( data_response[0]['display_name'] ),
                    'message'   : 'Servicio Ejecutado Existosamente'
                }  
                code = 200
            else :
                data_response = resp.json()
                logging.info("Response: " + str( data_response ) )

            logging.info("Time Response in " + str(diff/1000000000.0) + " sec." )

        except Exception as e:
            print("ERROR POST:", e)
        return data, code

    # ==============================================================================
    # Procesa todos los request 
    # ==============================================================================
    def requestProcess(self, request, subpath ) :
        logging.info("############################ Geo Util ##############################" )
        logging.info("Reciv " + str(request.method) + " Subpath: " + str(subpath) )
        logging.info("Reciv Data: " + str(request.data) )
        logging.info("Reciv Header : " + str(request.headers) )
        m1 = time.monotonic()
        try :
            if subpath == 'search' : 
                return self.searchAddress( request )
            elif subpath == 'inside' :
                return self.pointInside( request )
        except Exception as e:
            print("[GeoPosUtil] Error requestProcess:", e)
        diff = time.monotonic() - m1
        logging.info("[GeoPosUtil] Servicio Ejecutado en " + str(diff) + " msec." )
        return {}, 200 