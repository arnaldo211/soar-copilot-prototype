# logic.py - VERSÃO 13.0 (CORRIGIDO E CENTRALIZADO)
import requests
import sqlite3
import time
import socket
import nmap
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# --- CONFIGURAÇÕES E CONSTANTES ---
load_dotenv()
ABUSEIPDB_KEY = os.environ.get("ABUSEIPDB_KEY")
DB_FILE = "ip_intelligence.db"
CACHE_DURATION_DAYS = 7

# Base de conhecimento de segurança para portas comuns
SECURITY_RECOMMENDATIONS = {
    21: {"service": "FTP", "risk": "Alto", "details": "FTP não é criptografado. Credenciais e dados podem ser interceptados. Considere usar SFTP (porta 22)."},
    23: {"service": "Telnet", "risk": "Crítico", "details": "Telnet não é criptografado. Sessões inteiras podem ser capturadas. Desabilite e use SSH (porta 22)."},
    25: {"service": "SMTP", "risk": "Informativo", "details": "Servidor de e-mail aberto. Verifique se está protegido contra relay aberto para evitar spam."},
    80: {"service": "HTTP", "risk": "Médio", "details": "HTTP não é criptografado. O tráfego pode ser interceptado. Implemente HTTPS (porta 443)."},
    110: {"service": "POP3", "risk": "Alto", "details": "POP3 não é criptografado para download de e-mails. Use POP3S (995) ou IMAPS (993)."},
    143: {"service": "IMAP", "risk": "Alto", "details": "IMAP não é criptografado. Use IMAPS (porta 993)."},
    3389: {"service": "RDP", "risk": "Crítico", "details": "RDP (Remote Desktop) exposto à internet é um alvo comum para ataques. Restrinja o acesso via VPN ou firewall."},
}

# --- FUNÇÕES DE GERENCIAMENTO DO BANCO DE DADOS ---

def initialize_database():
    """Cria a tabela do banco de dados se ela não existir."""
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

def save_to_db(report):
    """Salva um relatório de análise externa no banco de dados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    query = '''
        INSERT OR REPLACE INTO reports (ip, hostname, open_ports, abuse_score, total_reports, country, city, isp, last_analyzed_at)
        VALUES (:ip, :hostname, :open_ports, :abuse_score, :total_reports, :country, :city, :isp, :last_analyzed_at)
    '''
    report['last_analyzed_at'] = datetime.now()
    cursor.execute(query, report)
    conn.commit()
    conn.close()

def get_report_from_db(ip):
    """Busca um relatório completo de um IP no banco de dados."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE ip = ?", (ip,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def is_cache_valid(ip):
    """Verifica se existe um cache recente e válido para um IP."""
    report = get_report_from_db(ip)
    if report and 'last_analyzed_at' in report and report['last_analyzed_at']:
        try:
            last_analyzed = datetime.fromisoformat(report['last_analyzed_at'])
            if datetime.now() - last_analyzed < timedelta(days=CACHE_DURATION_DAYS):
                return True
        except (TypeError, ValueError):
            return False # Se a data estiver em formato inválido, considera o cache inválido
    return False

# --- FUNÇÕES DE ANÁLISE (EXTERNA E INTERNA) ---

def analyze_ip_external(ip):
    """Executa a análise completa para um IP externo, coletando dados de várias fontes."""
    try:
        # Geolocalização
        geo_res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5 )
        geo_res.raise_for_status()
        geo_data = geo_res.json()
        if geo_data.get('status') == 'fail':
            raise ValueError(f"Geolocalização falhou: {geo_data.get('message', 'erro desconhecido')}")

        # AbuseIPDB
        abuse_data = {}
        if ABUSEIPDB_KEY:
            abuse_res = requests.get(
                'https://api.abuseipdb.com/api/v2/check',
                headers={'Key': ABUSEIPDB_KEY, 'Accept': 'application/json'},
                params={'ipAddress': ip},
                timeout=5
             )
            if abuse_res.status_code == 200:
                abuse_data = abuse_res.json().get("data", {})
            # Adormece um pouco para não exceder o limite da API gratuita
            time.sleep(1.1)

        # DNS Reverso
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except (socket.herror, Exception):
            hostname = None

        # Port Scan
        open_ports = "Nenhuma"
        try:
            nm = nmap.PortScanner()
            nm.scan(ip, arguments='-T4 -F') # Scan rápido das portas mais comuns
            if ip in nm.all_hosts() and 'tcp' in nm[ip]:
                ports = nm[ip]['tcp'].keys()
                if ports:
                    open_ports = ", ".join(map(str, sorted(ports)))
        except Exception:
            pass # Se o nmap falhar, apenas continua com "Nenhuma"

        return {
            "ip": ip,
            "hostname": hostname,
            "open_ports": open_ports,
            "abuse_score": abuse_data.get('abuseConfidenceScore', 0),
            "total_reports": abuse_data.get('totalReports', 0),
            "country": geo_data.get('country', 'N/A'),
            "city": geo_data.get('city', 'N/A'),
            "isp": geo_data.get('isp', 'N/A'),
        }
    except Exception as e:
        return {"ip": ip, "error": str(e)}

def analyze_ip_internal(ip):
    """Executa uma análise de segurança focada em um IP interno."""
    try:
        nm = nmap.PortScanner()
        # -sV tenta detectar a versão do serviço, -T4 é um template de timing agressivo
        nm.scan(ip, arguments='-sV -T4')
        
        if ip not in nm.all_hosts():
            return {"ip": ip, "status": "Host inativo ou não respondeu ao scan."}

        open_ports_details = []
        recommendations = []
        
        if 'tcp' in nm[ip]:
            for port in sorted(nm[ip]['tcp'].keys()): # Ordena as portas para consistência
                service_info = nm[ip]['tcp'][port]
                service_name = service_info.get('name', 'desconhecido')
                product = service_info.get('product', '')
                version = service_info.get('version', '')
                
                full_service = f"{service_name} ({product} {version})".strip().replace("()", "")
                open_ports_details.append(f"{port}/tcp - {full_service}")
                
                if port in SECURITY_RECOMMENDATIONS:
                    recommendations.append(SECURITY_RECOMMENDATIONS[port])

        return {
            "ip": ip,
            "open_ports_details": ", ".join(open_ports_details) if open_ports_details else "Nenhuma porta TCP aberta encontrada.",
            "security_recommendations": recommendations if recommendations else "Nenhuma recomendação de segurança automática para as portas encontradas."
        }
    except Exception as e:
        return {"ip": ip, "error": f"Erro na análise interna: {e}"}

