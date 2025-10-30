# IP Intelligence Service API

![API Banner](https://i.imgur.com/e3sYn0Y.png)

## 📖 Visão Geral

O **IP Intelligence Service** é um microsserviço de API RESTful, desenvolvido em Python com **Flask**, projetado para automatizar a coleta de informações de *Threat Intelligence*. Ele transforma uma ferramenta de linha de comando em uma plataforma de serviço que pode ser consumida por outras aplicações.

O serviço expõe endpoints para consultar e analisar endereços de IP, enriquecendo-os com dados de múltiplas fontes e armazenando os resultados de forma persistente em um banco de dados **SQLite**. A arquitetura inclui um sistema de cache inteligente para otimizar o desempenho e evitar chamadas de API redundantes.

Este projeto demonstra um conjunto avançado de habilidades de desenvolvimento de back-end e DevSecOps:
- **Desenvolvimento de APIs RESTful:** Criação de um serviço web com Flask, expondo endpoints claros e seguindo as melhores práticas.
- **Arquitetura de Microsserviços:** Separação da lógica de negócio (`logic.py`) da camada de apresentação da API (`api.py`).
- **Gerenciamento de Banco de Dados:** Uso de SQLite para persistência de dados, com atualizações inteligentes (`INSERT OR REPLACE`).
- **Lógica de Cache:** Implementação de um cache baseado em tempo para otimizar a performance e o uso de recursos.
- **Integração Multi-Fonte:** Consolidação de dados de APIs externas (ip-api.com, AbuseIPDB) e ferramentas de sistema (Nmap, DNS).

---

## 🚀 Arquitetura da API

O serviço é composto por dois endpoints principais:

#### `GET /query/<ip>`
Busca um endereço de IP diretamente no banco de dados local e retorna o último relatório conhecido instantaneamente.
- **Método:** `GET`
- **Resposta de Sucesso (200):** Um objeto JSON com os dados do IP.
- **Resposta de Falha (404):** Um objeto JSON de erro se o IP não for encontrado.

#### `POST /analyze`
Recebe uma lista de IPs em formato JSON e solicita uma análise. O serviço verifica o cache para cada IP:
- Se a análise for recente, retorna um status `cached`.
- Se a análise for antiga ou inexistente, executa o fluxo completo de enriquecimento e salva/atualiza o resultado no banco de dados, retornando um status `analyzed`.
- **Método:** `POST`
- **Corpo da Requisição:** `{"ips": ["ip1", "ip2", ...]}`
- **Resposta de Sucesso (200):** Um sumário em JSON com o status da análise para cada IP.

---

## ⚙️ Como Executar o Serviço Localmente

### 1. Pré-requisitos
- Python 3.10 ou superior
- Git
- Nmap (`sudo apt install nmap`)

### 2. Instalação
Clone o repositório e prepare o ambiente:

```bash
# Clone o repositório
git clone https://github.com/arnaldo211/soar-copilot-prototype.git
cd soar-copilot-prototype

# Mude para o branch da API
git checkout free-api-version

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração (Opcional)
Para a análise de reputação, crie um arquivo `.env` e adicione sua chave da AbuseIPDB:

```text
ABUSEIPDB_API_KEY="SUA_CHAVE_DO_ABUSEIPDB_AQUI"
```

### 4. Inicie o Servidor da API
Execute o arquivo `api.py`. O servidor ficará ativo, esperando por requisições.

```bash
python3 api.py
```

O servidor estará rodando em `http://127.0.0.1:5000`.

### 5. Interaja com a API (Exemplos com `curl`)
Abra um novo terminal para enviar requisições para o seu servidor.

Consultar um IP no banco de dados:

```bash
curl http://127.0.0.1:5000/query/8.8.8.8
```

Solicitar a análise de um ou mais IPs:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"ips": ["8.8.4.4", "1.1.1.1"]}' \
  http://127.0.0.1:5000/analyze
```

## 🔮 Próximos Passos
- **"Dockerizar" a Aplicação:** Criar um `Dockerfile` para empacotar a API, o banco de dados e todas as suas dependências em um contêiner Docker, tornando-a 100% portátil.
- **Criar um Cliente Web Simples:** Desenvolver uma página HTML com JavaScript que consuma esta API para fornecer uma interface gráfica ao usuário.
- **Adicionar Autenticação:** Implementar um sistema simples de chave de API para proteger os endpoints e controlar o acesso.
