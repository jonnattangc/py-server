# Server para dev.jonnattan.com

Servidor experimental Flask REST API (`dev.jonnattan.com`) que expone servicios para experimentos personales en diversas categorías: AWS, OAuth, WhatsApp via Meta, Atlassian, LLM/ML, geolocalización, correo, criptografía y más.

[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=jonnattangc_py-server)](https://sonarcloud.io/summary/new_code?id=jonnattangc_py-server)
[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-black.svg)](https://sonarcloud.io/summary/new_code?id=jonnattangc_py-server)
![](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2Fjonnattan)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=jonnattangc_py-server&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=jonnattangc_py-server)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=jonnattangc_py-server&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=jonnattangc_py-server)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=jonnattangc_py-server&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=jonnattangc_py-server)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=jonnattangc_py-server&metric=bugs)](https://sonarcloud.io/summary/new_code?id=jonnattangc_py-server)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=jonnattangc_py-server&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=jonnattangc_py-server)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=jonnattangc_py-server&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=jonnattangc_py-server)

---

## Inicio rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Levantar servidor (puerto obligatorio)
python app/http-server.py 8085

# Documentación interactiva Swagger
http://localhost:8085/apidocs/

# Docker (requiere directorio hermano ../envs/ con file.env y file.aws_credentials)
docker-compose up
```

---

## Autenticación

| Mecanismo | Descripción |
|---|---|
| **HTTP Basic Auth** | Usuario/contraseña almacenados en MySQL (tabla `oauth`). Aplica a `/checkall`, `/edr/*`, `/ucc/*`, `/cmkt/*`, `/dreams/*`. |
| **x-api-key** | Header `x-api-key` con clave por variable de entorno. Aplica a `/ucc/*` (`UCC_API_KEY`), `/logia/*` (`LOGIA_API_KEY`). |
| **Sin autenticación** | `/status`, `/infojonna`, `/mail/*`, `/waza/*`, `/cxp/*`, `/zlr/*`, `/page/*`, `/mobile/*`. |

---

## Referencia de la API

### Sistema

#### `GET /status`
Health check del servidor.

**Respuesta 200:**
```json
{ "status": "ok" }
```

---

#### `GET /infojonna`
Información del servidor y su autor.

**Respuesta 200:**
```json
{
  "Servidor": "dev.jonnattan.com",
  "Nombre": "Jonnattan Griffiths Catalan",
  "Linkedin": "https://www.linkedin.com/in/jonnattan/"
}
```

---

#### `GET /checkall` — Basic Auth requerido
Diagnóstico completo: verifica conectividad con MySQL y estado de componentes internos.

**Respuestas:**

| Código | Descripción |
|---|---|
| 200 | Sistema operativo con detalle de componentes |
| 401 | `{ "message": "invalid credentials" }` |

---

### Mail

#### `GET /mail/read`
Lee comprobantes de transferencia Tenpo desde la bandeja **"Bancos"** de Gmail via IMAP.

**Respuesta 200:**
```json
{
  "status": "Ok",
  "transfers": [
    {
      "msg_id": "<CABcXY123@mail.gmail.com>",
      "date": "Thu, 15 May 2026 10:30:00 +0000",
      "from": "no-reply@tenpo.cl",
      "subject": "Comprobante de transferencia - Tenpo",
      "text": "La transferencia de $10.000 fue exitosa. Monto transferencia: $10.000"
    }
  ]
}
```

#### `GET /mail/search`
Stub — responde `{ "status": "Ok search" }` sin datos.

**Errores:**

| Código | Descripción |
|---|---|
| 409 | Acción no reconocida o error interno |

---

### Waza (WhatsApp)

#### `GET /waza` — Verificación de webhook Meta
Verifica la suscripción del webhook de WhatsApp Business.

**Query params:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `hub.mode` | string | Debe ser `subscribe` |
| `hub.challenge` | string | Challenge retornado si la verificación es exitosa |
| `hub.verify_token` | string | Debe coincidir con env `UUID_WZ` |

**Respuestas:**

| Código | Descripción |
|---|---|
| 200 | Retorna el valor de `hub.challenge` |
| 401 | Token incorrecto |

---

#### `POST /waza` — Webhook de eventos WhatsApp
Recibe eventos de WhatsApp Business Account (mensajes de texto, imágenes, estados).

**Body:**
```json
{
  "object": "whatsapp_business_account",
  "entry": [{ "changes": [{ "field": "messages", "value": { ... } }] }]
}
```

**Comportamiento interno:**
- Mensajes de texto: responde via LLM (excepto `/validar` que inicia flujo de validación de identidad).
- Imágenes: avanza el flujo de validación de identidad (CI → rostro → acción → validación).
- Al finalizar la validación: genera y envía OTP por WhatsApp.

**Respuesta 200:**
```json
{ "statusCode": 200, "statusDescription": "Ok" }
```

---

#### `POST /waza/generate`
Genera un OTP y lo envía por WhatsApp usando plantilla `otp_dicode`.

**Body:**
```json
{
  "number_mobile": "56912345678",
  "duration_min": 5,
  "length_otp": 6
}
```

**Respuesta 200:**
```json
{
  "ref": "REF-ABC123",
  "channel": "whatsapp",
  "duration_min": "5"
}
```

**Errores:**

| Código | Descripción |
|---|---|
| 402 | Error al generar o enviar el OTP |

---

#### `POST /waza/validate`
Valida un OTP generado previamente.

**Body:**
```json
{
  "reference": "REF-ABC123",
  "otp": "482910"
}
```

**Respuesta 200:**
```json
{
  "success": true,
  "statusDescription": "OTP válido"
}
```

---

#### `POST /waza/marketing`
Envía mensajes de plantilla de WhatsApp a múltiples destinatarios.

**Body:**
```json
{
  "template": "init_validation",
  "count": 2,
  "clients": [
    { "phone": "56912345678", "name": "Juan Perez", "company": "Mi Empresa" }
  ]
}
```

**Respuesta 200:**
```json
{ "status": "success", "statusDescription": "Mensaje enviado a 2 clientes" }
```

**Errores:**

| Código | Descripción |
|---|---|
| 400 | `{ "status": "error", "statusDescription": "Payload incorrecto" }` |

---

#### `POST /waza/message`
Procesa un mensaje de texto libre via LLM y retorna la respuesta.

**Body:**
```json
{ "mesagge": "¿Cuál es el horario de atención?" }
```

> **Nota:** el campo es `mesagge` (typo heredado del código original).

**Respuesta 200:**
```json
{
  "success": true,
  "result": "Atendemos de lunes a viernes de 9 a 18 horas."
}
```

---

### UCC (Usuarios / Documentos) — Basic Auth + x-api-key requeridos

Header requerido: `x-api-key: <UCC_API_KEY>`

#### `GET /ucc/<rut-con-guion>`
Renderiza página HTML con datos del usuario identificado por RUT.

**Ejemplo:** `GET /ucc/12345678-9`

---

#### `POST /ucc/documents/sign`
Firma un documento y lo retorna.

**Body:**
```json
{ "document": "base64encodedPDF==" }
```

**Respuesta 200:**
```json
{
  "responseCode": 0,
  "description": "Emulador Jonna Firma Ok",
  "document": "base64encodedPDF=="
}
```

---

#### `POST /ucc/document/contract/<nombre>`
Renderiza un contrato HTML con los datos del payload.

**Body:**
```json
{
  "content": "<p>Cuerpo del contrato</p>",
  "contentType": "html",
  "identifier": "USR-001",
  "documentId": "DOC-2026-01",
  "referenceId": "REF-XYZ"
}
```

**Respuesta 200:** HTML renderizado del contrato.

**Errores:**

| Código | Descripción |
|---|---|
| 401 | `{ "message": "No autorizado", "code": 401, "data": null }` |
| 404 | `{ "message": "Servicio POST /ucc/<subpath> no encontrado", "code": 404, "data": null }` |

---

### EDR (Cifrado) — Basic Auth requerido

#### `POST /edr/<subpath>`
Cifra el payload JSON y lo retorna como JWT firmado con HMAC-SHA256 (clave env `AES_KEY`).

**Subpaths especiales:**
- `timeout` — simula latencia de 50 segundos (para pruebas de timeout).

**Body:** cualquier objeto JSON.
```json
{ "user": "jonnattan", "action": "login" }
```

**Respuesta 200:**
```json
{ "jwt": "eyJhbGciOiJIUzI1NiJ9.eyJtZXNzYWdlIjp7Li4ufX0.abc123" }
```

**Errores:**

| Código | Descripción |
|---|---|
| 401 | Credenciales Basic Auth inválidas |
| 500 | Clave AES no configurada o payload inválido |

---

### Crypto / Mercado — Basic Auth requerido

#### `GET /cmkt/bank_dates?id=<id_banco>`
Retorna el rango de fechas para evaluación de depósitos de un banco.

**Respuesta 200:**
```json
{
  "status": "success",
  "deposits": {
    "from_date": "14/05/2026",
    "to_date": "15/05/2026"
  }
}
```

---

#### `POST /cmkt/bank_deposits_update`
Registra nuevos depósitos para una cuenta bancaria y notifica al middleware.

**Body:**
```json
{
  "platform_bank_id": "1",
  "deposits": [
    {
      "origin_bank": "Banco de Chile",
      "origin_account": "123456789",
      "date": "2026-05-15 10:00:00",
      "amount": 50000,
      "origin_name": "Juan Perez",
      "identity": "12345678-9"
    }
  ]
}
```

**Respuesta 200:**
```json
{ "status": "success" }
```

---

#### `GET /cmkt/ping`
Endpoint de prueba de conectividad. Responde `{}`.

---

### Dreams (Notificaciones) — Basic Auth requerido

#### `POST /dreams/deposito`
Notifica un depósito bancario al canal Slack configurado en env `SLACK_NOTIFICATION`.

**Body:**
```json
{
  "amount": "50000",
  "date": "2026-05-15 10:30:00",
  "name": "Juan Perez",
  "identity": "12345678-9",
  "bank": "Banco de Chile",
  "account": "123456789",
  "code": "TRF-20260515-001"
}
```

---

#### `POST /dreams/<cualquier-subpath>`
Envía un mensaje genérico a Slack.

**Body:**
```json
{ "message": "Mensaje a enviar al canal" }
```

**Respuesta:** El código HTTP refleja la respuesta de Slack (200 si exitoso).

---

### CXP (Chilexpress)

Proxy transparente hacia la API de Chilexpress. El API key se inyecta automáticamente desde BD según la ruta.

| Ruta | Key usada | Descripción |
|---|---|---|
| `rating/` o `Rating/` | `coverage_key` | Tarifas (con caché en BD) |
| `transport-orders/` | `ot_key` | Órdenes de transporte |
| `georeference/` | `geo_key` | Georreferencia |
| `agendadigital/` | key hardcodeada | Agenda digital |

#### `GET /cxp/<subpath>`
**Query params opcionales:** `RegionCode`, `type` (cobertura), `fecha` (agenda digital).

#### `POST /cxp/<subpath>`
**Body:** Payload nativo de Chilexpress. Puede ser modificado por `meta_data` almacenado en BD.

#### `PUT /cxp/<subpath>`
Reenvío PUT transparente.

**Errores:**

| Código | Descripción |
|---|---|
| 4xx | Error retornado por Chilexpress (transparente) |
| 500 | `{ "statusCode": 500, "statusDescription": "Error interno Gw" }` |

---

### ZLR (Zeleri)

Proxy hacia la API de Zeleri. Inyecta JWT Bearer según la ruta; si no hay key mapeada, usa el `Authorization` header recibido. Los prefijos `integration/` y `production/` son eliminados antes del reenvío.

| Ruta | Key usada |
|---|---|
| `rating/` o `Rating/` | `coverage_key` |
| `transport-orders/` | `ot_key` |
| `georeference/` o `checkout/orders` | `geo_key` |

#### `GET /zlr/<subpath>`
#### `POST /zlr/<subpath>`
#### `PUT /zlr/<subpath>`

**Errores:**

| Código | Descripción |
|---|---|
| 4xx | Error retornado por Zeleri (transparente) |
| 500 | `{ "statusCode": 500, "statusDescription": "Error interno Gw" }` |

---

### Logia — x-api-key requerido

Header requerido: `x-api-key: <LOGIA_API_KEY>`

Todos los payloads se envían con el campo `data` **cifrado con AES** (env `AES_KEY`). El servidor descifra internamente.

#### `POST /logia/usergl/login`
Autentica un usuario en el sistema de Gran Logia.

`data` cifra: `usuario|||contraseña`

**Respuesta 200:**
```json
{
  "message": "Ok",
  "user": "jonnattan",
  "grade": 3,
  "name": "Jonnattan Griffiths"
}
```

---

#### `POST /logia/usergl/access`
Valida si un usuario tiene acceso a documentos de un grado determinado.

`data` cifra: `usuario&&grado`

**Respuesta 200:**
```json
{ "message": "Acceso autorizado", "code": 1 }
```

---

#### `POST /logia/usergl/grade`
Retorna el grado masónico de un usuario.

`data` cifra: `nombre_usuario`

**Respuesta 200:**
```json
{ "message": "Grado encontrado", "grade": 3 }
```

---

#### `POST /logia/docs/url`
Genera una URL de descarga temporal (válida por 1 segundo) para un documento PDF.

`data` cifra: `nombre_doc;grado;id_qh`

**Respuesta 200:**
```json
{
  "data": "eyJhbGci...",
  "url": "https://dev.jonnattan.com/logia/docs/pdf/172345678/"
}
```

---

#### `GET /logia/docs/pdf/<timestamp>/<token>`
Descarga el PDF. El `timestamp` es un `monotonic_ns`; el link expira al cabo de 1 segundo.

**Respuesta 200:** Archivo PDF.

**Errores:**

| Código | Descripción |
|---|---|
| 401 | API key ausente o inválida |
| 404 | Subpath no reconocido |

---

### Mobile

#### `POST /mobile/sms`
Reenvía una notificación a Slack via servicio externo (`NOTIFICATION_URL`).

**Body:** Objeto JSON libre.

**Respuesta 200:** `{ "code": "OK" }`
**Respuesta 500:** `{ "code": "ERROR" }` — variables de entorno no configuradas.

---

#### `GET/POST /mobile/<subpath>`
Endpoints de simulación para la app móvil.

| Subpath | Método | Comportamiento |
|---|---|---|
| `*validate*` | GET | `{ "nombre": "Jonnattan", "depto": "124", "torre": "A" }` |
| `*door*` | POST | `{ "opened": !state }` (invierte el estado recibido) |
| `*sms*` | POST | `{ "code": "OK" }` |

---

## Variables de entorno

| Variable | Descripción |
|---|---|
| `HOST_BD` | Host MySQL |
| `PORT_BD` | Puerto MySQL (default: 3306) |
| `USER_BD` | Usuario MySQL |
| `PASS_BD` | Contraseña MySQL |
| `SCHEMA_BD` | Schema MySQL |
| `AES_KEY` | Clave AES para cifrado/descifrado JWT |
| `UCC_API_KEY` | API key para servicios UCC |
| `LOGIA_API_KEY` | API key para servicios Gran Logia |
| `LOGIA_BASE_URL` | URL base del sistema de Gran Logia |
| `WAZA_BEARER_TOKEN` | Token Bearer para API de Meta/WhatsApp |
| `PHONE_ID` | ID del teléfono en WhatsApp Business |
| `WAZA_API_VERSION` | Versión de la API de Meta (ej: `v18.0`) |
| `UUID_WZ` | Token de verificación del webhook de WhatsApp |
| `SLACK_NOTIFICATION` | URL del webhook de Slack para notificaciones de depósitos |
| `NOTIFICATION_URL` | URL base del servicio de notificaciones (mobile/sms) |
| `NOTIFICATION_API_KEY` | API key del servicio de notificaciones |
| `BEARER_MIDDLEWARE` | Token Bearer para notificaciones al middleware IONIX |
| `TRANSBOT_ID` | ID del bot de transacciones |

---

## Arquitectura

```
app/
├── api/routes/        # Blueprints Flask (uno por dominio)
├── application/       # Capa de casos de uso (en migración)
├── domain/interfaces/ # Puertos/interfaces abstractas
├── infrastructure/    # Repositorios MySQL, BasicAuth
└── legacy/            # Módulos originales de negocio (aún en uso)
```

La arquitectura es una migración incremental desde un monolito legacy. Los blueprints delegan la lógica a los módulos en `legacy/` mientras la migración progresa hacia la arquitectura de capas.
