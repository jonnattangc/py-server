import logging
import sys
import os

from flask import Flask
from flasgger import Swagger
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import Config
from app.extensions import csrf, auth, cors
from app.api import register_blueprints


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
        "openapi": "3.0.1",
        "info": {
            "title": "API Documentación",
            "description": "Documentación de mi API con modelos compartidos",
            "version": "1.0.0"
        },
        "components": {
            "schemas": {
                "MiModelo": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "nombre": {"type": "string", "example": "Juan Perez"}
                    }
                }
            }
        }
    }

    app.config['SWAGGER'] = {
        'title': 'API Documentación',
        'uiversion': 3,
        'openapi': '3.0.1',
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
        "schemes": ["https"],
        "static_lib_url": "https://unpkg.com/swagger-ui-dist@3/"
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
