import paho.mqtt.client as mqtt
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, MQTT_USER, MQTT_PASSWORD

def publish_result(latency, hops, destino):
    client = mqtt.Client()
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    payload = {
        'destino': destino,
        'latencia': latency,
        'saltos': hops
    }
    client.publish(MQTT_TOPIC, str(payload))
    client.disconnect()

def subscribe_and_forward(bot, chat_id):
    def on_connect(client, userdata, flags, rc):
        client.subscribe(MQTT_TOPIC)
    def on_message(client, userdata, msg):
        try:
            # bot.sendMessage(chat_id, f"[MQTT] {msg.topic}: {msg.payload.decode()}")
            print(f"[MQTT] {msg.topic}: {msg.payload.decode()}")
        except Exception as e:
            print('Error procesando mensaje MQTT:', e)
    client = mqtt.Client()
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_start()
    return client
