import threading
import time
from network_monitor import ping_host, traceroute_host

class MonitoringService:
    def __init__(self, destino, interval=5, alert_callback=None, result_callback=None, latency_threshold=None, ping_interval=5, traceroute_interval=60):
        self.destino = destino
        self.interval = interval  # Intervalo de envío de resultados
        self.ping_interval = ping_interval
        self.traceroute_interval = traceroute_interval
        self.running = False
        self.ping_thread = None
        self.traceroute_thread = None
        self.monitor_thread = None
        self.message_thread = None
        self.alert_callback = alert_callback
        self.result_callback = result_callback
        self.latency_threshold = latency_threshold
        self.ping_result = None
        self.traceroute_result = None
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        self.ping_thread = threading.Thread(target=self.ping_loop)
        self.traceroute_thread = threading.Thread(target=self.traceroute_loop)
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.message_thread = threading.Thread(target=self.message_loop)
        self.ping_thread.start()
        self.traceroute_thread.start()
        self.monitor_thread.start()
        self.message_thread.start()

    def stop(self):
        self.running = False
        for t in [self.ping_thread, self.traceroute_thread, self.monitor_thread, self.message_thread]:
            if t:
                t.join()

    def ping_loop(self):
        while self.running:
            latency, _ = ping_host(self.destino)
            with self.lock:
                self.ping_result = latency
            if latency is None and self.alert_callback:
                self.alert_callback(self.destino, reason='inaccesible')
            elif self.latency_threshold is not None and latency is not None and latency > self.latency_threshold:
                if self.alert_callback:
                    self.alert_callback(self.destino, latency=latency, reason='umbral')
            time.sleep(self.ping_interval)

    def traceroute_loop(self):
        while self.running:
            hops, _ = traceroute_host(self.destino)
            with self.lock:
                self.traceroute_result = hops
            time.sleep(self.traceroute_interval)

    def monitor_loop(self):
        # Este hilo solo orquesta, podría usarse para lógica adicional
        while self.running:
            time.sleep(self.interval)

    def message_loop(self):
        # Este hilo se encarga de enviar los resultados periódicamente
        while self.running:
            with self.lock:
                latency = self.ping_result
                hops = self.traceroute_result
            if self.result_callback:
                self.result_callback(self.destino, latency, hops)
            time.sleep(self.interval)
