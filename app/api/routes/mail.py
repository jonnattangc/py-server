from flask import Blueprint, jsonify, request
import logging

mail_bp = Blueprint('mail', __name__)

@mail_bp.route('/mail/<path:subpath>', methods=['POST', 'GET'])
def mail_process(subpath):
    """
    Operaciones sobre correo electrónico (IMAP Gmail)
    ---
    tags:
      - Mail
    summary: Lee y procesa correos de transferencias bancarias desde Gmail
    parameters:
      - in: path
        name: subpath
        required: true
        type: string
        enum: [read, search]
        description: >
          Acción a ejecutar:
          `read` — lee comprobantes de transferencia Tenpo desde la bandeja "Bancos";
          `search` — stub, devuelve Ok sin datos.
    responses:
      200:
        description: Operación exitosa
        schema:
          type: object
          properties:
            status:
              type: string
              example: Ok
            transfers:
              type: array
              description: Lista de transferencias encontradas (solo para acción `read`)
              items:
                type: object
                properties:
                  msg_id:
                    type: string
                    example: "<CABcXY123@mail.gmail.com>"
                  date:
                    type: string
                    example: "Thu, 15 May 2026 10:30:00 +0000"
                  from:
                    type: string
                    example: "no-reply@tenpo.cl"
                  subject:
                    type: string
                    example: "Comprobante de transferencia - Tenpo"
                  text:
                    type: string
                    example: "La transferencia de $10.000 fue exitosa. Monto transferencia: $10.000"
      409:
        description: Acción no implementada o error interno
        schema:
          type: object
          properties:
            status:
              type: string
              example: No Implementedo
    """
    from app.legacy.utilmail import MailProcess
    mp = MailProcess()
    data, code = mp.request_process(request, subpath)
    del mp
    return data, code
