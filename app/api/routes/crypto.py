from flask import Blueprint, jsonify, request
import logging

from app.extensions import auth

crypto_bp = Blueprint('crypto', __name__)

@crypto_bp.route('/cmkt/<path:subpath>', methods=['GET', 'POST'])
@auth.login_required
def crypto_mrk(subpath):
    """
    Coordinador de crypto/mercado con soporte de depósitos bancarios
    ---
    tags:
      - Crypto / Mercado
    summary: Procesa consultas de fechas bancarias y actualizaciones de depósitos (requiere Basic Auth)
    security:
      - BasicAuth: []
    parameters:
      - in: path
        name: subpath
        required: true
        type: string
        description: >
          Rutas disponibles:
          `bank_dates` — retorna rango de fechas para evaluación bancaria (query param `id`);
          `bank_deposits_update` — registra nuevos depósitos para una cuenta;
          `ping` — responde vacío.
        example: bank_dates
      - in: query
        name: id
        type: string
        description: ID interno del banco (requerido para `bank_dates`)
        example: "1"
      - in: body
        name: body
        schema:
          type: object
          description: Requerido para `bank_deposits_update`
          properties:
            platform_bank_id:
              type: string
              example: "1"
            deposits:
              type: array
              items:
                type: object
                properties:
                  origin_bank:
                    type: string
                    example: Banco de Chile
                  origin_account:
                    type: string
                    example: "123456789"
                  date:
                    type: string
                    example: "2026-05-15 10:00:00"
                  amount:
                    type: number
                    example: 50000
                  origin_name:
                    type: string
                    example: Juan Perez
                  identity:
                    type: string
                    example: "12345678-9"
    responses:
      200:
        description: Operación exitosa
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            deposits:
              type: object
              description: Presente solo en `bank_dates`
              properties:
                from_date:
                  type: string
                  example: "14/05/2026"
                to_date:
                  type: string
                  example: "15/05/2026"
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
    data_tx, code_http = manager.proccess_solicitude(request, str(subpath))
    del manager
    return jsonify(data_tx), code_http
