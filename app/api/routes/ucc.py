from flask import Blueprint, jsonify, request
import logging

from app.extensions import auth

ucc_bp = Blueprint('ucc', __name__)

@ucc_bp.route('/ucc/<path:subpath>', methods=['GET', 'POST'])
@auth.login_required
def process_ucc(subpath):
    """
    Gestión de usuarios y firma de documentos UCC
    ---
    tags:
      - UCC (Usuarios / Documentos)
    summary: Consulta usuarios por RUT, firma documentos y genera contratos HTML (requiere Basic Auth + x-api-key)
    security:
      - BasicAuth: []
    parameters:
      - in: header
        name: x-api-key
        required: true
        type: string
        description: API key configurada en variable de entorno UCC_API_KEY
      - in: path
        name: subpath
        required: true
        type: string
        description: >
          **GET** `<rut-con-guion>` — renderiza HTML con datos del usuario;
          **POST** `documents/sign` — firma un documento y lo retorna;
          **POST** `document/contract/<nombre>` — renderiza contrato HTML con datos del payload.
        example: documents/sign
      - in: body
        name: body
        schema:
          type: object
          description: >
            Para `documents/sign`:
              `document` (string, requerido).
            Para `document/contract/<nombre>`:
              `content`, `contentType`, `identifier`, `documentId`, `referenceId` (todos string).
          properties:
            document:
              type: string
              example: "base64encodedPDF=="
            content:
              type: string
              example: "<p>Cuerpo del contrato</p>"
            contentType:
              type: string
              example: html
            identifier:
              type: string
              example: USR-001
            documentId:
              type: string
              example: DOC-2026-01
            referenceId:
              type: string
              example: REF-XYZ
    responses:
      200:
        description: Operación exitosa. Para `documents/sign` retorna JSON; para contratos retorna HTML.
        schema:
          type: object
          properties:
            responseCode:
              type: integer
              example: 0
            description:
              type: string
              example: Emulador Jonna Firma Ok
            document:
              type: string
              example: "base64encodedPDF=="
      401:
        description: Credenciales o API key inválidas
        schema:
          type: object
          properties:
            message:
              type: string
              example: No autorizado
            code:
              type: integer
              example: 401
            data:
              type: object
              nullable: true
              example: null
      404:
        description: Subpath no reconocido
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Servicio POST /ucc/unknown no encontrado"
            code:
              type: integer
              example: 404
            data:
              type: object
              nullable: true
              example: null
    """
    from app.legacy.ucc import Ucc
    ucc = Ucc()
    data_response, http_code = ucc.request_process(request, str(subpath))
    del ucc
    return data_response, http_code
