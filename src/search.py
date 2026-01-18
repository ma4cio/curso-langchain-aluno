"""
Script de busca no banco de dados PostgreSQL com pgVector.
"""

import os
import sys
from dotenv import load_dotenv

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
        collection_name="documents"
    )
    
    return vector_store

def search_documents(query, k=5):
    """Busca documentos similares à query."""
    try:
        # Configurar o vector store
        vector_store = setup_vector_store()
        
        # Realizar busca
        results = vector_store.similarity_search(query, k=k)
        
        return results
        
    except Exception as e:
        print(f"Erro durante a busca: {str(e)}")
        return []

def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("Uso: python search.py <query> [número_de_resultados]")
        print("Exemplo: python search.py 'machine learning' 3")
        sys.exit(1)
    
    query = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # Verificar se as variáveis de ambiente estão configuradas
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("Erro: OPENAI_API_KEY não configurada no arquivo .env")
        sys.exit(1)
    elif provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
        print("Erro: GOOGLE_API_KEY não configurada no arquivo .env")
        sys.exit(1)
    
    # Executar busca
    print(f"Buscando por: '{query}'")
    print_rate_limit_status()
    
    results = search_documents(query, k)
    
    if results:
        print(f"\nEncontrados {len(results)} resultados:\n")
        for i, doc in enumerate(results, 1):
            print(f"--- Resultado {i} ---")
            print(f"Conteudo: {doc.page_content[:200]}...")
            if hasattr(doc, 'metadata') and doc.metadata:
                print(f"Metadados: {doc.metadata}")
            print()
    else:
        print("Nenhum resultado encontrado")
    
    print_rate_limit_status()

if __name__ == "__main__":
    main()
