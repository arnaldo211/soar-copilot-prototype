# api.py
from flask import Flask, jsonify, request
# Importa as funções do nosso outro arquivo
import logic 

# Cria a aplicação Flask
app = Flask(__name__)

# Garante que o banco de dados exista ao iniciar a API
logic.initialize_database()

# --- DEFINIÇÃO DOS ENDPOINTS DA API ---

@app.route('/')
def index():
    """Endpoint principal para verificar se a API está no ar."""
    return "<h1>IP Intelligence Service v6.0</h1><p>API está online. Use os endpoints /query/&lt;ip&gt; ou /analyze.</p>"

@app.route('/query/<string:ip>', methods=['GET'])
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
