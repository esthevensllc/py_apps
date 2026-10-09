# WhatsApp mediante Aivo

Proceso ejecutable desde la raíz del repositorio para enviar una plantilla por
invocación. Primero realiza `POST https://gateway.aivo.co/api/v1/auth` con
`user` y `password`. Después realiza
`POST https://gateway.aivo.co/api/v1/conversation-whatsapp-native-templates`
con `Authorization: Bearer <token>` y `X-Token`.

## Instalación y credenciales

```powershell
python -m pip install -r src/aivo_whatsapp/requirements.txt
Copy-Item src/aivo_whatsapp/.env.example src/aivo_whatsapp/.env
```

En Linux, usar `cp` para copiar el archivo. Completar `AIVO_USER`,
`AIVO_PASSWORD` y `AIVO_X_TOKEN` en `src/aivo_whatsapp/.env`, ignorado por Git.
Este proyecto tiene configuración propia; no carga el `.env` raíz por defecto.
Las variables existentes del entorno tienen prioridad. Puede seleccionarse otro
archivo con `--env-file ruta/al/.env`.

Configurar también los proxies corporativos en ese archivo:

```dotenv
AIVO_HTTP_PROXY=http://claro-proxy
AIVO_HTTPS_PROXY=http://claro-proxy
```

Ambos POST usan estos proxies. Como los endpoints de Aivo son HTTPS, se utiliza
`AIVO_HTTPS_PROXY` para autenticación y envío. Si un proxy requiere un puerto,
incluirlo en la URL indicada por infraestructura. Si estas variables están
vacías, Requests utiliza la configuración estándar de proxy del entorno.

El nombre `AIVO_HTTPS_PROXY` indica el protocolo del destino; el esquema de su
valor indica cómo conectarse al proxy. Para un proxy HTTP debe ser
`http://claro-proxy`, también cuando el destino Aivo usa HTTPS. Requests crea
un túnel CONNECT y establece TLS con Aivo dentro de ese túnel. Configurar
`https://claro-proxy` intenta establecer TLS con el propio proxy y puede causar
`ProxyError` con `UNEXPECTED_EOF_WHILE_READING` si el proxy no admite esa conexión.
Ver [documentación de proxies de urllib3](https://urllib3.readthedocs.io/en/stable/advanced-usage.html#http-and-https-proxies).

`AIVO_TIMEOUT` establece el tiempo máximo de espera de conexión y lectura en
segundos (30 por defecto). No es un límite de duración total de la operación.

La respuesta de `/auth` tiene este formato:

```json
{"Authorization": "Bearer <token>"}
```

Por defecto se prioriza el campo `Authorization`. Se retira el prefijo recibido
y se construye el header `Authorization: Bearer <token>` una sola vez. No es
necesario configurar `AIVO_AUTH_TOKEN_FIELD` para esta respuesta. Se mantienen
`token`, `access_token`, `data.token` y `data.access_token` por compatibilidad.
Si otra respuesta usa un campo distinto, indicar su ruta en
`AIVO_AUTH_TOKEN_FIELD`, por ejemplo `result.bearer`. Nunca se imprime ni se
guarda el token de autenticación.

## Avería diagnosticada

```powershell
python -m src.aivo_whatsapp --plantilla averia_diagnosticada --to 999876502 --nombre "Daniel Muñante" --hora "08:00" --periodo PM
```

Usa campaña `69f45f6b-31d3-4337-b6d5-b0f31997aef5`, idioma `es_PE` y los
parámetros de texto en orden: nombre, hora, AM/PM. La hora usa formato de 12
horas, con dos dígitos; se elimina el espacio final del ejemplo recibido.

## Avería solucionada

```powershell
python -m src.aivo_whatsapp --plantilla averia_solucionada --to 999876502 --nombre "Daniel Muñante"
```

Usa campaña `a8a6350f-898a-4077-a20e-8b96e3731786`, idioma `en` y un único
parámetro de texto: nombre. Ambas conservan el namespace
`c44af9b7_3008_4b30_b7e8_070c35442389`, `type=template`,
`recipient_type=individual` y `language.policy=deterministic`.

El celular se envía tal como se recibe; no se agrega un prefijo de país.
Confirmar el formato requerido por la cuenta Aivo antes del envío real.

## Revisar sin enviar

```powershell
python -m src.aivo_whatsapp --plantilla averia_diagnosticada --to 999876502 --nombre "Daniel Muñante" --hora "08:00" --periodo PM --dry-run
```

`--dry-run` valida e imprime el JSON sin llamadas de red ni credenciales.
Sin esa opción se solicita el envío real. El código de salida es `0` si Aivo
responde HTTP 2xx, o `1` por configuración inválida o fallo del servicio.
Un HTTP 2xx indica aceptación de la solicitud; no confirma entrega al celular.
La salida incluye la respuesta de envío devuelta por Aivo.

Se valida la configuración y los parámetros antes de autenticar. Se mantienen
la verificación TLS y un tiempo de espera en ambos POST. No hay reintentos
automáticos: ante una desconexión o timeout durante el envío, comprobar el
estado en Aivo antes de repetir para evitar mensajes duplicados.

## Diagnóstico de conexión desde Airflow

Las pruebas unitarias usan respuestas simuladas y no verifican la salida de
red del servidor. Para probar únicamente la autenticación desde el contenedor:

```bash
python3 -m src.aivo_whatsapp --check-auth
```

Esta opción realiza únicamente el POST de autenticación y no imprime el token
ni solicita mensajes. Devuelve `autenticacion_correcta: true` si obtiene el token.
Los errores de conexión incluyen el tipo y la causa original con credenciales
ocultas, para distinguir certificados TLS, proxy y problemas de DNS o red.

Para comprobar el esquema HTTP del proxy sin modificar el archivo `.env`:

```bash
AIVO_HTTPS_PROXY=http://claro-proxy python3 -m src.aivo_whatsapp --check-auth
```

Si funciona, guardar `AIVO_HTTPS_PROXY=http://claro-proxy` en `.env` y actualizar
también cualquier variable `AIVO_HTTPS_PROXY` ya definida en el worker, porque
las variables existentes del entorno tienen prioridad sobre el archivo.

Si el error indica verificación de certificados, instalar las CA confiables en
el contenedor o establecer `REQUESTS_CA_BUNDLE` con la ruta de un archivo PEM
que contenga las CA necesarias. Si indica proxy, revisar `HTTPS_PROXY`,
`HTTP_PROXY` y `NO_PROXY`, además de `AIVO_HTTP_PROXY` y `AIVO_HTTPS_PROXY` si se
configuraron explícitamente. La verificación TLS permanece habilitada.

## Uso desde otro proceso Python

```python
from pathlib import Path
from dotenv import load_dotenv
from src.aivo_whatsapp import AivoClient, AivoSettings

load_dotenv(Path("src/aivo_whatsapp/.env"))
client = AivoClient(AivoSettings.from_environment())
respuesta = client.send_message(
    "averia_diagnosticada", "999876502", "Daniel Muñante", "08:00", "PM"
)
```

## Integración futura con Airflow

El DAG se creará posteriormente. El cliente puede invocarse desde una tarea
Python mediante `send_message(...)`. La autenticación y el envío ocurren al
llamar al método, nunca al importar el módulo; cada llamada obtiene un token
nuevo. El cliente devuelve la respuesta y propaga `AivoError` ante fallos, sin
imprimir resultados ni terminar el proceso.

Las credenciales deben estar disponibles en el worker que ejecute la tarea;
pueden pasarse directamente a `AivoSettings` desde la configuración de Airflow.
Los reintentos de la tarea deberán considerar que un timeout puede ocurrir
después de que Aivo haya aceptado el mensaje, para evitar envíos duplicados.

## Pruebas sin envíos reales

```powershell
python -m unittest discover -s tests/aivo_whatsapp -v
```
