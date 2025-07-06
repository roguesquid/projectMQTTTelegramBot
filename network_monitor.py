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
        # También buscar con caracteres especiales que pueden aparecer
        if not match:
            match = re.search(r'M[íi]nimo = \d+ms, M[áa]ximo = \d+ms, Media = (\d+)ms', output)
        avg_latency = int(match.group(1)) if match else None
        return avg_latency, output
    except Exception as e:
        return None, str(e)

def traceroute_host(host):
    try:
        # Usar tracert normal con timeout más largo
        result = subprocess.run(['tracert', '-h', '15', '-w', '1000', host], capture_output=True, text=True, timeout=90)
        output = result.stdout
        hops = 0
        for line in output.splitlines():
            line_stripped = line.strip()
            # Contar solo las líneas que empiezan con número seguido de espacios
            # Formato: "  1     1 ms     1 ms     1 ms  dlinkrouter6651.local [192.168.0.1]"
            # También acepta líneas con asteriscos: "  5     *        *        *     "
            if re.match(r'^\s*\d+\s+', line_stripped) and ('ms' in line_stripped or '*' in line_stripped):
                hops += 1
        return hops if hops > 0 else None, output
    except subprocess.TimeoutExpired:
        # Si hay timeout, usar pathping pero contar solo los saltos válidos
        try:
            result = subprocess.run(['pathping', '-n', '-q', '1', '-h', '15', host], capture_output=True, text=True, timeout=60)
            output = result.stdout
            hops = 0
            # Con pathping, contar solo las líneas del seguimiento inicial
            in_trace_section = False
            for line in output.splitlines():
                line_stripped = line.strip()
                if 'Seguimiento de ruta' in line or 'Tracing route' in line:
                    in_trace_section = True
                    continue
                if 'Procesamiento de' in line or 'Computing statistics' in line:
                    in_trace_section = False
                    break
                if in_trace_section and re.match(r'^\s*\d+\s+', line_stripped):
                    hops += 1
            return hops if hops > 0 else None, output
        except Exception:
            return None, "Timeout en traceroute"
    except Exception as e:
        return None, str(e)
