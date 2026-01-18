# Sistema RAG com LangChain e PostgreSQL

Este projeto implementa um sistema de Retrieval-Augmented Generation (RAG) usando LangChain, PostgreSQL com pgVector para armazenamento vetorial e suporte a múltiplos provedores de LLM (OpenAI e Google Gemini).

## Estrutura do Projeto

```
├── docker-compose.yml
├── requirements.txt      # Dependências
├── .env.example          # Template das variáveis de ambiente
├── venv/                 # Ambiente virtual Python (criado automaticamente)
├── src/
│   ├── ingest.py         # Script de ingestão do PDF
│   ├── search.py         # Script de busca
│   ├── chat.py           # CLI para interação com usuário
├── document.pdf          # PDF para ingestão
└── README.md             # Instruções de execução
```

## Pré-requisitos

- Python 3.8+
- Docker e Docker Compose
- API Key do Google Gemini

### Instalação do Docker

**Windows:**
1. Baixe o Docker Desktop para Windows: https://www.docker.com/products/docker-desktop/
2. Instale e reinicie o computador
3. Abra o Docker Desktop e aguarde a inicialização
4. Verifique se está funcionando: `docker --version`

**Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# macOS (com Homebrew)
brew install docker docker-compose
```

## Configuração

### 1. Clone o repositório e crie um ambiente virtual

**Windows (PowerShell):**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure as variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Provedor de LLM (gemini)
LLM_PROVIDER=gemini

# API Key do Google Gemini
GOOGLE_API_KEY=sua_chave_google_aqui

# Configuração do banco de dados
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/vector_db
```

### 4. Inicie o banco de dados PostgreSQL

```bash
docker-compose up -d
```

### 5. Desativar o ambiente virtual (quando necessário)

**Windows (PowerShell):**
```bash
deactivate
```

**Linux/macOS:**
```bash
deactivate
```

## Uso

### Ordem de Execução

**1. Subir o banco de dados:**
```bash
docker compose up -d
```

**2. Executar ingestão do PDF:**
```bash
python src/ingest.py document.pdf
```

**3. Rodar o chat:**
```bash
python src/chat.py
```

### Detalhes dos Scripts

#### 1. Ingestão de Documentos

Para ingerir um PDF no banco de dados:

```bash
python src/ingest.py document.pdf
```

O script irá:
- Carregar o PDF
- Dividir em chunks
- Gerar embeddings
- Armazenar no PostgreSQL com pgVector

#### 2. Busca de Documentos

Para buscar documentos similares a uma query:

```bash
python src/search.py "sua pergunta aqui" 5
```

Onde:
- `"sua pergunta aqui"` é a query de busca
- `5` é o número de resultados (opcional, padrão é 5)

#### 3. Chat Interativo

Para iniciar uma conversa com o sistema RAG:

```bash
python src/chat.py
```

O chat permite:
- Fazer perguntas sobre os documentos ingeridos
- Receber respostas baseadas no contexto dos documentos
- Digitar `sair` para encerrar

### ⚠️ Importante: Docker Necessário

**Se você não tiver o Docker instalado:**
- Os scripts irão falhar com erro de conexão ao banco de dados
- Isso é esperado e normal
- Instale o Docker Desktop primeiro para usar o sistema completo

### 🚦 Rate Limiting

O sistema inclui um contador de requisições automático que:
- **Limita a 15 requisições por minuto** (limite gratuito do Google Gemini)
- **Aguarda automaticamente** quando o limite é atingido
- **Mostra status** das requisições restantes
- **Processa em lotes** para otimizar o uso da API

**Comandos especiais no chat:**
- Digite `status` para ver o status do rate limiter
- Digite `sair` para encerrar o chat

## Funcionalidades

### Provedor de LLM

O sistema está configurado para usar Google Gemini:

- **Google Gemini**: Usa `models/embedding-001` para embeddings e `gemini-pro` para chat

### Processamento de PDF

- Carregamento automático de PDFs
- Divisão inteligente em chunks (1000 caracteres com overlap de 150)
- Preservação de metadados

### Armazenamento Vetorial

- PostgreSQL com extensão pgVector
- Busca por similaridade
- Limpeza automática antes de nova ingestão

## Exemplos de Uso

### Ingestão
```bash
# Ingerir um documento
python src/ingest.py meu_documento.pdf
```

### Busca
```bash
# Buscar informações sobre machine learning
python src/search.py "machine learning" 3

# Buscar conceitos de IA
python src/search.py "inteligência artificial"
```

### Chat
```bash
# Iniciar chat interativo
python src/chat.py

# Exemplo de conversa:
# 👤 Você: O que é machine learning?
# 🤖 Assistente: Machine learning é uma área da inteligência artificial...
```

## Troubleshooting

### Erro de Conexão com Banco
- Verifique se o Docker está rodando: `docker-compose ps`
- Reinicie o banco: `docker-compose restart`

### Erro de API Key
- Verifique se a chave do Google Gemini está configurada no arquivo `.env`
- Confirme se a chave é válida e tem créditos
- Obtenha sua chave em: https://makersuite.google.com/app/apikey

### Erro de Importação
- Reinstale as dependências: `pip install -r requirements.txt --force-reinstall`

## Tecnologias Utilizadas

- **LangChain**: Framework para aplicações com LLM
- **PostgreSQL + pgVector**: Banco de dados vetorial
- **Google Gemini API**: Modelos de linguagem e embeddings
- **PyPDF**: Processamento de PDFs
- **Docker**: Containerização do banco de dados
