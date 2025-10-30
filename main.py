import requests
import json
import sqlite3 # A biblioteca para o nosso banco de dados!
import time
import socket
import argparse
from tqdm import tqdm
from dotenv import load_dotenv
import os
import nmap

# --- CONFIGURAÇÕES E CONSTANTES ---
load_dotenv()
ABUSEIPDB_KEY = os.environ.get("ABUSEIPDB_API_KEY")
DB_FILE = "ip_intelligence.db" # O nome do nosso arquivo de banco de dados

# --- FUNÇÕES DE GERENCIAMENTO DO BANCO DE DADOS (SQLite) ---

def initialize_database():
    """Cria a tabela no banco de dados se ela ainda não existir."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # A query para criar a tabela. `IF NOT EXISTS` previne erros se a tabela já foi criada.
    # `UNIQUE(IP)` garante que não teremos IPs duplicados na tabela.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT UNIQUE,
            hostname TEXT,
            open_ports TEXT,
            abuse_score INTEGER,
            total_reports INTEGER,
            country TEXT,
            city TEXT,
            isp TEXT,
            last_analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_report_to_db(report):
    """Salva um único relatório no banco de dados. Usa ON CONFLICT para atualizar se o IP já existir."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Esta query é poderosa:
    # INSERT OR REPLACE: Se o IP (que é UNIQUE) não existe, ele insere. 
    # Se o IP já existe, ele substitui a linha antiga pela nova, atualizando os dados.
    query = '''
        INSERT OR REPLACE INTO reports (
            ip, hostname, open_ports, abuse_score, total_reports, country, city, isp, last_analyzed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    '''
    
    # Os valores precisam estar na mesma ordem da query
    values = (
        report.get("IP"),
        report.get("Hostname"),
        report.get("Portas Abertas (Comuns)"),
        report.get("Pontuação de Abuso (%)"),
        report.get("Total de Denúncias"),
        report.get("País"),
        report.get("Cidade"),
        report.get("Provedor (ISP)")
    )
    
    cursor.execute(query, values)
    conn.commit()
    conn.close()

# --- FUNÇÕES DE ENRIQUECIMENTO DE DADOS (As mesmas da v3.0) ---

def get_ip_geolocation(ip_address):
    url = f"http://ip-api.com/json/{ip_address}"
    try:
        r = requests.get(url, timeout=5 ); r.raise_for_status(); data = r.json()
        return {"error": data.get("message")} if data.get("status") == "fail" else data
    except requests.exceptions.RequestException as e: return {"error": f"Erro (ip-api): {e}"}

def get_abuseipdb_report(ip_address):
    if not ABUSEIPDB_KEY: return {"abuseConfidenceScore": None}
    url = 'https://api.abuseipdb.com/api/v2/check'
    params = {'ipAddress': ip_address}; headers = {'Key': ABUSEIPDB_KEY, 'Accept': 'application/json'}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=5 )
        return {"abuseConfidenceScore": None} if r.status_code == 429 else r.json().get("data", {})
    except requests.exceptions.RequestException: return {"abuseConfidenceScore": None}

def get_reverse_dns(ip_address):
    try: return socket.gethostbyaddr(ip_address)[0]
    except (socket.herror, Exception): return None

def get_open_ports(ip_address):
    try:
        nm = nmap.PortScanner(); nm.scan(ip_address, arguments='-T4 -F')
        if ip_address in nm.all_hosts() and 'tcp' in nm[ip_address]:
            return ", ".join(str(p) for p in nm[ip_address]['tcp'].keys())
        return None
    except Exception: return None

# --- FUNÇÃO PRINCIPAL DE PROCESSAMENTO ---

def process_ips(ip_list):
    """Processa uma lista de IPs, consulta as fontes e salva no banco de dados."""
    print(f"\n🔍 Analisando {len(ip_list)} IPs e salvando no banco de dados '{DB_FILE}'...")
    
    for ip in tqdm(ip_list, desc="Progresso da Análise"):
        geo_data = get_ip_geolocation(ip)
        
        if "error" in geo_data:
            print(f"\nAVISO: Não foi possível analisar o IP {ip}. Erro: {geo_data['error']}")
            continue

        abuse_data = get_abuseipdb_report(ip)
        hostname = get_reverse_dns(ip)
        open_ports = get_open_ports(ip)
        
        consolidated_report = {
            "IP": ip,
            "Hostname": hostname,
            "Portas Abertas (Comuns)": open_ports,
            "Pontuação de Abuso (%)": abuse_data.get('abuseConfidenceScore'),
            "Total de Denúncias": abuse_data.get('totalReports'),
            "País": geo_data.get('country'),
            "Cidade": geo_data.get('city'),
            "Provedor (ISP)": geo_data.get('isp'),
        }
        
        # Salva o resultado deste IP imediatamente no banco de dados
        save_report_to_db(consolidated_report)
        time.sleep(1.1)
    
    print(f"\n✅ Análise concluída! Todos os resultados foram salvos em '{DB_FILE}'.")

# --- FLUXO PRINCIPAL COM ARGPARSE ---
if __name__ == "__main__":
    # Garante que o banco de dados e a tabela existam antes de começar
    initialize_database()

    parser = argparse.ArgumentParser(description="IP Analyzer Pro v4.0 - Análise de IP com Banco de Dados.")
    parser.add_argument("-i", "--ip", help="Um único endereço de IP para analisar.")
    parser.add_argument("-f", "--file", help="Caminho para um arquivo de texto com uma lista de IPs.")
    
    args = parser.parse_args()

    ips_to_analyze = []
    if args.ip:
        ips_to_analyze.append(args.ip)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                ips_to_analyze = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ ERRO: Arquivo '{args.file}' não encontrado."); exit()
    else:
        parser.print_help(); exit()

    if ips_to_analyze:
        process_ips(ips_to_analyze)
    else:
        print("Nenhum IP válido para analisar.")
