import requests
import json
import csv
import time
import socket
import argparse # Biblioteca para argumentos de linha de comando
from tqdm import tqdm
from dotenv import load_dotenv
import os
import nmap # Biblioteca para o Port Scan

# --- CARREGAMENTO DE CONFIGURAÇÕES ---
load_dotenv()
ABUSEIPDB_KEY = os.environ.get("ABUSEIPDB_API_KEY")

# --- FUNÇÕES DE ENRIQUECIMENTO DE DADOS ---

def get_ip_geolocation(ip_address):
    """Consulta a API 'ip-api.com' para obter dados de geolocalização."""
    url = f"http://ip-api.com/json/{ip_address}"
    try:
        response = requests.get(url, timeout=5 )
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "fail":
            return {"error": data.get("message", "IP inválido")}
        return data
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro de conexão (ip-api): {e}"}

def get_abuseipdb_report(ip_address):
    """Consulta a API do AbuseIPDB para obter a pontuação de risco."""
    if not ABUSEIPDB_KEY:
        return {"abuseConfidenceScore": "N/A (Chave não configurada)"}
    
    url = 'https://api.abuseipdb.com/api/v2/check'
    params = {'ipAddress': ip_address, 'maxAgeInDays': '90'}
    headers = {'Accept': 'application/json', 'Key': ABUSEIPDB_KEY}
    try:
        response = requests.get(url=url, headers=headers, params=params, timeout=5 )
        if response.status_code == 429: # Rate Limit
            return {"abuseConfidenceScore": "N/A (Rate Limit)"}
        response.raise_for_status()
        return response.json().get("data", {})
    except requests.exceptions.RequestException:
        return {"abuseConfidenceScore": "N/A (Erro de Conexão)"}

def get_reverse_dns(ip_address):
    """Tenta encontrar o hostname associado a um IP."""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        return hostname
    except socket.herror:
        return "N/A" # Não encontrado
    except Exception:
        return "Erro"

def get_open_ports(ip_address):
    """Realiza um scan rápido nas portas TCP mais comuns."""
    try:
        nm = nmap.PortScanner()
        # Scan rápido: -T4 (agressivo), -F (portas mais comuns)
        nm.scan(ip_address, arguments='-T4 -F')
        open_ports = []
        if ip_address in nm.all_hosts():
            if 'tcp' in nm[ip_address]:
                for port in nm[ip_address]['tcp'].keys():
                    open_ports.append(str(port))
        return ", ".join(open_ports) if open_ports else "Nenhuma porta comum aberta"
    except Exception:
        return "Erro no Scan"

# --- FUNÇÃO PRINCIPAL DE PROCESSAMENTO ---

def process_ips(ip_list):
    """Processa uma lista de IPs, consulta todas as fontes de dados e retorna os resultados."""
    results = []
    print(f"\n🔍 Analisando {len(ip_list)} IPs com todas as fontes de dados...")
    
    for ip in tqdm(ip_list, desc="Progresso da Análise"):
        geo_data = get_ip_geolocation(ip)
        
        # Se a geolocalização falhar (IP inválido), pulamos para o próximo
        if "error" in geo_data:
            consolidated_report = {"IP": ip, "Erro": geo_data["error"]}
            results.append(consolidated_report)
            continue

        abuse_data = get_abuseipdb_report(ip)
        hostname = get_reverse_dns(ip)
        open_ports = get_open_ports(ip)
        
        consolidated_report = {
            "IP": ip,
            "Hostname": hostname,
            "Portas Abertas (Comuns)": open_ports,
            "Pontuação de Abuso (%)": abuse_data.get('abuseConfidenceScore', 'N/A'),
            "Total de Denúncias": abuse_data.get('totalReports', 'N/A'),
            "País": geo_data.get('country', 'N/A'),
            "Cidade": geo_data.get('city', 'N/A'),
            "Provedor (ISP)": geo_data.get('isp', 'N/A'),
        }
        results.append(consolidated_report)
        time.sleep(1.1) # Pausa para não exceder o limite de taxa da API do AbuseIPDB

    return results

# --- FUNÇÕES DE SAÍDA ---

# NOVA VERSÃO CORRIGIDA DA FUNÇÃO save_to_csv
def save_to_csv(results, filename):
    """Salva os resultados em um arquivo CSV, lidando com cabeçalhos inconsistentes."""
    if not results: return

    # Define uma lista FIXA e COMPLETA de todos os cabeçalhos possíveis.
    # A ordem aqui define a ordem das colunas no CSV.
    all_possible_headers = [
        "IP",
        "Hostname",
        "Portas Abertas (Comuns)",
        "Pontuação de Abuso (%)",
        "Total de Denúncias",
        "País",
        "Cidade",
        "Provedor (ISP)",
        "Erro"  # O campo de erro agora está oficialmente na lista!
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        # Usamos nossa lista fixa de cabeçalhos.
        # O argumento 'extrasaction="ignore"' poderia ser usado para ignorar campos extras,
        # mas definir todos os cabeçalhos é mais robusto.
        writer = csv.DictWriter(f, fieldnames=all_possible_headers)
        
        # Escreve o cabeçalho no arquivo
        writer.writeheader()
        
        # Escreve todas as linhas de resultados
        writer.writerows(results)
        
    print(f"\n✅ Relatório salvo com sucesso em '{filename}'")

def save_to_json(results, filename):
    """Salva os resultados em um arquivo JSON."""
    if not results: return
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    print(f"\n✅ Relatório salvo com sucesso em '{filename}'")

# --- FLUXO PRINCIPAL COM ARGPARSE ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IP Analyzer Pro v3.0 - Ferramenta de Análise de IPs.")
    parser.add_argument("-i", "--ip", help="Um único endereço de IP para analisar.")
    parser.add_argument("-f", "--file", help="Caminho para um arquivo de texto contendo uma lista de IPs (um por linha).")
    parser.add_argument("-o", "--output", default="relatorio", help="Nome base do arquivo de saída (sem a extensão). Padrão: 'relatorio'.")
    parser.add_argument("--format", default="csv", choices=['csv', 'json'], help="Formato do arquivo de saída: 'csv' ou 'json'. Padrão: 'csv'.")
    
    args = parser.parse_args()

    ips_to_analyze = []
    if args.ip:
        ips_to_analyze.append(args.ip)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                ips_to_analyze = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ ERRO: Arquivo '{args.file}' não encontrado.")
            exit()
    else:
        print("❌ ERRO: Você deve fornecer um IP (-i) ou um arquivo de IPs (-f).")
        parser.print_help()
        exit()

    if ips_to_analyze:
        final_results = process_ips(ips_to_analyze)
        
        output_filename = f"{args.output}.{args.format}"
        
        if args.format == 'csv':
            save_to_csv(final_results, output_filename)
        elif args.format == 'json':
            save_to_json(final_results, output_filename)

