"""
Exemplo de uso integrado - RAG Python + RAGFlow
Demonstra como usar ambos os sistemas e suas diferenças
"""

import os
from pathlib import Path
from rag_system import RAGSystem
from ragflow_client import RAGFlowRAGSystem, RAGFlowClient

def test_rag_python():
    """Testa o sistema RAG Python local"""
    print("🤖 Testando Sistema RAG Python (Local)")
    print("=" * 50)
    
    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY não configurada!")
        return False
    
    try:
        # Inicializar sistema
        print("🚀 Inicializando RAG Python...")
        rag = RAGSystem(
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000
        )
        print("✅ RAG Python inicializado!")
        
        # Carregar documento de exemplo
        example_file = "documents/exemplo.txt"
        if Path(example_file).exists():
            print(f"📁 Carregando documento: {example_file}")
            success = rag.load_documents(file_paths=[example_file])
            if success:
                print("✅ Documento carregado com sucesso!")
            else:
                print("⚠️ Erro ao carregar documento")
        else:
            print(f"⚠️ Arquivo {example_file} não encontrado")
        
        # Fazer perguntas
        questions = [
            "O que é inteligência artificial?",
            "Quais são os tipos de IA?",
            "Como funciona o machine learning?"
        ]
        
        for question in questions:
            print(f"\n❓ Pergunta: {question}")
            try:
                response = rag.query(question)
                if response["success"]:
                    print(f"🤖 Resposta: {response['answer'][:200]}...")
                    if response["sources"]:
                        print(f"📚 Fontes: {len(response['sources'])} encontradas")
                else:
                    print(f"❌ Erro: {response['answer']}")
            except Exception as e:
                print(f"❌ Erro: {str(e)}")
        
        # Informações do sistema
        print("\n📊 Informações do Sistema RAG Python:")
        info = rag.get_system_info()
        print(f"   Modelo: {info.get('model_name')}")
        print(f"   Documentos: {info.get('vector_store', {}).get('document_count', 0)}")
        print(f"   Fontes: {len(info.get('document_sources', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no RAG Python: {str(e)}")
        return False

def test_ragflow():
    """Testa o sistema RAGFlow via API"""
    print("\n🌐 Testando Sistema RAGFlow (API)")
    print("=" * 50)
    
    try:
        # Inicializar cliente RAGFlow
        print("🚀 Conectando ao RAGFlow...")
        ragflow_url = "http://localhost:8000"
        collection_name = "rag_python_docs"
        
        # Testar conexão
        client = RAGFlowClient(ragflow_url)
        if not client.health_check():
            print("❌ RAGFlow não está acessível!")
            print("💡 Certifique-se de que o RAGFlow está rodando em Docker:")
            print("   cd /opt/ragflow/docker")
            print("   docker-compose up -d")
            return False
        
        print("✅ Conexão com RAGFlow estabelecida!")
        
        # Inicializar sistema integrado
        rag = RAGFlowRAGSystem(ragflow_url, collection_name)
        
        # Verificar coleção
        print(f"📊 Verificando coleção: {collection_name}")
        collection_info = client.get_collection_info(collection_name)
        if 'error' in collection_info:
            print(f"⚠️ Coleção {collection_name} não existe ou está vazia")
        else:
            print(f"✅ Coleção encontrada com {collection_info.get('document_count', 0)} documentos")
        
        # Fazer perguntas
        questions = [
            "O que é inteligência artificial?",
            "Quais são os tipos de IA?",
            "Como funciona o machine learning?"
        ]
        
        for question in questions:
            print(f"\n❓ Pergunta: {question}")
            try:
                response = rag.query(question)
                if response["success"]:
                    print(f"🤖 Resposta: {response['answer'][:200]}...")
                    if response["sources"]:
                        print(f"📚 Fontes: {len(response['sources'])} encontradas")
                else:
                    print(f"❌ Erro: {response['answer']}")
            except Exception as e:
                print(f"❌ Erro: {str(e)}")
        
        # Informações do sistema
        print("\n📊 Informações do Sistema RAGFlow:")
        info = rag.get_system_info()
        print(f"   Status: {info.get('ragflow_status')}")
        print(f"   URL: {info.get('ragflow_url')}")
        print(f"   Coleção: {info.get('collection_name')}")
        print(f"   Documentos: {info.get('document_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no RAGFlow: {str(e)}")
        return False

def compare_systems():
    """Compara os dois sistemas"""
    print("\n📊 Comparação dos Sistemas")
    print("=" * 50)
    
    comparison = {
        "RAG Python": {
            "Tipo": "Local",
            "Complexidade": "Baixa",
            "Recursos": "Básicos",
            "Escalabilidade": "Limitada",
            "Manutenção": "Simples",
            "Custo": "Baixo",
            "Ideal para": "POCs, desenvolvimento, uso pessoal"
        },
        "RAGFlow": {
            "Tipo": "Distribuído",
            "Complexidade": "Alta",
            "Recursos": "Avançados",
            "Escalabilidade": "Alta",
            "Manutenção": "Complexa",
            "Custo": "Médio/Alto",
            "Ideal para": "Produção, empresas, múltiplos usuários"
        }
    }
    
    for system, features in comparison.items():
        print(f"\n🔧 {system}:")
        for feature, value in features.items():
            print(f"   {feature}: {value}")

def main():
    """Função principal"""
    print("🤖 Sistema RAG Python + RAGFlow - Exemplo Integrado")
    print("=" * 60)
    
    # Testar RAG Python
    rag_python_success = test_rag_python()
    
    # Testar RAGFlow
    ragflow_success = test_ragflow()
    
    # Comparar sistemas
    compare_systems()
    
    # Resumo
    print("\n🎯 Resumo dos Testes")
    print("=" * 30)
    print(f"RAG Python: {'✅ Funcionando' if rag_python_success else '❌ Erro'}")
    print(f"RAGFlow: {'✅ Funcionando' if ragflow_success else '❌ Erro'}")
    
    if rag_python_success and ragflow_success:
        print("\n🎉 Ambos os sistemas estão funcionando!")
        print("💡 Você pode usar a interface integrada:")
        print("   streamlit run app_integrated.py")
    elif rag_python_success:
        print("\n✅ RAG Python funcionando!")
        print("💡 Use a interface original:")
        print("   streamlit run app.py")
    elif ragflow_success:
        print("\n✅ RAGFlow funcionando!")
        print("💡 Use a interface web do RAGFlow:")
        print("   http://localhost:8000")
    else:
        print("\n❌ Nenhum sistema está funcionando!")
        print("🔧 Verifique as configurações e dependências")
    
    print("\n📚 Próximos Passos:")
    print("1. Configure sua API key da OpenAI no arquivo .env")
    print("2. Para RAGFlow, certifique-se de que está rodando via Docker")
    print("3. Use a interface integrada para alternar entre os sistemas")
    print("4. Adicione seus próprios documentos para testar")

if __name__ == "__main__":
    main() 