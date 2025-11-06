# api.py - VERSÃO 13.0 (CORRIGIDO E UNIFICADO)
import os
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Importa TODAS as funções necessárias do nosso módulo de lógica centralizado
from logic import (
    initialize_database,
    is_cache_valid,
    get_report_from_db,
    save_to_db,
    analyze_ip_external,
    analyze_ip_internal
)

# --- CONFIGURAÇÃO INICIAL DA APLICAÇÃO ---

load_dotenv() # Carrega as variáveis do .env
API_KEY = os.environ.get("API_SECRET_KEY")

# Cria a aplicação Flask
app = Flask(__name__)
CORS(app) # Habilita o CORS para permitir que o front-end acesse a API

# Garante que o banco de dados exista ao iniciar a API
initialize_database()

# --- DECORADOR DE AUTENTICAÇÃO ---

def require_api_key(f):
    """Um decorador para proteger endpoints que exigem uma chave de API."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if not API_KEY or provided_key != API_KEY:
            app.logger.warning(f"Acesso não autorizado negado. IP: {request.remote_addr}")
            return jsonify({"error": "Acesso não autorizado. Chave de API inválida ou ausente."}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- DEFINIÇÃO DOS ENDPOINTS DA API ---

@app.route('/')
def index():
    """Endpoint principal para verificar se a API está no ar."""
    return "<h1>IP Intelligence Service v13.0</h1><p>API está online.</p>"

@app.route('/query/<string:ip>', methods=['GET'])
@require_api_key
def query_ip_endpoint(ip):
    """Endpoint para buscar um IP no banco de dados. Ex: /query/8.8.8.8"""
    app.logger.info(f"Recebida requisição GET para /query/{ip}")
    report = get_report_from_db(ip)
    if report:
        return jsonify(report)
    else:
        return jsonify({"error": "IP não encontrado no banco de dados"}), 404

@app.route('/analyze', methods=['POST'])
@require_api_key
def analyze_ips_external_endpoint():
    """Endpoint para solicitar a análise EXTERNA de um ou mais IPs."""
    data = request.get_json()
    if not data or 'ips' not in data or not isinstance(data['ips'], list):
        return jsonify({"error": "Requisição inválida. Forneça um JSON com uma chave 'ips' contendo uma lista."}), 400

    ips = data['ips']
    app.logger.info(f"Recebida requisição POST para /analyze (externo) com {len(ips)} IPs.")
    
    results_summary = []
    for ip in ips:
        if is_cache_valid(ip):
            results_summary.append({"status": "cached", "ip": ip})
        else:
            analysis_result = analyze_ip_external(ip)
            if "error" in analysis_result:
                app.logger.error(f"Erro ao analisar {ip}: {analysis_result['error']}")
                results_summary.append({"status": "error", "ip": ip, "message": analysis_result['error']})
            else:
                save_to_db(analysis_result)
                results_summary.append({"status": "analyzed", "ip": ip})
                
    return jsonify({"analysis_summary": results_summary})

@app.route('/analyze/internal', methods=['POST'])
@require_api_key
def analyze_ips_internal_endpoint():
    """Endpoint para análise de segurança INTERNA de um ou mais IPs."""
    data = request.get_json()
    if not data or 'ips' not in data or not isinstance(data['ips'], list):
        return jsonify({"error": "Requisição inválida. Forneça um JSON com uma chave 'ips' contendo uma lista."}), 400

    ips = data['ips']
    app.logger.info(f"Recebida requisição POST para /analyze/internal com {len(ips)} IPs.")

    results = []
    for ip in ips:
        report = analyze_ip_internal(ip)
        results.append(report)
    
    return jsonify(results)

# --- EXECUÇÃO DO SERVIDOR ---

if __name__ == '__main__':
    # host='0.0.0.0' faz com que a API seja acessível de fora do contêiner Docker
    app.run(host='0.0.0.0', port=5000, debug=True)

