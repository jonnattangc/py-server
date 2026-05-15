from flask import Blueprint, jsonify, request
import logging
import os

logia_bp = Blueprint('logia', __name__)

@logia_bp.route('/logia/<path:subpath>', methods=['POST', 'GET'])
def gran_logia_process(subpath):
    """
    Servicios de Gran Logia: autenticación, grados y documentos
    ---
    tags:
      - Logia
    summary: Gestiona login, validación de acceso, grado masónico y descarga de documentos (requiere x-api-key)
    parameters:
      - in: header
        name: x-api-key
        required: true
        type: string
        description: API key configurada en variable de entorno LOGIA_API_KEY
      - in: path
        name: subpath
        required: true
        type: string
        description: >
          **POST** `usergl/login` — autentica usuario, retorna nombre y grado;
          **POST** `usergl/access` — valida si un usuario tiene acceso a documentos de un grado;
          **POST** `usergl/grade` — retorna el grado de un usuario;
          **POST** `docs/url` — genera URL temporal de descarga de documento PDF;
          **GET** `docs/pdf/<timestamp>/<token>` — descarga el PDF (válido por 1 segundo desde el timestamp).
        example: usergl/login
      - in: body
        name: body
        schema:
          type: object
          description: >
            Todos los campos se envían cifrados en el campo `data` (AES vía JWT).
            El servidor descifra y procesa internamente.
            **login**: `data` cifra `usuario|||contraseña`.
            **access**: `data` cifra `usuario&&grado`.
            **grade**: `data` cifra el nombre de usuario.
            **docs/url**: `data` cifra `nombre_doc;grado;id_qh`.
          required:
            - data
          properties:
            data:
              type: string
              description: Payload cifrado con AES (clave env AES_KEY)
              example: "eyJhbGciOiJIUzI1NiJ9..."
    responses:
      200:
        description: Operación exitosa
        schema:
          type: object
          properties:
            message:
              type: string
              example: Ok
            user:
              type: string
              description: Nombre de usuario (solo `login`)
              example: jonnattan
            grade:
              type: integer
              description: Grado masónico (solo `login` y `grade`)
              example: 3
            name:
              type: string
              description: Nombre completo (solo `login`)
              example: Jonnattan Griffiths
            code:
              type: integer
              description: Código de acceso (solo `access`)
              example: 1
            data:
              type: string
              description: Token cifrado del documento (solo `docs/url`)
              example: "eyJhbGci..."
            url:
              type: string
              description: URL base de descarga (solo `docs/url`)
              example: "https://dev.jonnattan.com/logia/docs/pdf/172345678/"
      401:
        description: API key inválida o ausente
        schema:
          type: object
          properties:
            message:
              type: string
              example: No autorizado
      404:
        description: Subpath no reconocido
        schema:
          type: object
          properties:
            message:
              type: string
              example: "No procesado el contexto: usergl/unknown"
    """
    from app.legacy.granl import GranLogia
    root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    gl = GranLogia(root_dir)
    data, code = gl.request_process(request, subpath)
    del gl
    return data, code
