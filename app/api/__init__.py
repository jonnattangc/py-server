from flask import Blueprint
from app.extensions import csrf

from app.api.routes.main import main_bp
from app.api.routes.check import check_bp
from app.api.routes.edr import edr_bp
from app.api.routes.crypto import crypto_bp
from app.api.routes.dreams import dreams_bp
from app.api.routes.ucc import ucc_bp
from app.api.routes.waza import waza_bp
from app.api.routes.logia import logia_bp
from app.api.routes.mail import mail_bp
from app.api.routes.page import page_bp
from app.api.routes.cxp import cxp_bp
from app.api.routes.status import status_bp
from app.api.routes.zlr import zlr_bp


def register_blueprints(app):
    """Register Flask blueprints and exempt CSRF where appropriate."""
    bps = [
        (main_bp, ''),
        (check_bp, ''),
        (edr_bp, ''),
        (crypto_bp, ''),
        (dreams_bp, ''),
        (ucc_bp, ''),
        (waza_bp, ''),
        (logia_bp, ''),
        (mail_bp, ''),
        (page_bp, ''),
        (cxp_bp, ''),
        (status_bp, ''),
        (zlr_bp, ''),
    ]
    for bp, url_prefix in bps:
        app.register_blueprint(bp, url_prefix=url_prefix)
        # Exempt CSRF for all routes in these blueprints (matches legacy behaviour)
        for view_name in bp.view_functions:
            csrf.exempt(bp.view_functions[view_name])
