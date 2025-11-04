# api.py
import os
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import logic

load_dotenv() # Carrega as variáveis do .env

API_KEY = os.environ.get("API_SECRET_KEY")

# Decorador para proteger os endpoints
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se a chave foi enviada no cabeçalho 'X-API-Key'
        provided_key = request.headers.get('X-API-Key')
        if not API_KEY or provided_key != API_KEY:
            # Se a chave estiver errada ou não for fornecida, retorna erro 401
            return jsonify({"error": "Acesso não autorizado. Chave de API inválida ou ausente."}), 401
        # Se a chave estiver correta, executa a função do endpoint
        return f(*args, **kwargs)
    return decorated_function

# api.py
from flask import Flask, jsonify, request
# Importa as funções do nosso outro arquivo
import logic 

# Cria a aplicação Flask
app = Flask(__name__)
CORS(app)

# Garante que o banco de dados exista ao iniciar a API
logic.initialize_database()

# --- DEFINIÇÃO DOS ENDPOINTS DA API ---

@app.route('/')
@require_api_key
def index():
    """Endpoint principal para verificar se a API está no ar."""
    return "<h1>IP Intelligence Service v6.0</h1><p>API está online. Use os endpoints /query/&lt;ip&gt; ou /analyze.</p>"

@app.route('/query/<string:ip>', methods=['GET'])
@require_api_key
def query_ip(ip):
    """Endpoint para buscar um IP no banco de dados. Ex: /query/8.8.8.8"""
    print(f"INFO: Recebida requisição GET para /query/{ip}")
    
    report = logic.query_db_for_ip(ip)
    
    if report:
        # jsonify converte o dicionário Python para uma resposta JSON
        return jsonify(report)
    else:
        # Retorna um erro 404 (Not Found) se o IP não estiver no banco
        return jsonify({"error": "IP não encontrado no banco de dados"}), 404

@app.route('/analyze', methods=['POST'])
@require_api_key
def analyze_ips():
    """Endpoint para solicitar a análise de um ou mais IPs."""
    print("INFO: Recebida requisição POST para /analyze")
    
    # Pega os dados JSON enviados na requisição
    data = request.get_json()
    
    if not data or 'ips' not in data:
        return jsonify({"error": "Requisição inválida. Forneça um JSON com uma chave 'ips' contendo uma lista de endereços de IP."}), 400

    ips_to_analyze = data['ips']
    if not isinstance(ips_to_analyze, list):
        return jsonify({"error": "'ips' deve ser uma lista."}), 400
        
    results = []
    for ip in ips_to_analyze:
        result = logic.process_ip(ip)
        results.append(result)
        
    return jsonify({"analysis_summary": results})

# --- EXECUÇÃO DO SERVIDOR ---

if __name__ == '__main__':
    # Roda o servidor Flask. debug=True faz com que ele reinicie automaticamente quando você salva o arquivo.
    # host='0.0.0.0' faz com que ele seja acessível de fora do 'localhost' (útil em alguns ambientes)
    app.run(host='0.0.0.0', port=5000, debug=True)
