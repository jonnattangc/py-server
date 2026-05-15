from flask import Blueprint, jsonify, request
import logging

from app.extensions import auth

dreams_bp = Blueprint('dreams', __name__)

@dreams_bp.route('/dreams/<path:subpath>', methods=['GET', 'POST'])
@auth.login_required
def sun_dreams(subpath):
    """
    Notificaciones de depósitos vía Slack
    ---
    tags:
      - Dreams (Notificaciones)
    summary: Recibe notificaciones de depósitos y las reenvía a un canal Slack (requiere Basic Auth)
    security:
      - BasicAuth: []
    parameters:
      - in: path
        name: subpath
        required: true
        type: string
        description: >
          `deposito` — notifica un depósito bancario con detalle;
          cualquier otro valor — reenvía un mensaje genérico a Slack.
        example: deposito
      - in: body
        name: body
        required: true
        schema:
          type: object
          description: Payload varía según subpath
          properties:
            amount:
              type: string
              description: Monto del depósito (requerido para `deposito`)
              example: "50000"
            date:
              type: string
              description: Fecha y hora del depósito
              example: "2026-05-15 10:30:00"
            name:
              type: string
              description: Nombre del originante
              example: Juan Perez
            identity:
              type: string
              description: RUT del originante
              example: "12345678-9"
            bank:
              type: string
              description: Banco de origen
              example: Banco de Chile
            account:
              type: string
              description: Cuenta de origen
              example: "123456789"
            code:
              type: string
              description: Código de transferencia
              example: TRF-20260515-001
            message:
              type: string
              description: Mensaje libre (para subpaths distintos de `deposito`)
              example: "Favor actualizar URL de webhook"
    responses:
      200:
        description: Notificación procesada (Slack puede haber fallado; el código refleja la respuesta de Slack)
        schema:
          type: object
          example: {}
      401:
        description: Credenciales HTTP Basic Auth inválidas
        schema:
          type: object
          properties:
            message:
              type: string
              example: invalid credentials
    """
    from app.legacy.coordinator import Coordinator
    manager = Coordinator()
    data_tx, code_http = manager.proccess_solicitude(request, '/dreams/' + str(subpath))
    del manager
    return jsonify(data_tx), code_http
