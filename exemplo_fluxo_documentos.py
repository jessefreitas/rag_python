"""
Exemplo prático do fluxo de documentos no sistema RAG
Demonstra como os documentos são processados e armazenados
"""

import os
import shutil
from pathlib import Path
from rag_system import RAGSystem

def criar_documento_exemplo():
    """Cria um documento de exemplo para demonstração"""
    documento = """
    # Manual de Inteligência Artificial
    
    ## Introdução
    A Inteligência Artificial (IA) é um campo da ciência da computação que busca criar sistemas capazes de realizar tarefas que normalmente requerem inteligência humana.
    
    ## Tipos de IA
    1. **IA Fraca (Narrow AI)**: Sistemas projetados para tarefas específicas
    2. **IA Forte (General AI)**: Sistemas com inteligência humana geral
    3. **Superinteligência**: IA que supera a inteligência humana
    
    ## Aplicações
    - Processamento de linguagem natural
    - Visão computacional
    - Sistemas de recomendação
    - Automação de processos
    - Diagnóstico médico
    
    ## Tecnologias
    - Machine Learning
    - Deep Learning
    - Redes Neurais
    - Algoritmos genéticos
    
    ## Desafios
    - Ética e responsabilidade
    - Viés algorítmico
    - Privacidade de dados
    - Impacto no emprego
    
    ## Futuro
    A IA continuará evoluindo e transformando diversos setores da sociedade.
    """
    
    # Criar pasta documents se não existir
    Path("documents").mkdir(exist_ok=True)
    
    # Salvar documento
    with open("documents/manual_ia.txt", "w", encoding="utf-8") as f:
        f.write(documento)
    
    print("✅ Documento de exemplo criado: documents/manual_ia.txt")

def demonstrar_fluxo_completo():
    """Demonstra o fluxo completo de documentos"""
    print("🔄 DEMONSTRAÇÃO DO FLUXO DE DOCUMENTOS")
    print("=" * 50)
    
    # 1. Criar documento de exemplo
    print("\n1️⃣ Criando documento de exemplo...")
    criar_documento_exemplo()
    
    # 2. Inicializar sistema RAG
    print("\n2️⃣ Inicializando sistema RAG...")
    rag = RAGSystem(
        persist_directory="./vector_db_demo",
        chunk_size=500,
        chunk_overlap=100
    )
    
    # 3. Carregar documentos
    print("\n3️⃣ Carregando documentos...")
    sucesso = rag.load_documents(directory_path="documents/")
    
    if sucesso:
        print("✅ Documentos carregados com sucesso!")
    else:
        print("❌ Erro ao carregar documentos")
        return
    
    # 4. Verificar informações do banco
    print("\n4️⃣ Verificando informações do banco...")
    info = rag.vector_store.get_collection_info()
    print(f"📊 Documentos no banco: {info['document_count']}")
    print(f"📁 Localização: {info['persist_directory']}")
    print(f"🤖 Modelo de embedding: {info['embedding_model']}")
    
    # 5. Fazer consultas de teste
    print("\n5️⃣ Testando consultas...")
    
    perguntas = [
        "O que é inteligência artificial?",
        "Quais são os tipos de IA?",
        "Quais são as aplicações da IA?",
        "Quais são os desafios da IA?"
    ]
    
    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n❓ Pergunta {i}: {pergunta}")
        
        response = rag.query(pergunta)
        
        if response["success"]:
            print(f"🤖 Resposta: {response['answer'][:200]}...")
            if response["sources"]:
                print(f"📚 Fontes: {len(response['sources'])} documento(s)")
        else:
            print(f"❌ Erro: {response['answer']}")
    
    # 6. Buscar documentos similares
    print("\n6️⃣ Testando busca por similaridade...")
    query = "machine learning"
    resultados = rag.search_similar_documents(query, k=3)
    
    print(f"🔍 Busca por: '{query}'")
    print(f"📄 Resultados encontrados: {len(resultados)}")
    
    for i, resultado in enumerate(resultados, 1):
        print(f"  {i}. Score: {resultado.get('score', 'N/A'):.3f}")
        print(f"     Conteúdo: {resultado.get('content', '')[:100]}...")
    
    # 7. Mostrar estrutura de pastas
    print("\n7️⃣ Estrutura de pastas criada:")
    mostrar_estrutura_pastas()
    
    return rag

def mostrar_estrutura_pastas():
    """Mostra a estrutura de pastas criada"""
    print("\n📁 ESTRUTURA DE PASTAS:")
    print("-" * 30)
    
    # Verificar se as pastas existem
    pastas = ["documents", "vector_db_demo"]
    
    for pasta in pastas:
        if Path(pasta).exists():
            print(f"✅ {pasta}/")
            
            # Listar arquivos na pasta
            try:
                arquivos = list(Path(pasta).rglob("*"))
                for arquivo in arquivos[:5]:  # Mostrar apenas os primeiros 5
                    if arquivo.is_file():
                        tamanho = arquivo.stat().st_size
                        print(f"   📄 {arquivo.name} ({tamanho} bytes)")
                    elif arquivo.is_dir():
                        print(f"   📁 {arquivo.name}/")
                
                if len(arquivos) > 5:
                    print(f"   ... e mais {len(arquivos) - 5} arquivos/pastas")
                    
            except Exception as e:
                print(f"   ❌ Erro ao listar: {e}")
        else:
            print(f"❌ {pasta}/ (não existe)")

def limpar_demonstracao():
    """Limpa os arquivos da demonstração"""
    print("\n🧹 Limpando arquivos da demonstração...")
    
    pastas_para_limpar = ["documents", "vector_db_demo"]
    
    for pasta in pastas_para_limpar:
        if Path(pasta).exists():
            try:
                shutil.rmtree(pasta)
                print(f"✅ Pasta {pasta}/ removida")
            except Exception as e:
                print(f"❌ Erro ao remover {pasta}/: {e}")

def verificar_status_sistema():
    """Verifica o status atual do sistema"""
    print("\n📊 STATUS DO SISTEMA")
    print("=" * 30)
    
    # Verificar se existe banco de vetores
    if Path("vector_db").exists():
        print("✅ Banco de vetores encontrado (vector_db/)")
        
        # Tentar carregar sistema
        try:
            rag = RAGSystem()
            info = rag.vector_store.get_collection_info()
            print(f"📊 Documentos no banco: {info['document_count']}")
        except Exception as e:
            print(f"❌ Erro ao carregar sistema: {e}")
    else:
        print("❌ Banco de vetores não encontrado")
    
    # Verificar pasta de documentos
    if Path("documents").exists():
        arquivos = list(Path("documents").glob("*"))
        print(f"📁 Pasta documents/ encontrada com {len(arquivos)} arquivos")
    else:
        print("❌ Pasta documents/ não encontrada")

def main():
    """Função principal"""
    print("📄 DEMONSTRAÇÃO DO FLUXO DE DOCUMENTOS NO RAG")
    print("=" * 60)
    
    while True:
        print("\nEscolha uma opção:")
        print("1. 🚀 Executar demonstração completa")
        print("2. 📊 Verificar status do sistema")
        print("3. 🧹 Limpar arquivos da demonstração")
        print("4. ❌ Sair")
        
        opcao = input("\nDigite sua opção (1-4): ").strip()
        
        if opcao == "1":
            try:
                rag = demonstrar_fluxo_completo()
                print("\n🎉 Demonstração concluída com sucesso!")
                print("\n💡 Agora você pode:")
                print("   • Fazer perguntas sobre IA")
                print("   • Adicionar mais documentos")
                print("   • Explorar a interface Streamlit")
                
            except Exception as e:
                print(f"❌ Erro na demonstração: {e}")
        
        elif opcao == "2":
            verificar_status_sistema()
        
        elif opcao == "3":
            limpar_demonstracao()
        
        elif opcao == "4":
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main() 