# IP Analyzer Pro: Ferramenta de Análise de IPs em Massa

![Network Banner](https://i.imgur.com/e3sYn0Y.png )

## 📖 Visão Geral

O **IP Analyzer Pro** (anteriormente SOAR-Copilot) é uma ferramenta de linha de comando desenvolvida em Python para analistas de cibersegurança e entusiastas de redes. O objetivo é automatizar e acelerar o processo de investigação de múltiplos endereços de IP.

Esta ferramenta robusta é capaz de processar um único IP ou uma lista de IPs de um arquivo, enriquecendo cada um com dados de **geolocalização** (via ip-api.com) e **reputação de abuso** (via AbuseIPDB). Os resultados são consolidados e convenientemente salvos em um arquivo `.csv` para análise posterior.

Este projeto demonstra habilidades práticas em:
- **Desenvolvimento de Ferramentas de Segurança:** Criação de um script útil para automação de *Threat Intelligence*.
- **Integração com Múltiplas APIs:** Comunicação e consolidação de dados de diferentes fontes externas.
- **Processamento de Dados em Lote:** Capacidade de analisar múltiplos alvos de forma eficiente, com feedback visual através de uma barra de progresso.
- **Manipulação de Arquivos:** Leitura de alvos de arquivos de texto e exportação de relatórios estruturados em formato CSV.

---

## ✨ Funcionalidades Principais

- **Modo Duplo de Análise:** Analise um único IP rapidamente ou processe centenas de IPs de um arquivo de texto.
- **Enriquecimento de Dados:** Integração com **ip-api.com** para geolocalização e **AbuseIPDB** para pontuação de risco.
- **Exportação para CSV:** Gera um arquivo `relatorio_ips.csv` com todos os resultados, pronto para ser importado em planilhas ou outras ferramentas de análise.
- **Feedback de Progresso:** Utiliza a biblioteca `tqdm` para exibir uma barra de progresso durante a análise em massa.
- **Design Resiliente:** Lida de forma elegante com chaves de API ausentes, IPs inválidos e limites de taxa das APIs.

---

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.10 ou superior
- Git

### 2. Instalação
Clone o repositório e entre na pasta do projeto:
```bash
git clone https://github.com/arnaldo211/soar-copilot-prototype.git
cd soar-copilot-prototype
