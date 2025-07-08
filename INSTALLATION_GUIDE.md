# Guía de Instalación - Bot MQTT Telegram

## ⚠️ PROBLEMA DETECTADO
El bot se ejecuta correctamente, pero **falta el broker MQTT**. Error actual:
```
ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it
```

## Dependencias del Proyecto

### 1. Python 3.7+
✅ **Instalado correctamente**

### 2. Dependencias Python
✅ **Instaladas correctamente**
```bash
pip install -r requirements.txt
```

**Contenido mínimo de requirements.txt:**
```
telepot
paho-mqtt
```

### 3. ⚠️ **FALTA: Broker MQTT (Mosquitto)**

## Instalación de Mosquitto MQTT Broker en Windows

### Opción 1: Descarga Manual (Recomendada)

1. **Ir a la página oficial:**
   - Abrir: https://mosquitto.org/download/
   - Descargar el instalador de Windows (32-bit o 64-bit según tu sistema)

2. **Ejecutar el instalador:**
   - Ejecutar como administrador
   - Seguir las instrucciones de instalación

3. **Instalar como servicio de Windows:**
   ```powershell
   # Abrir PowerShell como administrador
   cd "C:\Program Files\mosquitto"
   .\mosquitto install
   ```

4. **Iniciar el servicio:**
   ```powershell
   net start mosquitto
   ```

5. **Verificar que está corriendo:**
   ```powershell
   netstat -an | findstr :1883
   ```

### Opción 2: Usar binarios precompilados

Si prefieres no instalar, puedes descargar binarios:
- GitHub: https://github.com/Geloi/mosquitto-win32-binary
- Descargar y extraer los archivos
- Ejecutar `mosquitto.exe` desde la línea de comandos

## Verificación de la Instalación

### 1. Verificar que Mosquitto está corriendo:
```powershell
netstat -an | findstr :1883
```
Debería mostrar algo como: `TCP    0.0.0.0:1883           0.0.0.0:0              LISTENING`

### 2. Probar el broker:
```powershell
# Terminal 1 - Suscribirse a un topic
mosquitto_sub -h localhost -t test/topic

# Terminal 2 - Publicar un mensaje
mosquitto_pub -h localhost -t test/topic -m "Hola mundo"
```

### 3. Ejecutar el bot:
```bash
python inicio.py
```

## Configuración del Proyecto

El archivo `config.py` ya está configurado para usar:
- **Broker:** localhost:1883
- **Usuario:** anónimo (sin autenticación)
- **Topic:** mensaje_grupo

## Alternativa: Usar un Broker MQTT en la Nube

Si no quieres instalar Mosquitto localmente, puedes usar un broker público:

### Modificar config.py:
```python
MQTT_BROKER = 'broker.hivemq.com'  # Broker público
MQTT_PORT = 1883
MQTT_TOPIC = 'tu-topic-unico/mensajes'  # Usar un topic único
```

**Brokers públicos disponibles:**
- `broker.hivemq.com:1883`
- `test.mosquitto.org:1883`
- `broker.emqx.io:1883`

## Pasos para Ejecutar el Proyecto (Resumen)

1. ✅ Instalar Python 3.7+
2. ✅ Instalar dependencias: `pip install -r requirements.txt`
3. ⚠️ **INSTALAR Y EJECUTAR MOSQUITTO MQTT BROKER**
4. ✅ Configurar `config.py` con tu token de Telegram
5. ✅ Ejecutar: `python inicio.py`

## Comandos del Bot en Telegram

Una vez que todo esté funcionando:

- `/start` - Iniciar el bot
- `/destino <host>` - Consultar latencia y saltos (ej: `/destino 8.8.8.8`)
- `/monitorear <host>` - Iniciar monitoreo recurrente
- `/detener <host>` - Detener el monitoreo

## Notas Importantes

- El bot necesita el token de Telegram válido en `config.py`
- Mosquitto debe estar corriendo antes de ejecutar el bot
- El proyecto usa comandos de red (`ping`, `tracert`) que requieren privilegios de red
- Los resultados se publican en el topic MQTT configurado 