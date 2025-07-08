import telepot
from telepot.loop import MessageLoop
from config import TELEGRAM_TOKEN
from network_monitor import ping_host, traceroute_host
from mqtt_client import publish_result, subscribe_and_forward
from monitoring_service import MonitoringService
import threading
from datetime import datetime
import time
from telegram import Bot as PTGBot

monitoring_services = {}
bot = telepot.Bot(TELEGRAM_TOKEN)

# Guarda el último chat_id para enviar alertas y reenviar MQTT
last_chat_id = None
mqtt_client = None

def handle(msg):
    global last_chat_id, mqtt_client
    glance_result = telepot.glance(msg)
    content_type, chat_type, chat_id = glance_result[:3]
    last_chat_id = chat_id
    # Obtener información del usuario o grupo
    user_info = msg.get('from', {})
    username = user_info.get('username') or user_info.get('first_name') or 'Desconocido'
    user_id = user_info.get('id', 'N/A')
    group_title = msg.get('chat', {}).get('title')
    text = msg.get('text', '')
    # Detectar comando
    comando = text.split()[0] if text else '(sin comando)'
    # Log en consola
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if group_title:
        print(f"[{now}] Mensaje recibido en grupo '{group_title}' (ID: {chat_id}) de {username} (ID: {user_id}): {text}")
    else:
        print(f"[{now}] Mensaje recibido de {username} (ID: {user_id}): {text}")
    print(f"→ Comando detectado: {comando}")

    if mqtt_client is None:
        mqtt_client = subscribe_and_forward(bot, chat_id)
    if content_type != 'text':
        bot.sendMessage(chat_id, '⚠️ Solo se aceptan mensajes de texto.')
        return
    if text.startswith('/start'):
        bot.sendMessage(chat_id, 
            '👋 ¡Hola! Soy tu bot de monitoreo de red.\n'
            'Usa los siguientes comandos:\n'
            '- /destino <host> para consultar latencia y saltos 🛰️\n'
            '- /monitorear <host> para iniciar monitoreo recurrente 🔄\n'
            '- /detener <host> para detener el monitoreo ⏹️'
        )
    elif text.startswith('/destino'):
        parts = text.split()
        if len(parts) < 2:
            bot.sendMessage(chat_id, '⚠️ Debes indicar un destino.')
            return
        host = parts[1]
        # Mensaje de espera
        try:
            bot.sendMessage(chat_id, f'🔎 Determinando latencia y saltos hacia {host}... Por favor espera.')
        except Exception as e:
            print(f"[ERROR] Al enviar mensaje de espera a Telegram: {e}")
        latency, _ = ping_host(host)
        hops, _ = traceroute_host(host)
        # Validación robusta para evitar None o tipos inesperados
        if latency is None or not isinstance(latency, (int, float)):
            latency_str = "No disponible"
        else:
            latency_str = str(latency)
        if hops is None or not isinstance(hops, (int, float)):
            hops_str = "No disponible"
        else:
            hops_str = str(hops)
        time.sleep(1)
        # Envío asíncrono con python-telegram-bot
        import asyncio
        async def enviar_resultado():
            ptg_bot = PTGBot(token=TELEGRAM_TOKEN)
            await ptg_bot.send_message(
                chat_id=chat_id,
                text=(
                    f"✅ <b>Resultado para <code>{host}</code></b>\n"
                    f"⏱️ <b>Latencia:</b> <code>{latency_str} ms</code>\n"
                    f"🛣️ <b>Saltos:</b> <code>{hops_str}</code>"
                ),
                parse_mode='HTML'
            )
        try:
            asyncio.run(enviar_resultado())
        except Exception as e:
            print(f"[ERROR] Al enviar resultado a Telegram (python-telegram-bot): {e}")
        try:
            publish_result(latency, hops, host)
        except Exception as e:
            print(f"[ERROR] Al publicar en MQTT: {e}")
    elif text.startswith('/monitorear'):
        parts = text.split()
        if len(parts) < 2:
            bot.sendMessage(chat_id, '⚠️ Debes indicar un destino.')
            return
        host = parts[1]
        # Permitir umbral opcional: /monitorear <host> [umbral_ms]
        latency_threshold = None
        if len(parts) >= 3:
            try:
                latency_threshold = int(parts[2])
            except ValueError:
                bot.sendMessage(chat_id, '⚠️ El umbral debe ser un número entero (ms).')
                return
        if host in monitoring_services:
            bot.sendMessage(chat_id, 'ℹ️ Ya se está monitoreando este destino.')
            return
        def result_callback(destino, latency, hops):
            latency_str = f"{latency} ms" if latency is not None else "No disponible"
            hops_str = f"{hops}" if hops is not None else "No disponible"
            # Envío bonito y asíncrono con python-telegram-bot
            import asyncio
            async def enviar_monitoreo():
                ptg_bot = PTGBot(token=TELEGRAM_TOKEN)
                await ptg_bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"📊 <b>[Monitoreo] <code>{destino}</code></b>\n"
                        f"⏱️ <b>Latencia:</b> <code>{latency_str}</code>\n"
                        f"🛣️ <b>Saltos:</b> <code>{hops_str}</code>"
                    ),
                    parse_mode='HTML'
                )
            try:
                asyncio.run(enviar_monitoreo())
            except Exception as e:
                print(f"[ERROR] Al enviar resultado de monitoreo a Telegram (PTB): {e}")
            try:
                publish_result(latency, hops, destino)
            except Exception as e:
                print(f"[ERROR] Al publicar en MQTT (monitoreo): {e}")
        service = MonitoringService(host, alert_callback=send_alert, result_callback=result_callback, latency_threshold=latency_threshold)
        monitoring_services[host] = service
        service.start()
        if latency_threshold is not None:
            bot.sendMessage(chat_id, f'🔄 Monitoreo iniciado para {host} con alerta si latencia > {latency_threshold} ms.')
        else:
            bot.sendMessage(chat_id, f'🔄 Monitoreo iniciado para {host}.')
    elif text.startswith('/detener'):
        parts = text.split()
        if len(parts) < 2:
            bot.sendMessage(chat_id, '⚠️ Debes indicar un destino.')
            return
        host = parts[1]
        service = monitoring_services.pop(host, None)
        if service:
            service.stop()
            bot.sendMessage(chat_id, f'⏹️ Monitoreo detenido para {host}.')
        else:
            bot.sendMessage(chat_id, 'ℹ️ No se estaba monitoreando ese destino.')
    else:
        bot.sendMessage(chat_id, '❓ Comando no reconocido. Usa /start para ver las opciones.')

def send_alert(destino, latency=None, reason=None):
    if last_chat_id:
        if reason == 'umbral' and latency is not None:
            bot.sendMessage(last_chat_id, f'🚨 ALERTA: Latencia alta en {destino}: {latency} ms supera el umbral.')
        elif reason == 'inaccesible':
            bot.sendMessage(last_chat_id, f'🚨 ALERTA: El host {destino} está inalcanzable.')
        else:
            bot.sendMessage(last_chat_id, f'🚨 ALERTA: Evento detectado en {destino}.')

def main():
    MessageLoop(bot, handle).run_as_thread()
    print('Bot de Telegram corriendo...')
    while True:
        pass  # Mantener el hilo principal vivo

if __name__ == '__main__':
    main()
