from flask import Blueprint, jsonify, request
import logging

zlr_bp = Blueprint('zlr', __name__)

@zlr_bp.route('/zlr/<path:subpath>', methods=['GET', 'POST', 'PUT'])
def process_zlr(subpath):
    """
    Proxy hacia la API de Zeleri
    ---
    tags:
      - ZLR (Zeleri)
    summary: Reenvía solicitudes a los servicios de Zeleri (logística) inyectando JWT según la ruta
    parameters:
      - in: path
        name: subpath
        required: true
        type: string
        description: >
          Ruta de la API de Zeleri. Prefijos `integration/` y `production/` son eliminados antes del reenvío.
          El JWT se inyecta automáticamente según el path:
          `rating/` o `Rating/` — usa `coverage_key`;
          `transport-orders/` — usa `ot_key`;
          `georeference/` o `checkout/orders` — usa `geo_key`.
          Si se envía header `Authorization` y no hay key mapeada, se usa el valor recibido.
        example: integration/rating/api/v1.0/rates
      - in: header
        name: Authorization
        type: string
        description: Token JWT pasado por el cliente (se usa si no hay key mapeada en BD)
        example: "Bearer eyJhbGci..."
      - in: body
        name: body
        schema:
          type: object
          description: Payload transparente para la API de Zeleri
          example:
            originCountyCode: "STGO"
            destinationCountyCode: "VALP"
    responses:
      200:
        description: Respuesta exitosa de Zeleri (transparente)
        schema:
          type: object
          description: Estructura definida por Zeleri según el endpoint invocado
      4xx:
        description: Error retornado por Zeleri
        schema:
          type: object
          description: Estructura de error de Zeleri
      500:
        description: Error interno del gateway o fallo de conexión con Zeleri
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
    from app.legacy.irelez import Irelez
    zlr = Irelez()
    data_response, http_code = zlr.request_process(request, str(subpath))
    del zlr
    return data_response, http_code
