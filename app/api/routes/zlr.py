from flask import Blueprint, jsonify, request
import logging

zlr_bp = Blueprint('zlr', __name__)

@zlr_bp.route('/zlr/<path:subpath>', methods=['GET', 'POST', 'PUT'])
def process_zlr(subpath):
    """
    Proxy hacia la API de ZLR
    ---
    tags:
      - ZLR
    summary: Reenvía solicitudes a los servicios de proveedor de logística ZLR (logística) inyectando JWT según la ruta
    parameters:
      - in: path
        name: subpath
        required: true
        type: string
        description: >
          Ruta de la API de proveedor de logística ZLR. Prefijos `integration/` y `production/` son eliminados antes del reenvío.
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
          description: Payload transparente para la API de proveedor de logística ZLR
          example:
            originCountyCode: "STGO"
            destinationCountyCode: "VALP"
    responses:
      200:
        description: Respuesta exitosa de proveedor de logística ZLR (transparente)
        schema:
          type: object
          description: Estructura definida por proveedor de logística ZLR según el endpoint invocado
      4xx:
        description: Error retornado por proveedor de logística ZLR
        schema:
          type: object
          description: Estructura de error de proveedor de logística ZLR
      500:
        description: Error interno del gateway o fallo de conexión con proveedor de logística ZLR
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
    return jsonify(data_response), http_code
