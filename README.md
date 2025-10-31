# IP Intelligence Service API (Dockerized)

![Docker Banner](https://i.imgur.com/e3sYn0Y.png)

## 📖 Visão Geral

O **IP Intelligence Service** é um microsserviço de API RESTful, desenvolvido em Python com Flask e **containerizado com Docker**. O projeto foi projetado para automatizar a coleta de informações de *Threat Intelligence* de forma portátil, confiável e escalável.

O serviço expõe endpoints para consultar e analisar endereços de IP, enriquecendo-os com dados de múltiplas fontes (geolocalização, reputação, DNS, portas abertas) e armazenando os resultados em um banco de dados **SQLite** persistente. A arquitetura inclui um sistema de cache inteligente para otimizar o desempenho.

O uso de Docker encapsula toda a aplicação, suas dependências de sistema (como `nmap`) e de Python em um contêiner isolado, garantindo que ela funcione de maneira consistente em qualquer ambiente.

Este projeto demonstra um conjunto de habilidades essenciais em **DevSecOps e Engenharia de Back-end**:
- **Containerização com Docker:** Criação de um `Dockerfile` para empacotar e implantar a aplicação de forma eficiente.
- **Desenvolvimento de APIs RESTful:** Construção de um serviço web com Flask, seguindo as melhores práticas de endpoints.
- **Arquitetura de Microsserviços:** Separação da lógica de negócio da camada de API para maior modularidade.
- **Gerenciamento de Banco de Dados:** Uso de SQLite para persistência de dados e atualizações inteligentes.
- **Lógica de Cache:** Implementação de um cache baseado em tempo para otimização de recursos.

---

## 🚀 Como Executar com Docker (Método Recomendado)

A maneira mais fácil e recomendada de executar este serviço é através do Docker.

### 1. Pré-requisitos
- Docker Engine instalado e em execução.

### 2. Construa a Imagem Docker
Clone o repositório e navegue até a pasta do projeto. Em seguida, use o comando `docker build` para construir a imagem a partir do `Dockerfile`.

```bash
# Clone o repositório
git clone https://github.com/arnaldo211/soar-copilot-prototype.git
cd soar-copilot-prototype

# Mude para o branch correto
git checkout free-api-version

# Construa a imagem Docker
docker build -t ip-intelligence-service .
```

### 3. Execute o Contêiner
Após a construção da imagem, inicie o contêiner. O comando abaixo mapeia a porta 5000 e executa o contêiner em segundo plano.

```bash
docker run -d -p 5000:5000 --name ip-api-container ip-intelligence-service
```

Sua API agora está rodando dentro de um contêiner em `http://127.0.0.1:5000`.

### 4. Interaja com a API
Use `curl` ou qualquer outro cliente de API para interagir com o serviço.

**Consultar um IP no banco de dados:**

```bash
curl http://127.0.0.1:5000/query/8.8.8.8
```

**Solicitar a análise de novos IPs:**

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"ips": ["8.8.4.4", "1.1.1.1"]}' \
  http://127.0.0.1:5000/analyze
```

### 5. Gerenciando o Contêiner

```bash
# Ver os logs da API em tempo real
docker logs -f ip-api-container

# Parar o contêiner
docker stop ip-api-container

# Remover o contêiner (após pará-lo)
docker rm ip-api-container
```

---

## ⚙️ Arquitetura da API

### `GET /query/<ip>`
- **Descrição:** Busca um IP no banco de dados e retorna o último relatório conhecido.
- **Resposta de Sucesso (200):** Objeto JSON com os dados do IP.
- **Resposta de Falha (404):** Erro JSON se o IP não for encontrado.

### `POST /analyze`
- **Descrição:** Solicita a análise de uma lista de IPs. Verifica o cache antes de realizar uma nova análise completa.
- **Corpo da Requisição:** `{"ips": ["ip1", "ip2", ...]}`
- **Resposta de Sucesso (200):** Sumário em JSON com o status (`cached` ou `analyzed`) para cada IP.

---

## 🔮 Próximos Passos
- **Orquestração com Docker Compose:** Criar um arquivo `docker-compose.yml` para gerenciar múltiplos serviços (ex: a API e um banco de dados PostgreSQL) de forma declarativa.
- **Criar um Cliente Web Simples:** Desenvolver uma página HTML com JavaScript que consuma esta API para fornecer uma interface gráfica ao usuário.
- **Adicionar Autenticação:** Implementar um sistema simples de chave de API para proteger os endpoints.

- **`Docs: Atualiza README para a Versão 7.0 (Docker)`**
