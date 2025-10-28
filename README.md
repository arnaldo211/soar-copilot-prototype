# SOAR-Copilot: Protótipo de Assistente de IA para Resposta a Incidentes

![Cybersecurity AI Banner](https://i.imgur.com/e3sYn0Y.png )

## 📖 Visão Geral

O **SOAR-Copilot** é um protótipo funcional de uma ferramenta de cibersegurança com foco em **Blue Team**. Ele simula um assistente de IA que auxilia analistas de segurança a automatizar os primeiros passos da resposta a um incidente.

A ferramenta recebe um endereço de IP suspeito, utiliza um Modelo de Linguagem Grande (LLM) para raciocinar sobre o próximo passo investigativo e, em seguida, executa essa ação de forma autônoma, consultando a API do **AbuseIPDB** para coletar informações de ameaças.

Este projeto demonstra habilidades em:
- **Automação de Segurança (SOAR):** Orquestração de ferramentas e processos.
- **Integração de APIs:** Conexão com serviços de IA (OpenAI) e Threat Intelligence (AbuseIPDB).
- **Desenvolvimento em Python:** Criação de scripts robustos e modulares para cibersegurança.
- **Gerenciamento de Credenciais:** Uso de variáveis de ambiente para proteger segredos.

---

## ⚙️ Como Funciona

O fluxo de trabalho do Copilot é simples e poderoso:

1.  **Entrada do Analista:** O script solicita ao analista um endereço de IP suspeito.
2.  **Raciocínio com IA:** O IP é enviado para um modelo de IA (GPT-3.5-Turbo) com um prompt específico, pedindo que ele sugira a próxima ação lógica em um formato JSON estruturado.
3.  **Ação Automatizada:** O script interpreta a resposta da IA e executa a ação sugerida, que neste caso é consultar a API do AbuseIPDB.
4.  **Relatório Final:** As informações coletadas do AbuseIPDB são formatadas e apresentadas ao analista, incluindo a pontuação de risco, país de origem e número de denúncias.

---

## 🚀 Como Executar

Para executar este projeto localmente, siga os passos abaixo.

### 1. Pré-requisitos

- Python 3.10 ou superior
- Git

### 2. Instalação

Primeiro, clone o repositório para a sua máquina:
```bash
git clone https://github.com/arnaldo211/soar-copilot-prototype.git
cd soar-copilot-prototype

Crie e ative um ambiente virtual:
Bash
python3 -m venv venv
source venv/bin/activate
Instale as dependências necessárias a partir do arquivo requirements.txt:
Bash
pip install -r requirements.txt
3. Configuração das Chaves de API
Este script requer chaves de API para os seguintes serviços:
OpenAI: Para a análise e sugestão de ações pela IA.
AbuseIPDB: Para consulta de reputação de IP.
Crie um arquivo chamado .env na raiz do projeto e adicione suas chaves:
Plain Text
OPENAI_API_KEY="sk-SUA_CHAVE_DA_OPENAI_AQUI"
ABUSEIPDB_API_KEY="SUA_CHAVE_DO_ABUSEIPDB_AQUI"
Nota Importante: Em Outubro de 2025, a API da OpenAI pode requerer a adição de um método de pagamento para ativar a cota de uso da API, mesmo para novas contas. O script só funcionará com uma chave de API que tenha uma cota ativa.
4. Execução
Com tudo configurado, execute o script:
Bash
python3 main.py
O programa solicitará um endereço de IP para iniciar a análise.
🔮 Próximos Passos e Evolução
Este protótipo é a base para uma ferramenta muito mais poderosa. As próximas etapas poderiam incluir:
 Adicionar Mais Ações: Integrar com outras APIs, como VirusTotal para análise de hashes ou Shodan para informações de hosts.
 Criar uma Interface Web: Desenvolver uma interface simples com Flask ou FastAPI para uma experiência de usuário mais rica.
 Automatizar o Bloqueio: Gerar scripts (ex: iptables ou regras de Firewall do Windows ) para bloquear IPs maliciosos com a aprovação do analista.
 Análise de Logs: Modificar o script para ler IPs diretamente de arquivos de log (ex: Apache, Nginx, Firewall).
