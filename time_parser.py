# Verificar se o NTP está ativo

import subprocess
import csv
import re
import sys
from datetime import datetime, timedelta

ARQUIVO_ENTRADA = 'ips_teki.txt'
ARQUIVO_SAIDA = 'relatorio_horarios.csv'
USER = 'monitora'
PASS = 'abcd1234'

def buscar_horario(ip):
    """Executa o onvif-cli e extrai o horário local."""
    cmd = [
        'onvif-cli',
        '--user', USER,
        '--password', PASS,
        '--host', ip,
        'devicemgmt', 'GetSystemDateAndTime'
    ]

    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if resultado.returncode != 0:
            return None # Retorna None em caso de erro do comando

        padrao = r"LocalDateTime.*?Hour', (\d+).*?Minute', (\d+).*?Second', (\d+)"
        match = re.search(padrao, resultado.stdout, re.DOTALL)

        if match:
            h, m, s = map(int, match.groups())
            return f"{h:02d}:{m:02d}:{s:02d}" # Retorna String "HH:MM:SS"
        else:
            return None

    except Exception as e:
        return None 

def main():
    print(f"Lendo IPs de: {ARQUIVO_ENTRADA}")
    
    with open(ARQUIVO_SAIDA,'w',newline='') as arq_out:
        escritor = csv.writer(arq_out)
        escritor.writerow(['IP', 'Horario', 'Status'])

    try:
        with open(ARQUIVO_ENTRADA, 'r') as arq_in, open(ARQUIVO_SAIDA, 'a', newline='') as arq_out:
            leitor = csv.reader(arq_in)
            escritor = csv.writer(arq_out)

            for linha in leitor:
                # Evita linhas vazias ou comentários
                if not linha or linha[0].startswith('#'):
                    continue

                ip = linha[0].strip()
                print(f"Verificando {ip}...")
                
                horario_str = buscar_horario(ip)
                
                # Se não retornou horário (veio None), grava erro e pula
                if not horario_str:
                    escritor.writerow([ip, "N/A", "Erro/Offline"])
                    continue

                # --- CORREÇÃO DO ERRO ABAIXO ---
                
                # 1. Pega o momento atual como OBJETO (não string)
                agora = datetime.now()

                try:
                    # 2. Converte a string da câmera ("14:30:00") para OBJETO datetime
                    # Precisamos combinar a hora da câmera com a data de hoje para fazer contas
                    horario = datetime.strptime(horario_str, '%H:%M:%S').replace(
                        year=agora.year, month=agora.month, day=agora.day
                    )

                    # 3. Faz a comparação matemática usando os objetos
                    # Lógica: Se horário da câmera for maior que (Agora - 10min) E menor que (Agora + 1min de tolerância futura)
                    limite_atras = agora - timedelta(minutes=10)
                    
                    if limite_atras <= horario <= agora + timedelta(minutes=5):
                        escritor.writerow([ip, horario_str, "OK"])
                    else:
                        escritor.writerow([ip, horario_str, "Incorreto"])

                except ValueError:
                    escritor.writerow([ip, horario_str, "Erro Formato"])

    except FileNotFoundError:
        print(f"Arquivo {ARQUIVO_ENTRADA} não encontrado.")

if __name__ == "__main__":
    main()