"""
Exemplo de uso do sistema RAG Python
"""

import os
from rag_system import RAGSystem

def main():
    """Exemplo de uso do sistema RAG"""
    
    print("🤖 Sistema RAG Python - Exemplo de Uso")
    print("=" * 50)
    
    # Verificar se a API key está configurada
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Erro: OPENAI_API_KEY não configurada!")
        print("Configure a variável de ambiente ou edite o arquivo .env")
        return
    
    try:
        # Inicializar sistema RAG
        print("🚀 Inicializando sistema RAG...")
        rag = RAGSystem(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000
        )
        print("✅ Sistema inicializado com sucesso!")
        
        # Exemplo 1: Carregar documentos de um diretório
        print("\n📁 Exemplo 1: Carregando documentos...")
        documents_dir = "./documents"
        
        if os.path.exists(documents_dir):
            success = rag.load_documents(directory_path=documents_dir)
            if success:
                print("✅ Documentos carregados com sucesso!")
            else:
                print("⚠️ Nenhum documento foi carregado")
        else:
            print(f"⚠️ Diretório {documents_dir} não encontrado")
        
        # Exemplo 2: Fazer perguntas
        print("\n💬 Exemplo 2: Fazendo perguntas...")
        
        questions = [
            "O que é inteligência artificial?",
            "Como funciona o machine learning?",
            "Quais são as principais aplicações da IA?"
        ]
        
        for question in questions:
            print(f"\n❓ Pergunta: {question}")
            
            try:
                response = rag.query(question)
                
                if response["success"]:
                    print(f"🤖 Resposta: {response['answer']}")
                    
                    if response["sources"]:
                        print("📚 Fontes:")
                        for i, source in enumerate(response["sources"], 1):
                            print(f"   {i}. {source['source']}")
                else:
                    print(f"❌ Erro: {response['answer']}")
                    
            except Exception as e:
                print(f"❌ Erro ao processar pergunta: {str(e)}")
        
        # Exemplo 3: Buscar documentos similares
        print("\n🔍 Exemplo 3: Buscando documentos similares...")
        
        search_query = "tecnologia"
        try:
            results = rag.search_similar_documents(search_query, k=3)
            
            if results:
                print(f"✅ Encontrados {len(results)} documentos similares para '{search_query}':")
                for i, result in enumerate(results, 1):
                    print(f"\n   Documento {i}:")
                    print(f"   Fonte: {result['metadata'].get('source', 'N/A')}")
                    print(f"   Conteúdo: {result['content'][:100]}...")
            else:
                print("⚠️ Nenhum documento encontrado")
                
        except Exception as e:
            print(f"❌ Erro na busca: {str(e)}")
        
        # Exemplo 4: Informações do sistema
        print("\nℹ️ Exemplo 4: Informações do sistema...")
        
        try:
            system_info = rag.get_system_info()
            
            print("📊 Informações do Sistema:")
            print(f"   Modelo: {system_info.get('model_name')}")
            print(f"   Temperatura: {system_info.get('temperature')}")
            print(f"   Max Tokens: {system_info.get('max_tokens')}")
            
            vector_info = system_info.get("vector_store", {})
            print(f"   Documentos: {vector_info.get('document_count', 0)}")
            print(f"   Coleção: {vector_info.get('collection_name')}")
            
            sources = system_info.get("document_sources", [])
            if sources:
                print("   Fontes de documentos:")
                for source in sources:
                    print(f"     • {source}")
                    
        except Exception as e:
            print(f"❌ Erro ao obter informações: {str(e)}")
        
        print("\n🎉 Exemplo concluído!")
        print("\n💡 Dica: Use 'streamlit run app.py' para acessar a interface web")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar sistema: {str(e)}")

if __name__ == "__main__":
    main() 