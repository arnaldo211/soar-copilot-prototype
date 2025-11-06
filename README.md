# IP Intelligence System: Ferramenta Full-Stack de Análise de Segurança

![Cybersecurity AI Banner](https://i.imgur.com/Q3fG4aA.png)

## 📖 Visão Geral

O **IP Intelligence System** é uma aplicação full-stack de cibersegurança com foco em Blue Team, projetada para automatizar a coleta e análise de informações sobre endereços de IP. O projeto evoluiu de um simples script para um sistema completo, demonstrando um ciclo de desenvolvimento de software moderno, desde a linha de comando até uma API em contêiner com uma interface web interativa.

Este projeto demonstra um amplo conjunto de habilidades, incluindo:

- **Desenvolvimento Back-End:** Criação de uma API RESTful robusta com Flask.
- **Desenvolvimento Front-End:** Construção de uma interface de usuário reativa com HTML, CSS e JavaScript puro.
- **Automação de Segurança:** Orquestração de ferramentas como Nmap e integração com APIs de Threat Intelligence (AbuseIPDB).
- **Gerenciamento de Dados:** Persistência de dados com um banco de dados SQLite e implementação de um sistema de cache inteligente.
- **DevOps:** Containerização da aplicação com Docker e orquestração de serviços com Docker Compose.
- **Arquitetura de Software:** Refatoração de código para uma arquitetura modular e centralizada (`logic.py`).

---

## ⚙️ Arquitetura e Funcionalidades

O sistema é composto por três componentes principais que trabalham juntos:

1.  **`IP Intelligence API` (Back-End):** O coração do sistema. Uma API Flask que expõe endpoints seguros para consultar o banco de dados, solicitar análises externas (Geolocalização, AbuseIPDB, etc.) e análises de segurança internas (scan de portas com Nmap).
2.  **`IP Intelligence Dashboard` (Front-End):** Uma interface web que consome a API, permitindo que o analista realize análises de forma interativa, visualize os resultados em uma tabela dinâmica, ordene os dados e exporte para CSV.
3.  **`ip-intel-cli` (Linha de Comando):** A ferramenta original, que permite a automação de análises via terminal, ideal para scripting e integração com outros processos.

---

## 🚀 Como Executar (Método Recomendado: Docker Compose)

A forma mais simples e recomendada de executar a aplicação completa (API + Banco de Dados) é usando o Docker e o Docker Compose.

### 1. Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- Git

### 2. Instalação
Primeiro, clone o repositório e navegue para o branch correto:

```bash
git clone https://github.com/arnaldo211/soar-copilot-prototype.git
cd soar-copilot-prototype
git checkout free-api-version
```

### 3. Configuração
Crie um arquivo chamado `.env` na raiz do projeto para armazenar as chaves de API. A chave `API_SECRET_KEY` é para proteger sua própria API, e a `ABUSEIPDB_KEY` é para o serviço externo.

```env
# Chave para proteger sua API. Pode ser qualquer string segura.
API_SECRET_KEY="secret-key-for-ip-intel-api-12345-xyz"

# Chave opcional para o serviço AbuseIPDB
ABUSEIPDB_KEY="SUA_CHAVE_DO_ABUSEIPDB_AQUI"
```

### 4. Execução com Docker Compose
Com o Docker em execução na sua máquina, suba os serviços com um único comando:

```bash
docker compose up -d --build
```

O comando irá construir a imagem da sua API e iniciar o contêiner em segundo plano (`-d`).
O banco de dados `ip_intelligence.db` será criado e persistido na pasta do projeto.

### 5. Acessando a Aplicação
- **Interface Web (Dashboard):** Abra o arquivo `frontend/index.html` diretamente no seu navegador. A interface se conectará automaticamente à API que está rodando no Docker.
- **API:** A API estará disponível em `http://127.0.0.1:5000`. Você pode testar os endpoints com ferramentas como `curl` ou Postman.

### 6. Parando a Aplicação
Para parar os serviços, execute na pasta do projeto:

```bash
docker compose down
```

---

## 🔧 Uso da Ferramenta de Linha de Comando (`main.py`)

A ferramenta de linha de comando ainda é funcional e pode ser usada para automação.

**Ative o Ambiente Virtual:**

```bash
source venv/bin/activate
```

**Execute com os Argumentos:**

```bash
# Analisar um IP externo
python3 main.py --ip 8.8.8.8

# Consultar um IP no banco de dados
python3 main.py --query 8.8.8.8

# Fazer uma análise de segurança em um IP interno
python3 main.py --ip 192.168.1.1 --internal
```
**`Docs: Atualiza README para a Versão 13.0 (Full-Stack)`**
