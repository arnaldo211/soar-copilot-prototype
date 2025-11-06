# main.py - VERSÃO 13.0 (CORRIGIDO E CENTRALIZADO)
import argparse
from tqdm import tqdm

# Importa TODA a lógica de negócio do nosso módulo centralizado
import logic

# --- FUNÇÕES DE EXIBIÇÃO (ESPECÍFICAS PARA A LINHA DE COMANDO) ---

def display_external_report(report):
    """Formata e exibe um relatório de análise externa de forma legível."""
    print("\n--- 🔎 RELATÓRIO DO BANCO DE DADOS ---")
    for key, value in report.items():
        print(f"{key:<25}: {value}")
    print("-------------------------------------\n")

def display_internal_report(report):
    """Formata e exibe um relatório de análise interna de forma legível."""
    print(f"\n[+] Resultados para o IP: {report.get('ip')}")
    print(f"  - Portas Abertas e Serviços: {report.get('open_ports_details', 'N/A')}")
    
    recommendations = report.get('security_recommendations', [])
    if isinstance(recommendations, list) and recommendations:
        print("  - 🚨 Recomendações de Segurança:")
        for rec in recommendations:
            print(f"    - Porta {rec['service']}: Risco {rec['risk']} - {rec['details']}")
    elif isinstance(recommendations, str):
         print(f"  - ✅ {recommendations}")

# --- FLUXO PRINCIPAL COM ARGPARSE ---
if __name__ == "__main__":
    # Garante que o banco de dados exista ao iniciar a ferramenta
    logic.initialize_database()

    parser = argparse.ArgumentParser(description="IP Intelligence System v13.0 - Análise Externa e Interna.")
    
    # Grupo para ações principais
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("-i", "--ip", help="Um único endereço de IP para analisar.")
    action_group.add_argument("-f", "--file", help="Caminho para um arquivo de texto com IPs para analisar.")
    action_group.add_argument("-q", "--query", help="Busca um IP no banco de dados local e exibe o resultado.")
    
    # Argumento opcional para o modo de análise
    parser.add_argument("--internal", action='store_true', help="Ativa o modo de análise de segurança interna.")
    
    args = parser.parse_args()

    if args.query:
        # Modo de Consulta
        result = logic.get_report_from_db(args.query)
        if result:
            display_external_report(result)
        else:
            print(f"IP '{args.query}' não encontrado no banco de dados.")

    elif args.ip or args.file:
        # Modo de Análise (Interna ou Externa)
        ips_to_analyze = []
        if args.ip:
            ips_to_analyze.append(args.ip)
        elif args.file:
            try:
                with open(args.file, 'r') as f:
                    ips_to_analyze = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"❌ ERRO: Arquivo '{args.file}' não encontrado."); exit()
        
        if not ips_to_analyze:
            print("Nenhum IP válido para analisar."); exit()

        if args.internal:
            # --- MODO DE ANÁLISE INTERNA ---
            print(f"\n--- 🕵️  RELATÓRIO DE ANÁLISE DE SEGURANÇA INTERNA ---")
            for ip in ips_to_analyze:
                report = logic.analyze_ip_internal(ip)
                display_internal_report(report)
        else:
            # --- MODO DE ANÁLISE EXTERNA ---
            print(f"\n🔍 Analisando {len(ips_to_analyze)} IPs e salvando no banco de dados...")
            for ip in tqdm(ips_to_analyze, desc="Progresso Geral"):
                if not logic.is_cache_valid(ip):
                    tqdm.write(f"CACHE MISS: Analisando o IP {ip} com todas as fontes...")
                    analysis_result = logic.analyze_ip_external(ip)
                    if "error" in analysis_result:
                        tqdm.write(f"AVISO: Não foi possível analisar o IP {ip}. Erro: {analysis_result['error']}")
                    else:
                        logic.save_to_db(analysis_result)
                else:
                    tqdm.write(f"CACHE HIT: Usando dados do banco para o IP {ip} (análise recente).")
            print("\n✅ Operação concluída! O banco de dados foi atualizado.")
    else:
        parser.print_help()

