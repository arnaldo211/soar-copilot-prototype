# IP Intelligence Dashboard & API Service

![Dashboard Banner](https://i.imgur.com/e3sYn0Y.png)

## 📖 Visão Geral

O **IP Intelligence Dashboard** é uma aplicação web Full-Stack projetada para automatizar a coleta e visualização de informações de *Threat Intelligence*. O projeto consiste em um **front-end interativo** e um **back-end de microsserviço**, containerizado com Docker.

O **back-end** é uma API RESTful desenvolvida em Python com Flask. Ele enriquece endereços de IP com dados de múltiplas fontes (geolocalização, reputação, DNS, portas abertas) e armazena os resultados em um banco de dados SQLite persistente, utilizando um sistema de cache inteligente para otimizar o desempenho.

O **front-end** é uma interface de usuário moderna, construída com HTML, CSS e JavaScript puro, que consome a API do back-end para fornecer uma experiência de análise de IPs rica e interativa diretamente no navegador.

Todo o serviço de back-end é encapsulado em um **contêiner Docker**, garantindo portabilidade, consistência e facilidade de implantação.

Este projeto demonstra um conjunto de habilidades em **Engenharia Full-Stack e DevSecOps**:
- **Desenvolvimento Front-End:** Criação de uma UI reativa com HTML, CSS e JavaScript (Fetch API, Promises).
- **Desenvolvimento de Back-End:** Construção de uma API RESTful com Flask e lógica de negócio modular.
- **Containerização com Docker:** Empacotamento da aplicação e suas dependências para implantação consistente.
- **Gerenciamento de Banco de Dados:** Uso de SQLite para persistência de dados e cache.
- **Integração de Sistemas:** Conexão de um front-end a um back-end via requisições HTTP (CORS).

---

## 🚀 Como Executar a Aplicação Completa

A maneira mais fácil de executar o projeto é usando o contêiner Docker para o back-end e abrindo o arquivo do front-end no navegador.

### 1. Pré-requisitos
- Docker Engine instalado e em execução.
- Git.
- Nmap (para a construção da imagem Docker).

### 2. Inicie o Back-End (API em Contêiner)
Clone o repositório, navegue até a pasta do projeto e use os comandos do Docker para construir e executar o serviço de API.

```bash
# Clone o repositório
git clone https://github.com/arnaldo211/soar-copilot-prototype.git
cd soar-copilot-prototype

# Mude para o branch correto
git checkout free-api-version

# Construa a imagem Docker (pode levar alguns minutos na primeira vez)
docker build -t ip-intelligence-service .

# Execute o contêiner em segundo plano
docker run -d -p 5000:5000 --name ip-api-container ip-intelligence-service
```

Neste ponto, seu serviço de back-end está rodando em `http://127.0.0.1:5000`.

### 3. Use a Interface Web (Front-End)
Com o back-end no ar, basta abrir a interface no seu navegador.
1. Navegue até a pasta `frontend` dentro do diretório do projeto.
2. Dê um clique duplo no arquivo `index.html`.

A página "IP Intelligence Dashboard" será aberta. Agora você pode usar os botões "Consultar do Banco" e "Analisar IPs" para interagir com a sua API.

### 4. Gerenciando o Contêiner

```bash
# Ver os logs da API em tempo real
docker logs -f ip-api-container

# Parar o contêiner quando terminar
docker stop ip-api-container

# Remover o contêiner (opcional, após pará-lo)
docker rm ip-api-container
```

---

## ⚙️ Detalhes da Arquitetura da API

Para usuários avançados, a API pode ser consumida diretamente:

### `GET /query/<ip>`
- **Descrição:** Busca um IP no banco de dados e retorna o último relatório conhecido.
- **Resposta de Sucesso (200):** Objeto JSON com os dados do IP.

### `POST /analyze`
- **Descrição:** Solicita a análise de uma lista de IPs, utilizando o cache para otimização.
- **Corpo da Requisição:** `{"ips": ["ip1", "ip2", ...]}`
- **Exemplo de uso com curl:**

```bash
# Consultar um IP
curl http://127.0.0.1:5000/query/8.8.8.8

# Analisar múltiplos IPs
curl -X POST -H "Content-Type: application/json" -d '{"ips": ["8.8.4.4", "1.1.1.1"]}' http://127.0.0.1:5000/analyze
```

---

## 🔮 Próximos Passos
- **Orquestração com Docker Compose:** Criar um `docker-compose.yml` para gerenciar múltiplos serviços.
- **Adicionar Autenticação:** Implementar um sistema de chave de API para proteger os endpoints.
- **Melhorar a UI:** Adicionar funcionalidades como ordenação de tabelas, filtros e exportação de dados diretamente da interface.

- **`Docs: Atualiza README para a Versão 8.0 (Full-Stack )`**
