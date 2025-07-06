import telepot
from telepot.loop import MessageLoop
from config import TELEGRAM_TOKEN
from network_monitor import ping_host, traceroute_host
from mqtt_client import publish_result, subscribe_and_forward
from monitoring_service import MonitoringService
import threading

monitoring_services = {}
bot = telepot.Bot(TELEGRAM_TOKEN)

# Guarda el último chat_id para enviar alertas y reenviar MQTT
last_chat_id = None
mqtt_client = None

def handle(msg):
    global last_chat_id, mqtt_client
    content_type, chat_type, chat_id = telepot.glance(msg)
    last_chat_id = chat_id
    if mqtt_client is None:
        mqtt_client = subscribe_and_forward(bot, chat_id)
    if content_type != 'text':
        bot.sendMessage(chat_id, 'Solo se aceptan mensajes de texto.')
        return
    text = msg['text']
    if text.startswith('/start'):
        bot.sendMessage(chat_id, 'Bot listo. Usa /destino <host> para comenzar.')
    elif text.startswith('/destino'):
        parts = text.split()
        if len(parts) < 2:
            bot.sendMessage(chat_id, 'Debes indicar un destino.')
            return
        host = parts[1]
        latency, _ = ping_host(host)
        hops, _ = traceroute_host(host)
        publish_result(latency, hops, host)
        bot.sendMessage(chat_id, f'Latencia promedio: {latency} ms\nSaltos: {hops}')
    elif text.startswith('/monitorear'):
        parts = text.split()
        if len(parts) < 2:
            bot.sendMessage(chat_id, 'Debes indicar un destino.')
            return
        host = parts[1]
        if host in monitoring_services:
            bot.sendMessage(chat_id, 'Ya se está monitoreando este destino.')
            return
        def result_callback(destino, latency, hops):
            publish_result(latency, hops, destino)
            bot.sendMessage(chat_id, f'[Monitoreo] {destino}: Latencia={latency} ms, Saltos={hops}')
        service = MonitoringService(host, alert_callback=send_alert, result_callback=result_callback)
        monitoring_services[host] = service
        service.start()
        bot.sendMessage(chat_id, f'Monitoreo iniciado para {host}.')
    elif text.startswith('/detener'):
        parts = text.split()
        if len(parts) < 2:
            bot.sendMessage(chat_id, 'Debes indicar un destino.')
            return
        host = parts[1]
        service = monitoring_services.pop(host, None)
        if service:
            service.stop()
            bot.sendMessage(chat_id, f'Monitoreo detenido para {host}.')
        else:
            bot.sendMessage(chat_id, 'No se estaba monitoreando ese destino.')
    else:
        bot.sendMessage(chat_id, 'Comando no reconocido.')

def send_alert(destino):
    if last_chat_id:
        bot.sendMessage(last_chat_id, f'ALERTA: El host {destino} está inalcanzable.')

def main():
    MessageLoop(bot, handle).run_as_thread()
    print('Bot de Telegram corriendo...')
    while True:
        pass  # Mantener el hilo principal vivo

if __name__ == '__main__':
    main()
