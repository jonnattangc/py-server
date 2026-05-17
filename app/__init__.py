#!/usr/bin/python
try:
    import logging
    import sys
    import os

    from flask import Flask
    from flasgger import Swagger
    from werkzeug.middleware.proxy_fix import ProxyFix

    from app.config import Config
    from app.extensions import csrf, auth, cors
    from app.api import register_blueprints

except ImportError:

    logging.error(ImportError)
    print((os.linesep * 2).join(['[_INIT_] Error al buscar los modulos:', str(sys.exc_info()[1]), 'Debes Instalarlos para continuar', 'Deteniendo...']))
    sys.exit(-2)

def configure_logging():
    fmt = '%(asctime)s %(levelname)s : %(message)s'
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    root.addHandler(handler)


def create_app(template_dir=None, static_dir=None) -> Flask:
    configure_logging()

    app = Flask(
        __name__,
        template_folder=template_dir or Config.TEMPLATE_DIR,
        static_folder=static_dir or Config.STATIC_DIR,
    )

    app.config.from_object(Config)
    app.config.update(DEBUG=False, SECRET_KEY=str(Config.SECRET_KEY))
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

    # Swagger / Flasgger config
    template = {
        "swagger": "2.0",
        "info": {
            "title": "api.jonna.cl — API",
            "description": (
                "API personal experimental con integraciones a otros servicios."
            ),
            "version": "1.0.0",
            "contact": {
                "name": "Jonnattan Griffiths",
                "url": "https://www.jonna.cl"
            }
        },
        "host": "api.jonna.cl",
        "basePath": "/",
        "schemes": ["https"],
        "securityDefinitions": {
            "BasicAuth": {
                "type": "basic",
                "description": "HTTP Basic Auth. Usuario y contraseña almacenados en MySQL (tabla oauth)."
            },
            "ApiKeyHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "x-api-key",
                "description": "API key enviada en el header x-api-key."
            }
        },
        "tags": [
            {"name": "Sistema", "description": "Health checks e información del servidor"},
            {"name": "Mail", "description": "Lectura de correos bancarios via IMAP"},
            {"name": "Waza (WhatsApp)", "description": "Webhook y operaciones de WhatsApp Business via Meta"},
            {"name": "UCC (Usuarios / Documentos)", "description": "Gestión de usuarios y firma de documentos"},
            {"name": "EDR (Cifrado)", "description": "Cifrado/descifrado JWT con clave AES"},
            {"name": "Crypto / Mercado", "description": "Coordinador de depósitos bancarios y crypto"},
            {"name": "Dreams (Notificaciones)", "description": "Notificaciones de depósitos vía Slack"},
            {"name": "CXP", "description": "Proxy hacia la API de logística CXP"},
            {"name": "ZLR", "description": "Proxy hacia la API de logística ZLR"},
            {"name": "Logia", "description": "Servicios de Gran Logia: login, grados y documentos"},
            {"name": "Mobile", "description": "Endpoints para aplicación móvil"},
        ]
    }

    app.config['SWAGGER'] = {
        'title': 'api.jonnattan.cl — API',
        'uiversion': 3,
        'specs_route': '/apidocs/',
        'doc_dir': os.path.join(Config.BASE_DIR, 'docs'),
        'static_url_path': '/flasgger_static',
        'specs': [
            {
                "endpoint": 'apijonna',
                "route": '/apijonna.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "headers": [],
    }

    # Initialize extensions
    csrf.init_app(app)
    cors.init_app(
        app,
        origins=[
            "http://192.168.1.10:3000",
            "https://dev.jonnattan.com",
            "https://api.jonnattan.cl",
            "https://www.jonna.cl",
            "https://www.jonnattan.cl",
            "https://api.jonna.cl",
            "https://docs.jonna.cl",
            "https://docs.jonnattan.cl",
        ]
    )

    Swagger(app, template=template)

    # Register blueprints
    register_blueprints(app)

    return app
