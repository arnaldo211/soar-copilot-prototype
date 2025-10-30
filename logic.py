# logic.py
import requests
import sqlite3
import time
import socket
import nmap
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
ABUSEIPDB_KEY = os.environ.get("ABUSEIPDB_KEY")
DB_FILE = "ip_intelligence.db"
CACHE_DURATION_DAYS = 7

def initialize_database():
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, ip TEXT UNIQUE, hostname TEXT, open_ports TEXT, abuse_score INTEGER, total_reports INTEGER, country TEXT, city TEXT, isp TEXT, last_analyzed_at TIMESTAMP)''')
    conn.commit(); conn.close()

def save_report_to_db(report):
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    query = '''INSERT OR REPLACE INTO reports (ip, hostname, open_ports, abuse_score, total_reports, country, city, isp, last_analyzed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    values = (report.get("IP"), report.get("Hostname"), report.get("Portas Abertas (Comuns)"), report.get("Pontuação de Abuso (%)"), report.get("Total de Denúncias"), report.get("País"), report.get("Cidade"), report.get("Provedor (ISP)"), datetime.now())
    cursor.execute(query, values); conn.commit(); conn.close()

def query_db_for_ip(ip):
    conn = sqlite3.connect(DB_FILE); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE ip = ?", (ip,)); result = cursor.fetchone(); conn.close()
    return dict(result) if result else None

def get_ip_geolocation(ip):
    url = f"http://ip-api.com/json/{ip}"; r = requests.get(url, timeout=5 ); r.raise_for_status(); data = r.json()
    return {"error": data.get("message")} if data.get("status") == "fail" else data

def get_abuseipdb_report(ip):
    if not ABUSEIPDB_KEY: return {}
    url = 'https://api.abuseipdb.com/api/v2/check'; params = {'ipAddress': ip}; headers = {'Key': ABUSEIPDB_KEY, 'Accept': 'application/json'}
    r = requests.get(url, headers=headers, params=params, timeout=5 )
    return {} if r.status_code == 429 else r.json().get("data", {})

def get_reverse_dns(ip):
    try: return socket.gethostbyaddr(ip)[0]
    except (socket.herror, Exception): return None

def get_open_ports(ip):
    try:
        nm = nmap.PortScanner(); nm.scan(ip, arguments='-T4 -F')
        if ip in nm.all_hosts() and 'tcp' in nm[ip_address]:
            return ", ".join(str(p) for p in nm[ip_address]['tcp'].keys())
    except Exception: return None

def process_ip(ip):
    cached_report = query_db_for_ip(ip)
    if cached_report:
        last_analyzed = datetime.fromisoformat(cached_report['last_analyzed_at'])
        if datetime.now() - last_analyzed < timedelta(days=CACHE_DURATION_DAYS):
            return {"status": "cached", "ip": ip, "message": "Dados recentes encontrados no cache do banco de dados."}
    
    geo_data = get_ip_geolocation(ip)
    if "error" in geo_data: return {"status": "error", "ip": ip, "message": geo_data['error']}
    
    abuse_data = get_abuseipdb_report(ip)
    hostname = get_reverse_dns(ip)
    open_ports = get_open_ports(ip)
    
    report = {
        "IP": ip, "Hostname": hostname, "Portas Abertas (Comuns)": open_ports,
        "Pontuação de Abuso (%)": abuse_data.get('abuseConfidenceScore'), "Total de Denúncias": abuse_data.get('totalReports'),
        "País": geo_data.get('country'), "Cidade": geo_data.get('city'), "Provedor (ISP)": geo_data.get('isp'),
    }
    save_report_to_db(report)
    time.sleep(1.1)
    return {"status": "analyzed", "ip": ip, "message": "Análise concluída e salva no banco de dados."}
