# Sistema de Monitoreo de Latencia y Saltos vía Telegram y MQTT

## Descripción

Este proyecto permite a un usuario, a través de un bot de Telegram, ejecutar comandos de red (ping y traceroute) desde un servidor, monitorear la latencia y los saltos a un nodo objetivo, y publicar los resultados en un broker MQTT. El sistema también puede monitorear recurrentemente un nodo y enviar alertas al bot si el host es inalcanzable.

## Requisitos

- Python 3.7+
- Mosquitto (u otro broker MQTT)
- Dependencias Python:
  - telepot
  - paho-mqtt

Instala las dependencias con:

```
pip install telepot paho-mqtt
```

## Configuración

Edita el archivo `config.py` y coloca tu token de bot de Telegram y los datos de tu broker MQTT:

```python
TELEGRAM_TOKEN = 'TU_TOKEN_AQUI'
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'mensaje_grupo'
MQTT_USER = ''  # Opcional
MQTT_PASSWORD = ''  # Opcional
```

## Uso

1. **Inicia el broker Mosquitto** (si no está corriendo):

   - En consola: `mosquitto`

2. **Ejecuta el bot:**

   - En consola: `python inicio.py`

3. **Desde Telegram:**

   - Escribe `/start` para iniciar.
   - Escribe `/destino <host>` para consultar latencia y saltos (ejemplo: `/destino 8.8.8.8`).
   - Escribe `/monitorear <host>` para iniciar monitoreo recurrente (ejemplo: `/monitorear 8.8.8.8`).
   - Escribe `/detener <host>` para detener el monitoreo.

4. **Monitoreo MQTT:**
   - Los resultados se publican en el topic configurado y pueden verse en MQTT Explorer o con `mosquitto_sub`:
     ```
     mosquitto_sub -h localhost -t mensaje_grupo
     ```
   - Puedes publicar mensajes de prueba en el topic y el bot los reenviará al chat:
     ```
     mosquitto_pub -h localhost -t mensaje_grupo -m "Mensaje de prueba"
     ```

## Seguridad

- Puedes configurar usuario y contraseña para el broker MQTT en `config.py`.
- El sistema maneja errores de red y de comandos.

## Notas

- El bot solo responde a comandos de texto.
- El monitoreo tiene un retardo de 5 segundos entre ciclos.
- Si el host es inalcanzable, se envía una alerta al chat.

## Créditos

Desarrollado para prácticas de Redes de Comunicación.
