from flask import Blueprint, jsonify, request
import logging
import os

waza_bp = Blueprint('waza', __name__)

@waza_bp.route('/waza', methods=['POST', 'GET', 'PUT'])
def wazasp_1():
    """
    Webhook principal de WhatsApp Business (Meta)
    ---
    tags:
      - Waza (WhatsApp)
    summary: Recibe eventos del webhook de WhatsApp o verifica suscripción
    parameters:
      - in: query
        name: hub.mode
        type: string
        description: Modo de verificación Meta (`subscribe`)
      - in: query
        name: hub.challenge
        type: string
        description: Challenge a retornar para verificar el webhook
      - in: query
        name: hub.verify_token
        type: string
        description: Token de verificación (debe coincidir con env UUID_WZ)
      - in: body
        name: body
        schema:
          type: object
          description: Evento entrante de WhatsApp Business Account
          properties:
            object:
              type: string
              example: whatsapp_business_account
            entry:
              type: array
              items:
                type: object
    responses:
      200:
        description: Evento procesado o challenge retornado
        schema:
          type: object
          properties:
            statusCode:
              type: integer
              example: 200
            statusDescription:
              type: string
              example: Ok
      401:
        description: Token de verificación incorrecto
      404:
        description: Método HTTP no disponible
        schema:
          type: object
          properties:
            statusCode:
              type: integer
              example: 404
            statusDescription:
              type: string
              example: Metodo no disponible
      500:
        description: Error interno al procesar el evento
        schema:
          type: object
          properties:
            statusCode:
              type: integer
              example: 500
            statusDescription:
              type: string
              example: Error en la ejecucion del servicio
    """
    return process_waze_msg()

@waza_bp.route('/waza/<path:subpath>', methods=['POST', 'GET', 'PUT'])
def wazasp_2(subpath: str):
    """
    Operaciones de WhatsApp: OTP, marketing y mensajes LLM
    ---
    tags:
      - Waza (WhatsApp)
    summary: Genera OTP, valida OTP, envía campañas de marketing o procesa mensajes con LLM
    parameters:
      - in: path
        name: subpath
        required: true
        type: string
        enum: [generate, validate, marketing, message]
        description: >
          `generate` — genera y envía OTP por WhatsApp;
          `validate` — valida un OTP existente;
          `marketing` — envía mensajes de plantilla a múltiples clientes;
          `message` — procesa un mensaje de texto vía LLM.
      - in: body
        name: body
        required: true
        schema:
          type: object
          description: >
            **generate**: `number_mobile` (string), `duration_min` (int), `length_otp` (int).
            **validate**: `reference` (string), `otp` (string).
            **marketing**: `template` (string), `count` (int), `clients` (array de objetos con `phone`, `name`, `company`).
            **message**: `mesagge` (string, typo intencional en el campo).
          properties:
            number_mobile:
              type: string
              example: "56912345678"
            duration_min:
              type: integer
              example: 5
            length_otp:
              type: integer
              example: 6
            reference:
              type: string
              example: "REF-ABC123"
            otp:
              type: string
              example: "482910"
            template:
              type: string
              example: init_validation
            count:
              type: integer
              example: 2
            clients:
              type: array
              items:
                type: object
                properties:
                  phone:
                    type: string
                    example: "56912345678"
                  name:
                    type: string
                    example: Juan Perez
                  company:
                    type: string
                    example: Mi Empresa
            mesagge:
              type: string
              example: "¿Cuál es el horario de atención?"
    responses:
      200:
        description: Operación exitosa
        schema:
          type: object
          properties:
            ref:
              type: string
              description: Referencia del OTP generado (solo para `generate`)
              example: REF-ABC123
            channel:
              type: string
              description: Canal usado (solo para `generate`)
              example: whatsapp
            duration_min:
              type: string
              description: Duración en minutos (solo para `generate`)
              example: "5"
            success:
              type: boolean
              description: Resultado de la validación (solo para `validate`)
              example: true
            statusDescription:
              type: string
              description: Descripción del resultado
              example: OTP válido
            status:
              type: string
              description: Estado general (solo para `marketing`)
              example: success
            result:
              type: string
              description: Respuesta LLM (solo para `message`)
              example: "Atendemos de lunes a viernes de 9 a 18 horas."
      400:
        description: Payload incorrecto (solo para `marketing`)
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            statusDescription:
              type: string
              example: Payload incorrecto
      402:
        description: Error al generar OTP
        schema:
          type: object
          properties:
            statusCode:
              type: integer
              example: 402
            statusDescription:
              type: string
              example: Error en generacion de OTP
      404:
        description: Subpath no reconocido
        schema:
          type: object
          properties:
            statusCode:
              type: integer
              example: 404
            statusDescription:
              type: string
              example: Servicio no encontrado
    """
    return process_waze_msg(subpath)

def process_waze_msg(subpath: str = None):
    from app.legacy.utilwaza import UtilWaza
    root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    waza = UtilWaza(root_dir)
    msg, code = waza.requestProcess(request, subpath)
    del waza
    return msg, code
