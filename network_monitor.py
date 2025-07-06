import subprocess
import re
import platform

def ping_host(host):
    system = platform.system()
    if system == 'Windows':
        cmd = ['ping', '-n', '4', host]
    else:
        cmd = ['ping', '-c', '4', host]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = result.stdout
        # Buscar latencia promedio
        if system == 'Windows':
            match = re.search(r'Media = (\d+)ms', output)
            if not match:
                match = re.search(r'Average = (\d+)ms', output)
            if not match:
                match = re.search(r'M[íi]nimo = \d+ms, M[áa]ximo = \d+ms, Media = (\d+)ms', output)
        else:
            # Linux: buscar 'avg' en la línea de estadísticas
            match = re.search(r'avg[/=](\d+\.?\d*)', output)
            if not match:
                # Formato típico: rtt min/avg/max/mdev = 10.123/20.456/30.789/5.678 ms
                match = re.search(r'rtt [^=]+= [^/]+/(\d+\.?\d*)/', output)
        avg_latency = int(float(match.group(1))) if match else None
        return avg_latency, output
    except Exception as e:
        return None, str(e)

def traceroute_host(host):
    system = platform.system()
    if system == 'Windows':
        cmd = ['tracert', '-h', '15', '-w', '1000', host]
    else:
        cmd = ['traceroute', '-m', '15', host]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        output = result.stdout
        hops = 0
        for line in output.splitlines():
            line_stripped = line.strip()
            if system == 'Windows':
                # Contar solo las líneas que empiezan con número seguido de espacios
                if re.match(r'^\s*\d+\s+', line_stripped) and ('ms' in line_stripped or '*' in line_stripped):
                    hops += 1
            else:
                # Linux: líneas que empiezan con número y contienen una IP o *
                if re.match(r'^\s*\d+\s+', line_stripped) and (re.search(r'(\d+\.\d+\.\d+\.\d+|\*)', line_stripped)):
                    hops += 1
        return hops if hops > 0 else None, output
    except subprocess.TimeoutExpired:
        return None, "Timeout en traceroute"
    except Exception as e:
        return None, str(e)
