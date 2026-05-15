from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_httpauth import HTTPBasicAuth

# Extensiones Flask (sin inicializar app todavía)
csrf = CSRFProtect()
auth = HTTPBasicAuth()
cors = CORS()
