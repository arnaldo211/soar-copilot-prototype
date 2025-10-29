# VERSÃO COM API GRATUITA (ip-api.com)
import requests
import json

def get_ip_geolocation(ip_address):
    print(f"\n⚡ [Ação] Consultando dados de geolocalização para o IP: {ip_address}...")
    url = f"http://ip-api.com/json/{ip_address}"
    try:
        response = requests.get(url )
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "fail":
            print(f"❌ ERRO: A API retornou uma falha. Mensagem: {data.get('message')}")
            return None
        return data
    except requests.exceptions.RequestException as e:
        print(f"❌ ERRO de comunicação com a API: {e}")
        return None
    except json.JSONDecodeError:
        print("❌ ERRO: Não foi possível decodificar a resposta da API.")
        return None

if __name__ == "__main__":
    target_ip = input("👨‍💻 [Analista] Por favor, insira o endereço de IP para análise: ")
    report = get_ip_geolocation(target_ip)
    if report:
        print("\n--- ✅ RELATÓRIO DE GEOLOCALIZAÇÃO ---")
        print(f"IP Analisado:    {report.get('query', 'N/A')}")
        print(f"País:            {report.get('country', 'N/A')} ({report.get('countryCode', 'N/A')})")
        print(f"Região/Estado:     {report.get('regionName', 'N/A')}")
        print(f"Cidade:          {report.get('city', 'N/A')}")
        print(f"CEP/Zip Code:    {report.get('zip', 'N/A')}")
        print(f"Latitude:        {report.get('lat', 'N/A')}")
        print(f"Longitude:       {report.get('lon', 'N/A')}")
        print(f"Provedor (ISP):  {report.get('isp', 'N/A')}")
        print(f"Organização:     {report.get('org', 'N/A')}")
        print("-------------------------------------\n")
    else:
        print("\n❌ Não foi possível gerar o relatório para o IP informado.")
