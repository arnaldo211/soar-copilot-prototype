# logic.py - VERSÃO 14.0 (com PostgreSQL)
import requests
import time
import socket
import nmap
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import psycopg2
import psycopg2.extras

# --- CONFIGURAÇÕES E CONSTANTES ---
load_dotenv()
ABUSEIPDB_KEY = os.environ.get("ABUSEIPDB_KEY")
CACHE_DURATION_DAYS = 7

# Credenciais do Banco de Dados (do .env)
DB_HOST = "db" # O nome do serviço no docker-compose.yml
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

SECURITY_RECOMMENDATIONS = {
    21: {"service": "FTP", "risk": "Alto", "details": "FTP não é criptografado. Credenciais e dados podem ser interceptados. Considere usar SFTP (porta 22)."},
    23: {"service": "Telnet", "risk": "Crítico", "details": "Telnet não é criptografado. Sessões inteiras podem ser capturadas. Desabilite e use SSH (porta 22)."},
    80: {"service": "HTTP", "risk": "Médio", "details": "HTTP não é criptografado. O tráfego pode ser interceptado. Implemente HTTPS (porta 443)."},
    # ... (outras recomendações)
}

# --- FUNÇÕES DE GERENCIAMENTO DO BANCO DE DADOS (PostgreSQL) ---

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados PostgreSQL."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def initialize_database():
    """Cria a tabela 'reports' se ela não existir."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id SERIAL PRIMARY KEY,
            ip TEXT UNIQUE NOT NULL,
            hostname TEXT,
            open_ports TEXT,
            abuse_score INTEGER,
            total_reports INTEGER,
            country TEXT,
            city TEXT,
            isp TEXT,
            last_analyzed_at TIMESTAMPTZ NOT NULL
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def save_to_db(report):
    """Salva ou atualiza um relatório no banco de dados PostgreSQL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        INSERT INTO reports (ip, hostname, open_ports, abuse_score, total_reports, country, city, isp, last_analyzed_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ip) DO UPDATE SET
            hostname = EXCLUDED.hostname,
            open_ports = EXCLUDED.open_ports,
            abuse_score = EXCLUDED.abuse_score,
            total_reports = EXCLUDED.total_reports,
            country = EXCLUDED.country,
            city = EXCLUDED.city,
            isp = EXCLUDED.isp,
            last_analyzed_at = EXCLUDED.last_analyzed_at;
    '''
    values = (
        report.get("ip"), report.get("hostname"), report.get("open_ports"),
        report.get("abuse_score"), report.get("total_reports"), report.get("country"),
        report.get("city"), report.get("isp"), datetime.now()
    )
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

# NOVA VERSÃO da função get_report_from_db em logic.py

def get_report_from_db(ip):
    """Busca um relatório de IP no banco de dados e mapeia para as chaves do front-end."""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM reports WHERE ip = %s;", (ip,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not result:
        return None
        
    # Mapeia os nomes das colunas do banco (ex: 'abuse_score')
    # para as chaves que o front-end espera (ex: 'abuse_score').
    # Isso garante consistência.
    report = {
        'id': result['id'],
        'ip': result['ip'],
        'hostname': result['hostname'],
        'open_ports': result['open_ports'],
        'abuse_score': result['abuse_score'],
        'total_reports': result['total_reports'],
        'country': result['country'],
        'city': result['city'],
        'isp': result['isp'],
        'last_analyzed_at': result['last_analyzed_at'].isoformat() if result['last_analyzed_at'] else None
    }
    return report

# NOVA E CORRIGIDA VERSÃO da função is_cache_valid em logic.py

def is_cache_valid(ip):
    """Verifica se o cache para um IP é recente e válido."""
    report = get_report_from_db(ip)
    if report and report.get('last_analyzed_at'):
        # Converte a string ISO de volta para um objeto datetime
        last_analyzed_str = report['last_analyzed_at']
        last_analyzed_aware = datetime.fromisoformat(last_analyzed_str)
        
        # CORREÇÃO: Remove a informação de fuso horário para a comparação
        last_analyzed_naive = last_analyzed_aware.replace(tzinfo=None)
        
        # Agora a comparação funciona, pois estamos comparando dois datetimes "naive"
        if datetime.now() - last_analyzed_naive < timedelta(days=CACHE_DURATION_DAYS):
            return True
    return False

# --- FUNÇÕES DE ANÁLISE (sem mudanças, apenas chamam as funções de DB corretas) ---

def analyze_ip_external(ip):
    """Executa a análise completa para um IP externo."""
    try:
        geo_data = requests.get(f"http://ip-api.com/json/{ip}", timeout=5 ).json()
        if geo_data.get('status') == 'fail':
            raise ValueError(geo_data.get('message', 'Falha na geolocalização'))

        abuse_data = {}
        if ABUSEIPDB_KEY:
            abuse_res = requests.get('https://api.abuseipdb.com/api/v2/check',
                                     headers={'Key': ABUSEIPDB_KEY, 'Accept': 'application/json'},
                                     params={'ipAddress': ip}, timeout=5 )
            if abuse_res.status_code == 200:
                abuse_data = abuse_res.json().get("data", {})

        hostname = None
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror):
            pass # Ignora falhas de DNS reverso

        open_ports = "Nenhuma"
        try:
            nm = nmap.PortScanner()
            nm.scan(ip, arguments='-T4 -F')
            if ip in nm.all_hosts() and 'tcp' in nm[ip]:
                ports = sorted(nm[ip]['tcp'].keys())
                open_ports = ", ".join(str(p) for p in ports)
        except Exception:
            pass # Ignora falhas no Nmap

        report = {
            "ip": ip, "hostname": hostname, "open_ports": open_ports,
            "abuse_score": abuse_data.get('abuseConfidenceScore', 0),
            "total_reports": abuse_data.get('totalReports', 0),
            "country": geo_data.get('country', 'N/A'), "city": geo_data.get('city', 'N/A'),
            "isp": geo_data.get('isp', 'N/A'),
        }
        save_to_db(report)
        report['status'] = 'analyzed'  # Adiciona o status ao relatório
        return report  # Retorna o relatório completo


    except Exception as e:
        return {"status": "error", "ip": ip, "message": str(e)}

def analyze_ip_internal(ip):
    """Executa uma análise de segurança focada em um IP interno."""
    try:
        nm = nmap.PortScanner()
        nm.scan(ip, arguments='-sV -T4')
        
        if ip not in nm.all_hosts():
            return {"ip": ip, "status": "Host inativo ou não respondeu ao scan."}

        open_ports_details = []
        recommendations = []
        
        if 'tcp' in nm[ip]:
            ports = sorted(nm[ip]['tcp'].keys())
            for port in ports:
                service_info = nm[ip]['tcp'][port]
                service_name = service_info.get('name', 'desconhecido')
                product = service_info.get('product', '')
                version = service_info.get('version', '')
                
                full_service = f"{service_name} ({product} {version})".strip()
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
