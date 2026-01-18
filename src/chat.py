"""
CLI para interação com usuário usando RAG (Retrieval-Augmented Generation).
"""

import os
import sys
from dotenv import load_dotenv

from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
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

def get_llm():
    """Retorna o modelo de linguagem baseado na configuração."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7
        )
    elif provider == "gemini":
        # Verificar rate limit antes de criar LLM
        if not check_rate_limit():
            raise Exception("Rate limit excedido. Tente novamente em alguns minutos.")
        
        return ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7
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

def create_rag_chain():
    """Cria a cadeia RAG para conversação."""
    vector_store = setup_vector_store()
    llm = get_llm()
    
    # Configurar o retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # Template do prompt
    prompt_template = ChatPromptTemplate.from_template("""
    Você é um assistente útil que responde perguntas baseado no contexto fornecido.
    
    Contexto:
    {context}
    
    Pergunta: {question}
    
    Instruções:
    - Responda baseado apenas no contexto fornecido
    - Se a informação não estiver no contexto, diga que não tem essa informação
    - Seja claro e conciso
    - Use português brasileiro
    """)
    
    # Criar a cadeia RAG
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def chat_loop():
    """Loop principal de conversação."""
    print("Chat RAG iniciado! Digite 'sair' para encerrar.\n")
    print("Comandos especiais:")
    print("- 'status': Mostrar status do rate limiter")
    print("- 'sair': Encerrar o chat\n")
    
    try:
        rag_chain = create_rag_chain()
        
        while True:
            # Obter pergunta do usuário
            question = input("Voce: ").strip()
            
            if question.lower() in ['sair', 'exit', 'quit']:
                print("Ate logo!")
                break
            
            if question.lower() == 'status':
                print_rate_limit_status()
                continue
            
            if not question:
                continue
            
            try:
                # Verificar rate limit antes de processar
                if not check_rate_limit():
                    print("Rate limit excedido. Aguardando...")
                    continue
                
                # Gerar resposta
                print("Assistente: ", end="", flush=True)
                response = rag_chain.invoke(question)
                print(response)
                print()
                
            except Exception as e:
                print(f"Erro ao processar pergunta: {str(e)}")
                print()
                
    except Exception as e:
        print(f"Erro ao inicializar o chat: {str(e)}")
        sys.exit(1)

def main():
    """Função principal."""
    # Verificar se as variáveis de ambiente estão configuradas
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("Erro: OPENAI_API_KEY não configurada no arquivo .env")
        sys.exit(1)
    elif provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
        print("Erro: GOOGLE_API_KEY não configurada no arquivo .env")
        sys.exit(1)
    
    # Iniciar chat
    chat_loop()

if __name__ == "__main__":
    main()
