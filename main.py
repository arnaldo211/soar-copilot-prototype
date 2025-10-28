import os
import requests
import json
from dotenv import load_dotenv
# Importa a nova biblioteca da OpenAI
from openai import OpenAI

# Carrega as chaves de API do arquivo .env
load_dotenv()
try:
    ABUSEIPDB_KEY = os.environ["ABUSEIPDB_API_KEY"]
    # Configura o cliente da OpenAI com a chave do .env
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    print("✅ Autenticação com OpenAI e AbuseIPDB bem-sucedida!")
except KeyError:
    print("❌ ERRO: Verifique se OPENAI_API_KEY e ABUSEIPDB_API_KEY estão no seu arquivo .env")
    exit()

# --- FUNÇÕES DO COPILOT ---

def get_ai_suggestion(ip_address):
    """Pede ao modelo de IA da OpenAI para analisar a situação e sugerir o próximo passo."""
    
    print(f"\n🤖 [Copilot] Analisando o IP: {ip_address}...")

    # O prompt é o mesmo, mas a forma de enviar é diferente
    prompt = f"""
    Você é um SOAR-Copilot, um assistente de IA para analistas de cibersegurança.
    Sua tarefa é raciocinar sobre um incidente e sugerir a próxima ação LÓGICA em um formato que um script possa entender.

    INCIDENTE: Um alerta de atividade suspeita foi gerado para o endereço de IP: {ip_address}.

    PERGUNTA: Qual é a próxima ação recomendada para investigar este IP?

    Responda APENAS com um objeto JSON. A ação deve ser consultar uma base de dados de Threat Intelligence.
    Exemplo de resposta:
    {{
        "action": "query_threat_intelligence",
        "parameters": {{
            "service": "abuseipdb",
            "ip_address": "{ip_address}"
        }}
    }}
    """
    
    try:
        # Chamada para a API da OpenAI
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo", # Modelo rápido e eficiente
            temperature=0.1, # Baixa temperatura para respostas mais diretas e menos criativas
        )
        
        # Extrai a resposta do modelo
        ai_response_text = chat_completion.choices[0].message.content
        
        # Limpa e converte a resposta para JSON
        cleaned_response = ai_response_text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response)
        
    except Exception as e:
        print(f"❌ ERRO ao comunicar com a IA (OpenAI): {e}")
        return None

def query_abuseipdb(ip_address):
    """Executa a ação de consultar o AbuseIPDB."""
    print(f"⚡ [Ação] Consultando o AbuseIPDB para o IP {ip_address}...")
    url = 'https://api.abuseipdb.com/api/v2/check'
    params = {'ipAddress': ip_address, 'maxAgeInDays': '90'}
    headers = {'Accept': 'application/json', 'Key': ABUSEIPDB_KEY}
    try:
        response = requests.get(url=url, headers=headers, params=params )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO ao consultar o AbuseIPDB: {e}")
        return None

# --- FLUXO PRINCIPAL ---
if __name__ == "__main__":
    target_ip = input("👨‍💻 [Analista] Por favor, insira o endereço de IP suspeito: ")
    suggestion = get_ai_suggestion(target_ip)

    if suggestion and suggestion.get("action") == "query_threat_intelligence":
        ip_to_check = suggestion["parameters"]["ip_address"]
        report = query_abuseipdb(ip_to_check)

        if report and "data" in report:
            data = report["data"]
            print("\n--- RELATÓRIO FINAL ---")
            print(f"✅ Sucesso! Relatório gerado.")
            print(f"IP: {data['ipAddress']}")
            print(f"País: {data.get('countryCode', 'N/A')}")
            print(f"Domínio: {data.get('domain', 'N/A')}")
            print(f"Provedor: {data.get('isp', 'N/A')}")
            print(f"Pontuação de Confiança de Abuso (0-100): {data['abuseConfidenceScore']}%")
            print(f"Total de Denúncias: {data['totalReports']}")
            print("-----------------------\n")
        else:
            print("❌ Não foi possível gerar o relatório do AbuseIPDB.")
    else:
        print("❌ O Copilot não conseguiu sugerir uma ação válida.")


