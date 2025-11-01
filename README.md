# IP Intelligence Service API (Orquestrado com Docker Compose)

![Docker Banner](https://i.imgur.com/e3sYn0Y.png)

## 📖 Visão Geral

O **IP Intelligence Service** é um microsserviço de API RESTful, projetado para automatizar a coleta de informações de *Threat Intelligence*. A aplicação é orquestrada com **Docker Compose**, permitindo que todo o ambiente (serviço de API, dependências e configurações de rede) seja gerenciado com um único comando.

O projeto é composto por:
- **Back-End:** Uma API em Python/Flask que enriquece IPs com dados de múltiplas fontes (geolocalização, reputação, DNS, portas abertas) e os armazena em um banco de dados SQLite.
- **Front-End:** Uma interface web interativa (HTML/CSS/JS) que consome a API, permitindo que os usuários analisem e consultem IPs diretamente do navegador.

A arquitetura utiliza Docker para containerização e Docker Compose para orquestração, garantindo um ambiente de desenvolvimento e implantação que é **simples, portátil e consistente**.

Este projeto demonstra habilidades em **Engenharia de Software e DevOps**:
- **Orquestração de Contêineres:** Uso de `docker-compose.yml` para definir e gerenciar uma aplicação multi-serviço.
- **Desenvolvimento Full-Stack:** Conexão de uma UI de front-end a uma API de back-end.
- **Arquitetura de Microsserviços:** Separação da lógica de negócio da camada de API.
- **Gerenciamento de Dados:** Persistência de dados com SQLite e volumes Docker.

---

## 🚀 Como Executar a Aplicação (com Docker Compose)

Com Docker e Docker Compose instalados, iniciar toda a aplicação se resume a um único comando.

### 1. Pré-requisitos
- Docker Engine e Docker Compose Plugin instalados.
- Git.

### 2. Clone e Inicie o Serviço
Clone o repositório, navegue até a pasta do projeto e use o comando `docker compose up`.

```bash
# 1. Clone o repositório
git clone https://github.com/arnaldo211/soar-copilot-prototype.git
cd soar-copilot-prototype

# 2. Mude para o branch correto
git checkout free-api-version

# 3. Inicie toda a aplicação em segundo plano
docker compose up -d
```

Na primeira vez, o Compose construirá a imagem Docker, o que pode levar alguns minutos. Nas vezes seguintes, será quase instantâneo.
Sua API de back-end está agora rodando e acessível em `http://127.0.0.1:5000`.

### 3. Use a Interface Web
Com o back-end no ar, abra a interface no seu navegador:
1. Navegue até a pasta `frontend` dentro do diretório do projeto.
2. Dê um clique duplo no arquivo `index.html`.

A página "IP Intelligence Dashboard" será aberta, pronta para uso.

### 4. Gerenciando a Aplicação com Compose

```bash
# Ver o status dos seus serviços
docker compose ps

# Ver os logs da API em tempo real
docker compose logs -f

# Parar e remover os contêineres da aplicação
docker compose down
```

---

## ⚙️ Detalhes da Arquitetura

### `docker-compose.yml`
- **`services.ip-intelligence-api`:** Define o nosso serviço principal.
- **`build: .`:** Instrui o Compose a construir a imagem a partir do `Dockerfile` local.
- **`ports: - "5000:5000"`:** Mapeia a porta do host para a porta do contêiner.
- **`volumes: - ./ip_intelligence.db:/app/ip_intelligence.db`:** Garante que o banco de dados seja persistido no seu computador, sobrevivendo a recriações do contêiner.

### API Endpoints
- **`GET /query/<ip>`:** Consulta um IP no banco de dados.
- **`POST /analyze`:** Analisa uma lista de IPs, utilizando o cache.
- **Corpo da Requisição:** `{"ips": ["ip1", "ip2", ...]}`

---

## 🔮 Próximos Passos
- **Adicionar Autenticação:** Implementar um sistema de chave de API para proteger os endpoints.
- **Melhorar a UI:** Adicionar funcionalidades como ordenação de tabelas, filtros e exportação de dados.
- **Migrar para um Banco de Dados mais Robusto:** Usar o Docker Compose para adicionar um serviço de PostgreSQL e adaptar a aplicação para usá-lo.

- **`Docs: Atualiza README para a Versão 9.0 (Docker Compose )`**
