from flask import Blueprint, jsonify, request
import logging

cxp_bp = Blueprint('cxp', __name__)

@cxp_bp.route('/cxp/<path:subpath>', methods=['GET', 'POST', 'PUT'])
def process_cxp(subpath):
    """
    Proxy hacia la API de CXP
    ---
    tags:
      - CXP
    summary: Reenvía solicitudes a los servicios de proveedor de logística CXP (cobertura, órdenes, georreferencia, agenda digital)
    parameters:
      - in: path
        name: subpath
        required: true
        type: string
        description: >
          Ruta original de la API de proveedor de logística CXP. Ejemplos:
          `rating/api/v1.0/rates/business` — tarifas (con caché habilitado en BD);
          `transport-orders/api/v1.0/...` — órdenes de transporte;
          `georeference/api/v1.0/...` — georreferencia;
          `agendadigital/...` — agenda digital (usa key hardcoded).
        example: rating/api/v1.0/rates/business
      - in: query
        name: RegionCode
        type: string
        description: Código de región (solo para GET en rutas de cobertura/georreferencia)
        example: "13"
      - in: query
        name: type
        type: string
        description: Tipo de cobertura (solo para GET)
        example: "1"
      - in: query
        name: fecha
        type: string
        description: Fecha para agenda digital (solo para GET agendadigital)
        example: "2026-05-15"
      - in: body
        name: body
        schema:
          type: object
          description: Payload que se reenvía sin modificación a proveedor de logística CXP (para POST/PUT). Puede ser modificado por `meta_data` almacenado en BD.
          example:
            ServiceDeliveryId: "3"
            OriginCountyCode: "STGO"
            DestinationCountyCode: "VALP"
    responses:
      200:
        description: Respuesta exitosa de proveedor de logística CXP (transparente)
        schema:
          type: object
          description: Estructura definida por proveedor de logística CXP según el endpoint invocado
      4xx:
        description: Error retornado por proveedor de logística CXP
        schema:
          type: object
          description: Estructura de error de proveedor de logística CXP
      500:
        description: Error interno del gateway o fallo de conexión con proveedor de logística CXP
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
    from app.legacy.sserpxelihc import Sserpxelihc
    cxp = Sserpxelihc()
    data_response, http_code = cxp.requestProcess(request, str(subpath))
    del cxp
    return data_response, http_code
