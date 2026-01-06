# 📷 Teki Camera Automation & Auditor

> Ferramenta de automação e auditoria para dispositivos CCTV Teki, combinando Web Scraping (Selenium) e protocolo ONVIF para validação de configurações e sincronia de tempo.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Selenium](https://img.shields.io/badge/Selenium-Web%20Scraping-green?style=flat&logo=selenium)
![Bash](https://img.shields.io/badge/Bash-Scripting-lightgrey?style=flat&logo=gnu-bash)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-orange)

## 📋 Sobre o Projeto

Este projeto foi desenvolvido para automatizar a tarefa repetitiva e manual de auditar grandes parques de câmeras de segurança IP (modelo Teki). A solução atua em duas frentes:

1.  **Auditoria de Configurações (Python + Selenium):** Acessa a interface web de cada câmera em modo *headless*, extrai configurações críticas (Resolução, Codec, NTP, Idioma) e compara com o padrão de conformidade da organização.
2.  **Verificação de Sincronia de Tempo (Bash + ONVIF):** Utiliza o protocolo ONVIF para consultar o horário interno do dispositivo e identificar desvios (*time drift*) que possam comprometer a validade jurídica das gravações.

## 🚀 Funcionalidades

* **Coleta Automatizada:** Extração de MAC, Serial, Firmware e Configurações de Vídeo.
* **Validação de NTP:** Verifica se o servidor NTP está configurado corretamente.
* **Time Drift Check:** Script Bash dedicado para auditoria precisa de horário via ONVIF CLI.
* **Geração de Relatórios:** Exporta os dados auditados para CSV (`dados_teki.csv`) para análise em planilhas ou Power BI.
* **Sistema de Logs:** Registro detalhado de sucessos e falhas de conexão para troubleshooting.
* **Segurança:** Suporte a geração dinâmica de senhas (via `generate_password.py`) e ocultação de credenciais.

## 🛠️ Tecnologias Utilizadas

* **Linguagens:** Python 3, Bash Script.
* **Bibliotecas Python:** `selenium`, `webdriver-manager`.
* **Ferramentas Externas:** `onvif-cli` (Node.js).
* **Browser Driver:** Microsoft Edge WebDriver.

## ⚙️ Pré-requisitos

Antes de executar, certifique-se de ter instalado:

1.  **Python 3.8+**
2.  **Node.js** (Necessário para a ferramenta de auditoria de tempo):
    ```bash
    npm install -g onvif-cli
    ```
3.  **Microsoft Edge** (O script utiliza o driver nativo do Edge).

## 📦 Instalação

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/SEU_USUARIO/teki-automation.git](https://github.com/SEU_USUARIO/teki-automation.git)
    cd teki-automation
    ```

2.  Instale as dependências do Python:
    ```bash
    pip install -r requirements.txt
    ```

3.  Crie o arquivo de lista de IPs (`ips_teki.txt`) na raiz do projeto seguindo o modelo:
    ```text
    192.168.1.10, Camera_Entrada_Principal
    192.168.1.11, Camera_Estacionamento
    ```

## ▶️ Como Usar

### 1. Auditoria de Configurações (Python)
Executa a varredura via interface web e gera o CSV principal.

```bash
python teki_scanner.py
O script rodará em segundo plano (headless). Acompanhe o progresso no terminal ou no arquivo scan_teki.log.
```
### 2. Auditoria de Horário (Bash)
Consulta o horário via protocolo ONVIF. Recomenda-se usar o Git Bash (Windows) ou terminal Linux.

```Bash

./onvif_time_audit.sh
Os resultados brutos serão salvos em raw_onvif_data.txt.
```

## 📂 Estrutura do Projeto
```
teki-automation/
├── teki_scanner.py        # Script principal de auditoria (Selenium)
├── onvif_time_audit.sh    # Script de verificação de horário (ONVIF)
├── generate_password.py   # Módulo auxiliar de senhas (não incluído por segurança)
├── requirements.txt       # Dependências Python
├── ips_example.txt        # Modelo de arquivo de IPs
├── .gitignore             # Arquivos ignorados pelo Git
└── README.md              # Documentação
```

## ⚠️ Disclaimer
Este software foi desenvolvido para uso administrativo em redes autorizadas. O uso não autorizado em dispositivos de terceiros pode violar leis de privacidade e segurança. Utilize com responsabilidade.

Desenvolvido por João Pedro de Assunção Rego