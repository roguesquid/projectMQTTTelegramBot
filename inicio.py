from bot_telegram import main as bot_main
from config import TELEGRAM_TOKEN, MQTT_BROKER, MQTT_PORT, MQTT_USER
from datetime import datetime

if __name__ == '__main__':
    print("="*50)
    print(f"🟢 Bot de Monitoreo de Red - INICIANDO ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"Telegram Token: ...{TELEGRAM_TOKEN[-8:]}")
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"MQTT Usuario: {MQTT_USER if MQTT_USER else '(anónimo)'}")
    print("Esperando comandos desde Telegram...")
    print("="*50)
    bot_main()