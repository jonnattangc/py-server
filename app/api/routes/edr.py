from flask import Blueprint, jsonify, request
import logging

from app.extensions import auth

edr_bp = Blueprint('edr', __name__)

@edr_bp.route('/edr/<path:subpath>', methods=['GET', 'POST'])
@auth.login_required
def dernede_process(subpath):
    """
    Servicio de cifrado/descifrado JWT con clave AES
    ---
    tags:
      - EDR (Cifrado)
    summary: Cifra un payload JSON y lo retorna como JWT firmado con HMAC-SHA256
    security:
      - BasicAuth: []
    parameters:
      - in: path
        name: subpath
        required: true
        type: string
        description: >
          Cualquier ruta activa el cifrado. Usa `timeout` para simular latencia de 50 segundos.
        example: encrypt
      - in: body
        name: body
        required: true
        schema:
          type: object
          description: Cualquier objeto JSON a cifrar
          example:
            user: "jonnattan"
            action: "login"
    responses:
      200:
        description: Payload cifrado como JWT
        schema:
          type: object
          properties:
            jwt:
              type: string
              description: Token JWT firmado con la clave AES (env AES_KEY)
              example: eyJhbGciOiJIUzI1NiJ9.eyJtZXNzYWdlIjp7InVzZXIiOiJqb25uYXR0YW4ifX0.abc123
      401:
        description: Credenciales HTTP Basic Auth inválidas
        schema:
          type: object
          properties:
            message:
              type: string
              example: invalid credentials
      500:
        description: Error interno al cifrar (clave AES no configurada o payload inválido)
        schema:
          type: object
          properties:
            statusCode:
              type: integer
              example: 500
            statusDescription:
              type: string
              example: Error interno Gw
    """
    from app.legacy.dernede import Dernede
    import os
    root_dir = os.path.dirname(os.path.abspath(__file__))
    edr = Dernede(root_dir)
    data_tx, error = edr.requestProcess(request, subpath)
    del edr
    return data_tx, error
