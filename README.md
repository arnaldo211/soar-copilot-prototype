# IP Intelligence Database: Ferramenta de Análise e Persistência de Dados

![Database Banner](https://i.imgur.com/e3sYn0Y.png )

## 📖 Visão Geral

O **IP Intelligence Database** (anteriormente IP Analyzer Pro) é uma ferramenta de linha de comando desenvolvida em Python para analistas de cibersegurança. Sua função é automatizar a coleta de informações de *Threat Intelligence* sobre endereços de IP e armazená-las de forma persistente em um banco de dados **SQLite**.

A ferramenta processa múltiplos IPs, enriquece cada um com dados de geolocalização, reputação de abuso, resolução de DNS e portas abertas, e salva os resultados em um banco de dados local. Isso cria um histórico de análises que cresce com o tempo, permitindo consultas futuras e evitando análises repetidas.

Este projeto demonstra um conjunto robusto de habilidades:
- **Arquitetura de Dados:** Implementação de um banco de dados SQLite para persistência de dados.
- **Desenvolvimento de Ferramentas de Segurança:** Criação de um script para automação de coleta de *Threat Intelligence*.
- **Integração com Múltiplas APIs e Ferramentas:** Comunicação com APIs externas (ip-api.com, AbuseIPDB) e ferramentas de sistema (Nmap, DNS).
- **Interface de Linha de Comando Profissional:** Uso da biblioteca `argparse` para uma interação flexível e automatizável.
- **Programação Robusta:** Lida com erros, atualiza registros existentes e gerencia a estrutura do banco de dados.

---

## ✨ Funcionalidades Principais

- **Banco de Dados Persistente:** Todos os resultados são salvos em um arquivo de banco de dados SQLite (`ip_intelligence.db`), criando um histórico de todas as análises.
- **Atualização Inteligente:** Ao reanalisar um IP, a ferramenta atualiza o registro existente no banco de dados com as informações mais recentes, em vez de criar duplicatas.
- **Análise Multi-Fonte:** Para cada IP, a ferramenta coleta:
    - **Geolocalização:** País, cidade e provedor (ISP).
    - **Reputação:** Pontuação de abuso e número de denúncias via AbuseIPDB.
    - **DNS Reverso:** Tenta encontrar o hostname associado ao IP.
    - **Port Scan:** Verifica as portas TCP mais comuns abertas usando Nmap.
- **Interface via Argumentos:** Controle total pela linha de comando para especificar alvos (`--ip`, `--file`).

---

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.10 ou superior
- Git
- Nmap (`sudo apt install nmap`)

### 2. Instalação
Clone o repositório e entre na pasta do projeto:
```bash
git clone https://github.com/arnaldo211/soar-copilot-prototype.git
cd soar-copilot-prototype
