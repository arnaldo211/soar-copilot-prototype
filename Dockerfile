# --- Estágio 1: Imagem Base e Dependências do Sistema ---
# Usamos uma imagem "slim" do Python, que é menor e mais otimizada.
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner.
# Todos os comandos seguintes serão executados a partir daqui.
WORKDIR /app

# Atualiza os pacotes e instala o 'nmap', que é uma dependência de sistema.
# O '--no-install-recommends' evita instalar pacotes desnecessários.
# O 'rm -rf /var/lib/apt/lists/*' limpa o cache para manter a imagem pequena.
RUN apt-get update && \
    apt-get install -y nmap --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# --- Estágio 2: Dependências Python ---
# Copia apenas o arquivo de requisitos primeiro.
# Isso aproveita o cache do Docker: se o requirements.txt não mudar,
# o Docker não reinstalará as dependências toda vez que você construir a imagem.
COPY requirements.txt .

# Instala as bibliotecas Python.
RUN pip install --no-cache-dir -r requirements.txt

# --- Estágio 3: Código da Aplicação e Execução ---
# Copia todo o resto do código do projeto para o diretório de trabalho /app.
COPY . .

# Expõe a porta 5000, informando ao Docker que o contêiner escutará nesta porta.
EXPOSE 5000

# O comando que será executado quando o contêiner iniciar.
# Inicia o servidor Flask, tornando-o acessível de fora (host='0.0.0.0').
CMD ["python3", "api.py"]
