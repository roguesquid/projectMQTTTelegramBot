import threading
import time
from network_monitor import ping_host, traceroute_host

class MonitoringService:
    def __init__(self, destino, interval=5, alert_callback=None, result_callback=None, latency_threshold=None):
        self.destino = destino
        self.interval = interval
        self.running = False
        self.thread = None
        self.alert_callback = alert_callback
        self.result_callback = result_callback
        self.latency_threshold = latency_threshold

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.monitor)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def monitor(self):
        while self.running:
            latency, _ = ping_host(self.destino)
            hops, _ = traceroute_host(self.destino)
            if latency is None and self.alert_callback:
                self.alert_callback(self.destino, reason='inaccesible')
            elif self.latency_threshold is not None and latency is not None and latency > self.latency_threshold:
                if self.alert_callback:
                    self.alert_callback(self.destino, latency=latency, reason='umbral')
            if self.result_callback:
                self.result_callback(self.destino, latency, hops)
            time.sleep(self.interval)
