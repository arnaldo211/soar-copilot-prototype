import requests
import json
import sqlite3
import time
import socket
import argparse
from tqdm import tqdm
from dotenv import load_dotenv
import os
import nmap
from datetime import datetime, timedelta # Importa as bibliotecas de data e hora

# --- CONFIGURAÇÕES E CONSTANTES ---
load_dotenv()
ABUSEIPDB_KEY = os.environ.get("ABUSEIPDB_KEY")
DB_FILE = "ip_intelligence.db"
CACHE_DURATION_DAYS = 7 # Define a duração do cache em dias

# --- FUNÇÕES DE GERENCIAMENTO DO BANCO DE DADOS (SQLite) ---

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT UNIQUE, hostname TEXT, open_ports TEXT,
            abuse_score INTEGER, total_reports INTEGER, country TEXT, city TEXT, isp TEXT,
            last_analyzed_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_report_to_db(report):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    query = '''
        INSERT OR REPLACE INTO reports (ip, hostname, open_ports, abuse_score, total_reports, country, city, isp, last_analyzed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    values = (
        report.get("IP"), report.get("Hostname"), report.get("Portas Abertas (Comuns)"),
        report.get("Pontuação de Abuso (%)"), report.get("Total de Denúncias"), report.get("País"),
        report.get("Cidade"), report.get("Provedor (ISP)"), datetime.now() # Salva a data e hora atual
    )
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def query_db_for_ip(ip):
    """Busca um IP no banco de dados e retorna o resultado se existir."""
    conn = sqlite3.connect(DB_FILE)
    # row_factory permite acessar os resultados como um dicionário (mais fácil)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE ip = ?", (ip,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

# --- FUNÇÕES DE ENRIQUECIMENTO DE DADOS (As mesmas da v4.0) ---
# (Nenhuma mudança necessária aqui, então foram omitidas para brevidade)
def get_ip_geolocation(ip_address):
    #...código igual ao da v4.0...
    url = f"http://ip-api.com/json/{ip_address}"; r = requests.get(url, timeout=5 ); r.raise_for_status(); data = r.json()
    return {"error": data.get("message")} if data.get("status") == "fail" else data

def get_abuseipdb_report(ip_address):
    #...código igual ao da v4.0...
    if not ABUSEIPDB_KEY: return {}
    url = 'https://api.abuseipdb.com/api/v2/check'; params = {'ipAddress': ip_address}; headers = {'Key': ABUSEIPDB_KEY, 'Accept': 'application/json'}
    r = requests.get(url, headers=headers, params=params, timeout=5 )
    return {} if r.status_code == 429 else r.json().get("data", {})

def get_reverse_dns(ip_address):
    try: return socket.gethostbyaddr(ip_address)[0]
    except (socket.herror, Exception): return None

def get_open_ports(ip_address):
    try:
        nm = nmap.PortScanner(); nm.scan(ip_address, arguments='-T4 -F')
        if ip_address in nm.all_hosts() and 'tcp' in nm[ip_address]:
            return ", ".join(str(p) for p in nm[ip_address]['tcp'].keys())
    except Exception: return None

# --- FUNÇÃO PRINCIPAL DE PROCESSAMENTO (AGORA COM LÓGICA DE CACHE) ---

def process_ip(ip):
    """Processa um único IP, com verificação de cache."""
    
    # 1. Verifica o cache no banco de dados
    cached_report = query_db_for_ip(ip)
    if cached_report:
        last_analyzed = datetime.fromisoformat(cached_report['last_analyzed_at'])
        if datetime.now() - last_analyzed < timedelta(days=CACHE_DURATION_DAYS):
            print(f"CACHE HIT: Usando dados do banco para o IP {ip} (análise recente).")
            return # Retorna nada, pois não há nova análise

    # 2. Se não houver cache ou o cache for antigo, faz a análise completa
    print(f"CACHE MISS: Analisando o IP {ip} com todas as fontes...")
    geo_data = get_ip_geolocation(ip)
    if "error" in geo_data:
        print(f"AVISO: Não foi possível analisar o IP {ip}. Erro: {geo_data['error']}")
        return

    abuse_data = get_abuseipdb_report(ip)
    hostname = get_reverse_dns(ip)
    open_ports = get_open_ports(ip)
    
    consolidated_report = {
        "IP": ip, "Hostname": hostname, "Portas Abertas (Comuns)": open_ports,
        "Pontuação de Abuso (%)": abuse_data.get('abuseConfidenceScore'),
        "Total de Denúncias": abuse_data.get('totalReports'), "País": geo_data.get('country'),
        "Cidade": geo_data.get('city'), "Provedor (ISP)": geo_data.get('isp'),
    }
    
    save_report_to_db(consolidated_report)
    time.sleep(1.1)

def display_report(report):
    """Formata e exibe um relatório de forma legível."""
    print("\n--- 🔎 RELATÓRIO DO BANCO DE DADOS ---")
    for key, value in report.items():
        # Formata a chave para ter um espaçamento uniforme
        print(f"{key:<25}: {value}")
    print("-------------------------------------\n")

# --- FLUXO PRINCIPAL COM ARGPARSE (ATUALIZADO) ---
if __name__ == "__main__":
    initialize_database()

    parser = argparse.ArgumentParser(description="IP Intelligence System v5.0 - Análise, Cache e Consulta.")
    # Grupo para garantir que apenas uma ação principal seja escolhida
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("-i", "--ip", help="Um único endereço de IP para analisar e salvar.")
    action_group.add_argument("-f", "--file", help="Caminho para um arquivo de texto com IPs para analisar e salvar.")
    action_group.add_argument("-q", "--query", help="Busca um IP no banco de dados local e exibe o resultado.")
    
    args = parser.parse_args()

    if args.query:
        # Modo de Consulta
        result = query_db_for_ip(args.query)
        if result:
            display_report(result)
        else:
            print(f"IP '{args.query}' não encontrado no banco de dados.")

    else:
        # Modo de Análise
        ips_to_analyze = []
        if args.ip:
            ips_to_analyze.append(args.ip)
        elif args.file:
            try:
                with open(args.file, 'r') as f:
                    ips_to_analyze = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"❌ ERRO: Arquivo '{args.file}' não encontrado."); exit()
        
        if ips_to_analyze:
            for ip in tqdm(ips_to_analyze, desc="Progresso Geral"):
                process_ip(ip)
            print("\n✅ Operação concluída! O banco de dados foi atualizado.")
        else:
            print("Nenhum IP válido para analisar.")
