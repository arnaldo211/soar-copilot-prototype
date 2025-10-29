import requests
import json
import csv
import time
from tqdm import tqdm # Importa a biblioteca de barra de progresso
from dotenv import load_dotenv
import os

# Carrega a chave da API do AbuseIPDB do arquivo .env
load_dotenv()
try:
    ABUSEIPDB_KEY = os.environ["ABUSEIPDB_API_KEY"]
except KeyError:
    # Se a chave não for encontrada, o programa ainda pode funcionar, mas sem a pontuação de risco.
    print("⚠️  Aviso: Chave ABUSEIPDB_API_KEY não encontrada no arquivo .env. A análise de reputação será pulada.")
    ABUSEIPDB_KEY = None

# --- FUNÇÕES DE CONSULTA DAS APIS ---

def get_ip_geolocation(ip_address):
    """Consulta a API 'ip-api.com' para obter dados de geolocalização."""
    url = f"http://ip-api.com/json/{ip_address}"
    try:
        response = requests.get(url )
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "fail":
            return {"error": data.get("message", "IP inválido ou privado")}
        return data
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro de conexão com ip-api: {e}"}

def get_abuseipdb_report(ip_address):
    """Consulta a API do AbuseIPDB para obter a pontuação de risco."""
    if not ABUSEIPDB_KEY:
        return {"abuseConfidenceScore": "N/A"} # Retorna N/A se a chave não estiver configurada

    url = 'https://api.abuseipdb.com/api/v2/check'
    params = {'ipAddress': ip_address, 'maxAgeInDays': '90'}
    headers = {'Accept': 'application/json', 'Key': ABUSEIPDB_KEY}
    try:
        response = requests.get(url=url, headers=headers, params=params )
        response.raise_for_status()
        data = response.json().get("data", {})
        return data
    except requests.exceptions.RequestException:
        # Limite de taxa da API é de 1 requisição por segundo. Vamos esperar e tentar de novo.
        time.sleep(1) 
        return {"abuseConfidenceScore": "Rate Limited"}


# --- FUNÇÃO PRINCIPAL DE PROCESSAMENTO ---

def process_ips(ip_list):
    """Processa uma lista de IPs, consulta as APIs e retorna os resultados consolidados."""
    results = []
    print(f"\n🔍 Analisando {len(ip_list)} IPs...")
    
    # A barra de progresso (tqdm) envolve a lista de IPs
    for ip in tqdm(ip_list, desc="Progresso da Análise"):
        geo_data = get_ip_geolocation(ip)
        abuse_data = get_abuseipdb_report(ip)
        
        # Consolida os resultados de ambas as APIs em um único dicionário
        consolidated_report = {
            "IP": ip,
            "País": geo_data.get('country', 'N/A'),
            "Cidade": geo_data.get('city', 'N/A'),
            "Provedor (ISP)": geo_data.get('isp', 'N/A'),
            "Pontuação de Abuso (%)": abuse_data.get('abuseConfidenceScore', 'N/A'),
            "Total de Denúncias": abuse_data.get('totalReports', 'N/A'),
            "Erro": geo_data.get("error") # Adiciona um campo de erro, se houver
        }
        results.append(consolidated_report)
        time.sleep(1.1) # Pausa para não exceder o limite de taxa das APIs

    return results

def save_to_csv(results, filename="relatorio_ips.csv"):
    """Salva uma lista de resultados em um arquivo CSV."""
    if not results:
        print("Nenhum resultado para salvar.")
        return

    # Pega os cabeçalhos do primeiro resultado
    headers = results[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ Relatório salvo com sucesso em '{filename}'")


# --- FLUXO PRINCIPAL DO PROGRAMA ---
if __name__ == "__main__":
    print("--- 🕵️  Analisador de IPs v2.0 ---")
    print("1: Analisar um único IP")
    print("2: Analisar uma lista de IPs de um arquivo (ex: ips_para_analise.txt)")
    
    choice = input("Escolha uma opção (1 ou 2): ")

    ips_to_analyze = []

    if choice == '1':
        single_ip = input("👨‍💻 Por favor, insira o endereço de IP para análise: ")
        if single_ip:
            ips_to_analyze.append(single_ip)
    elif choice == '2':
        filename = input("📂 Por favor, insira o nome do arquivo de texto: ")
        try:
            with open(filename, 'r') as f:
                # Lê cada linha, remove espaços em branco e ignora linhas vazias
                ips_to_analyze = [line.strip() for line in f if line.strip()]
            if not ips_to_analyze:
                 print(f"❌ Arquivo '{filename}' está vazio ou não contém IPs válidos.")
        except FileNotFoundError:
            print(f"❌ ERRO: Arquivo '{filename}' não encontrado.")
    else:
        print("Opção inválida. Encerrando o programa.")

    if ips_to_analyze:
        final_results = process_ips(ips_to_analyze)
        save_to_csv(final_results)


