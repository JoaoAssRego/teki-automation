import csv
import datetime
import logging
import os
import time
import sys
from typing import Dict, Any, List

from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Tenta importar o gerador de senhas (copie este arquivo do projeto anterior)
try:
    from generate_password import create as generate_custom_password
except ImportError:
    generate_custom_password = None

# --- Configurações ---
INPUT_FILE = 'ips_teki.txt'
OUTPUT_FILE = 'dados_teki.csv'
LOG_FILE = 'scan_teki.log'
DEFAULT_USER = 'monitora'
DEFAULT_PASS = 'abcd1234'  # Recomendado: Usar variável de ambiente os.getenv('TEKI_PASS')

# --- Configuração de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class TekiScanner:
    def __init__(self, headless=True):
        self.options = EdgeOptions()
        if headless:
            self.options.add_argument("--headless")
            self.options.add_argument("--log-level=3") # Menos verboso no console
        self.driver = None

    def start_driver(self):
        """Inicia ou reinicia o WebDriver."""
        if self.driver:
            self.driver.quit()
        try:
            self.driver = webdriver.Edge(options=self.options)
        except Exception as e:
            logging.critical(f"Falha ao iniciar WebDriver: {e}")
            sys.exit(1)

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def wait_for(self, by, value, timeout=5, multiple=False):
        """Helper para esperar elementos."""
        try:
            if multiple:
                return WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((by, value)))
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            return None

    def safe_get_value(self, element_or_none, attr="value"):
        """Extrai valor de forma segura."""
        if element_or_none:
            return element_or_none.get_attribute(attr)
        return "N/A"

    def login(self, ip, password):
        """Tenta logar com senha customizada, fallback para padrão."""
        url_custom = f"http://admin:{password}@{ip}/system.html"
        url_default = f"http://{DEFAULT_USER}:{DEFAULT_PASS}@{ip}/system.html"
        
        try:
            self.driver.get(url_custom)
            # Verifica sucesso procurando um elemento chave
            if self.wait_for(By.NAME, "c7_MAC", timeout=3):
                return True, "Custom"
        except Exception:
            pass
        
        try:
            logging.info(f"[{ip}] Tentando senha padrão...")
            self.driver.get(url_default)
            if self.wait_for(By.NAME, "c7_MAC", timeout=3):
                return True, "Default"
        except Exception:
            pass

        return False, "Falha"

    def scan_camera(self, ip, nome) -> Dict[str, Any]:
        data = {
            'Ip': ip, 'MAC': 'N/A', 'Nome': nome, 'Status': 'Erro Conexão',
            'Language': 'N/A', 'NTP': 'N/A', 'NTP_Server': 'N/A',
            'Video_Setting': 'N/A', 'Video_Erros': 'N/A'
        }

        # Gera senha customizada se o módulo existir
        custom_pass = generate_custom_password(nome) if generate_custom_password else "admin"
        
        success, auth_type = self.login(ip, custom_pass)
        if not success:
            logging.error(f"[{ip}] Falha no Login.")
            return data

        data['Status'] = 'Sucesso'
        
        try:
            # 1. Coleta Básica
            data['MAC'] = self.safe_get_value(self.wait_for(By.NAME, "c7_MAC"))
            
            # 2. Language Check
            chk_english = self.wait_for(By.XPATH, '//*[@id="div_serv"]/table/tbody/tr[4]/td[2]/table/tbody/tr/td/input[3]')
            data['Language'] = "Correto" if (chk_english and chk_english.is_selected()) else "Errado"

            # 3. NTP Settings
            self.wait_for(By.ID, "oTimeSetting").click()
            ntp_chk = self.wait_for(By.XPATH, "//input[contains(@onclick, 'Ntp')]") # Melhorando seletor
            
            if ntp_chk and ntp_chk.is_selected():
                data['NTP'] = "Habilitado"
                # Ajuste o XPath conforme a estrutura real da página
                ntp_serv = self.wait_for(By.XPATH, "//input[@name='sNtpServer']") 
                # Se não tiver name, use o xpath absoluto do seu código original
                if not ntp_serv:
                     ntp_serv = self.wait_for(By.XPATH, "/html/body/table/tbody/tr[2]/td[2]/form/div[3]/table/tbody/tr[9]/td[2]/input")
                
                data['NTP_Server'] = self.safe_get_value(ntp_serv)
            else:
                data['NTP'] = "Desabilitado"

            # 4. Video Settings
            self.wait_for(By.ID, "mVideo").click()
            
            # Mapeamento e Validação (Simplificado para o exemplo)
            # Adicione aqui a lógica de comparação detalhada do seu notebook
            # ...
            data['Video_Setting'] = "Não Verificado (Implementar Lógica)" 

        except Exception as e:
            logging.error(f"[{ip}] Erro durante coleta: {e}")
            data['Status'] = f"Erro Coleta: {e}"

        return data

def main():
    if not os.path.exists(INPUT_FILE):
        logging.critical(f"Arquivo {INPUT_FILE} não encontrado.")
        return

    ips_to_scan = []
    with open(INPUT_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 2:
                ips_to_scan.append((parts[0].strip(), parts[1].strip()))

    logging.info(f"Iniciando varredura em {len(ips_to_scan)} dispositivos.")
    
    scanner = TekiScanner(headless=True)
    scanner.start_driver()
    
    results = []
    
    try:
        for ip, nome in ips_to_scan:
            logging.info(f"Processando: {ip} ({nome})")
            info = scanner.scan_camera(ip, nome)
            results.append(info)
    except KeyboardInterrupt:
        logging.warning("Varredura interrompida pelo usuário.")
    finally:
        scanner.close_driver()

    # Exportação
    keys = results[0].keys() if results else []
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    
    logging.info(f"Relatório salvo em {OUTPUT_FILE}")

if __name__ == "__main__":
    main()