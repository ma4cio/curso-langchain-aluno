"""
Script de ingestão de PDF para o banco de dados PostgreSQL com pgVector.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from rate_limiter import check_rate_limit, print_rate_limit_status

# Carregar variáveis de ambiente
load_dotenv()

def get_embeddings():
    """Retorna o modelo de embeddings baseado na configuração."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    elif provider == "gemini":
        # Verificar rate limit antes de criar embeddings
        if not check_rate_limit():
            raise Exception("Rate limit excedido. Tente novamente em alguns minutos.")
        
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    else:
        raise ValueError(f"Provedor não suportado: {provider}")

def setup_vector_store():
    """Configura e retorna o store vetorial."""
    embeddings = get_embeddings()
    
    # URL do banco de dados
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/vector_db")
    
    # Configurar o PGVector
    vector_store = PGVector(
        embeddings=embeddings,
        connection=database_url,
        collection_name="documents",
        pre_delete_collection=True  # Limpa a tabela antes de inserir novos dados
    )
    
    return vector_store

def load_and_split_pdf(pdf_path):
    """Carrega e divide o PDF em chunks."""
    print(f"Carregando PDF: {pdf_path}")
    
    # Carregar o PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    print(f"PDF carregado com {len(documents)} páginas")
    
    # Configurar o text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Dividir os documentos em chunks
    chunks = text_splitter.split_documents(documents)
    
    print(f"PDF dividido em {len(chunks)} chunks")
    
    return chunks

def ingest_pdf(pdf_path):
    """Executa o processo completo de ingestão."""
    try:
        # Verificar se o arquivo PDF existe
        if not os.path.exists(pdf_path):
            print(f"Erro: Arquivo PDF não encontrado: {pdf_path}")
            return False
        
        # Carregar e dividir o PDF
        chunks = load_and_split_pdf(pdf_path)
        
        # Configurar o vector store
        print("Configurando vector store...")
        vector_store = setup_vector_store()
        
        # Inserir os chunks no banco de dados
        print("Inserindo chunks no banco de dados...")
        print(f"Processando {len(chunks)} chunks...")
        
        # Processar chunks em lotes para respeitar rate limit
        batch_size = 5  # Processar 5 chunks por vez
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            print(f"Processando lote {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size} ({len(batch)} chunks)")
            
            # Verificar rate limit antes de cada lote
            if not check_rate_limit():
                print("Rate limit excedido. Aguardando...")
                continue
            
            vector_store.add_documents(batch)
            print(f"Lote {i//batch_size + 1} processado com sucesso!")
        
        print("Ingestão concluída com sucesso!")
        print_rate_limit_status()
        return True
        
    except Exception as e:
        print(f"Erro durante a ingestão: {str(e)}")
        return False

def main():
    """Função principal."""
    if len(sys.argv) != 2:
        print("Uso: python ingest.py <caminho_para_pdf>")
        print("Exemplo: python ingest.py document.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Verificar se as variáveis de ambiente estão configuradas
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("Erro: OPENAI_API_KEY não configurada no arquivo .env")
        sys.exit(1)
    elif provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
        print("Erro: GOOGLE_API_KEY não configurada no arquivo .env")
        sys.exit(1)
    
    # Executar ingestão
    success = ingest_pdf(pdf_path)
    
    if success:
        print("Ingestao concluida com sucesso!")
    else:
        print("Falha na ingestao")
        sys.exit(1)

if __name__ == "__main__":
    main()

