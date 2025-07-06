import subprocess
import re

def ping_host(host):
    try:
        result = subprocess.run(['ping', '-n', '4', host], capture_output=True, text=True, timeout=10)
        output = result.stdout
        # Buscar 'Media' (español) o 'Average' (inglés)
        match = re.search(r'Media = (\d+)ms', output)
        if not match:
            match = re.search(r'Average = (\d+)ms', output)
        avg_latency = int(match.group(1)) if match else None
        return avg_latency, output
    except Exception as e:
        return None, str(e)

def traceroute_host(host):
    try:
        result = subprocess.run(['tracert', host], capture_output=True, text=True, timeout=20)
        output = result.stdout
        hops = 0
        for line in output.splitlines():
            # Coincide con líneas de saltos válidos: número, tiempos y una IP o nombre de host
            if re.match(r'^\s*\d+\s+.*(\d+ ms|\*)+.*(\d+\.\d+\.\d+\.\d+|[a-zA-Z0-9\-\.]+)$', line.strip()):
                hops += 1
        return hops if hops > 0 else None, output
    except Exception as e:
        return None, str(e)
