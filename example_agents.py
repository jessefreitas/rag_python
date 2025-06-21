"""
Exemplo prático de uso dos Agentes de IA integrados com RAG
Demonstra diferentes cenários de uso dos agentes
"""

import os
import asyncio
from datetime import datetime
from typing import List, Dict

from agent_system import (
    MultiAgentSystem,
    ConversationalAgent,
    ResearchAgent,
    TaskExecutorAgent,
    create_agent
)
from rag_system import RAGSystem
from ragflow_client import RAGFlowRAGSystem

def setup_environment():
    """Configura o ambiente para os exemplos"""
    print("🔧 Configurando ambiente...")
    
    # Verificar variáveis de ambiente
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OpenAI API Key não configurada. Configure a variável OPENAI_API_KEY")
        return False
    
    print("✅ Ambiente configurado com sucesso!")
    return True

def example_conversational_agent():
    """Exemplo de uso do agente conversacional"""
    print("\n" + "="*60)
    print("💬 EXEMPLO: Agente Conversacional")
    print("="*60)
    
    try:
        # Criar sistema RAG
        rag_system = RAGSystem()
        
        # Criar agente conversacional
        agent = ConversationalAgent(rag_system)
        
        # Exemplos de conversas
        conversations = [
            "Olá! Como você pode me ajudar hoje?",
            "Pode me explicar sobre inteligência artificial?",
            "Quais são as principais tecnologias de IA?",
            "Como funciona o processamento de linguagem natural?"
        ]
        
        for i, user_input in enumerate(conversations, 1):
            print(f"\n👤 Usuário: {user_input}")
            
            # Processar com o agente
            response = agent.process(user_input)
            
            print(f"🤖 Agente: {response.content}")
            print(f"📊 Confiança: {response.confidence:.2f}")
            
            if response.actions_taken:
                print(f"🔧 Ações: {', '.join(response.actions_taken)}")
        
        print("\n✅ Exemplo do agente conversacional concluído!")
        
    except Exception as e:
        print(f"❌ Erro no exemplo conversacional: {str(e)}")

def example_research_agent():
    """Exemplo de uso do agente de pesquisa"""
    print("\n" + "="*60)
    print("🔍 EXEMPLO: Agente de Pesquisa")
    print("="*60)
    
    try:
        # Criar sistema RAG
        rag_system = RAGSystem()
        
        # Criar agente de pesquisa
        agent = ResearchAgent(rag_system)
        
        # Tópicos de pesquisa
        research_topics = [
            "Inteligência Artificial",
            "Machine Learning",
            "Deep Learning",
            "Processamento de Linguagem Natural"
        ]
        
        for topic in research_topics:
            print(f"\n🔍 Pesquisando sobre: {topic}")
            
            # Realizar análise
            response = agent.analyze_documents(topic)
            
            print(f"📋 Análise: {response.content}")
            print(f"📊 Confiança: {response.confidence:.2f}")
            
            if response.metadata:
                print(f"📈 Documentos analisados: {response.metadata.get('documents_analyzed', 0)}")
        
        print("\n✅ Exemplo do agente de pesquisa concluído!")
        
    except Exception as e:
        print(f"❌ Erro no exemplo de pesquisa: {str(e)}")

def example_task_executor_agent():
    """Exemplo de uso do agente executor"""
    print("\n" + "="*60)
    print("⚡ EXEMPLO: Agente Executor de Tarefas")
    print("="*60)
    
    try:
        # Criar sistema RAG
        rag_system = RAGSystem()
        
        # Criar agente executor
        agent = TaskExecutorAgent(rag_system)
        
        # Tarefas para executar
        tasks = [
            "Crie um resumo executivo sobre inteligência artificial",
            "Extraia os principais conceitos de machine learning dos documentos",
            "Compare diferentes abordagens de deep learning",
            "Gere recomendações para implementar IA em uma empresa"
        ]
        
        for i, task in enumerate(tasks, 1):
            print(f"\n⚡ Executando Tarefa {i}: {task}")
            
            # Executar tarefa
            response = agent.execute_task(task)
            
            print(f"📋 Resultado: {response.content}")
            print(f"📊 Confiança: {response.confidence:.2f}")
            
            if response.metadata:
                print(f"⏰ Tempo: {response.metadata.get('execution_time', 'N/A')}")
        
        print("\n✅ Exemplo do agente executor concluído!")
        
    except Exception as e:
        print(f"❌ Erro no exemplo executor: {str(e)}")

def example_multi_agent_system():
    """Exemplo de uso do sistema multi-agente"""
    print("\n" + "="*60)
    print("🤖 EXEMPLO: Sistema Multi-Agente")
    print("="*60)
    
    try:
        # Criar sistema RAG
        rag_system = RAGSystem()
        
        # Criar sistema multi-agente
        multi_agent = MultiAgentSystem(rag_system)
        
        # Exibir status dos agentes
        print("📊 Status dos Agentes:")
        agent_status = multi_agent.get_agent_status()
        for name, info in agent_status.items():
            print(f"  • {name}: {info['description']}")
        
        # Testar coordenação
        test_inputs = [
            "Olá, como você pode me ajudar?",
            "Pesquise sobre machine learning",
            "Execute uma análise de documentos sobre IA",
            "Quais são as tendências em deep learning?"
        ]
        
        for user_input in test_inputs:
            print(f"\n👤 Usuário: {user_input}")
            
            # Processar com coordenação
            response = multi_agent.process_with_coordination(user_input)
            
            print(f"🤖 Resposta: {response.content}")
            print(f"🎯 Agente Selecionado: {response.metadata.get('selected_agent', 'N/A')}")
            print(f"📊 Confiança: {response.confidence:.2f}")
        
        print("\n✅ Exemplo do sistema multi-agente concluído!")
        
    except Exception as e:
        print(f"❌ Erro no exemplo multi-agente: {str(e)}")

def example_ragflow_integration():
    """Exemplo de integração com RAGFlow"""
    print("\n" + "="*60)
    print("🔗 EXEMPLO: Integração com RAGFlow")
    print("="*60)
    
    try:
        # Verificar se RAGFlow está configurado
        if not os.getenv("RAGFLOW_API_KEY"):
            print("⚠️  RAGFlow API Key não configurada. Pulando exemplo...")
            return
        
        # Criar cliente RAGFlow
        ragflow_system = RAGFlowRAGSystem(
            base_url=os.getenv("RAGFLOW_BASE_URL", "http://localhost:9380"),
            api_key=os.getenv("RAGFLOW_API_KEY")
        )
        
        # Criar agente com RAGFlow
        agent = ConversationalAgent(ragflow_system)
        
        # Testar consultas
        queries = [
            "Explique sobre inteligência artificial",
            "Quais são as aplicações de machine learning?",
            "Como funciona o deep learning?"
        ]
        
        for query in queries:
            print(f"\n🔍 Consulta: {query}")
            
            # Processar consulta
            response = agent.process(query)
            
            print(f"🤖 Resposta: {response.content}")
            print(f"📊 Confiança: {response.confidence:.2f}")
        
        print("\n✅ Exemplo de integração com RAGFlow concluído!")
        
    except Exception as e:
        print(f"❌ Erro no exemplo RAGFlow: {str(e)}")

def example_custom_agent():
    """Exemplo de criação de agente personalizado"""
    print("\n" + "="*60)
    print("🎨 EXEMPLO: Agente Personalizado")
    print("="*60)
    
    try:
        from agent_system import AgentConfig, BaseAgent
        
        # Criar sistema RAG
        rag_system = RAGSystem()
        
        # Configuração personalizada
        custom_config = AgentConfig(
            name="Agente Especialista em IA",
            description="Agente especializado em inteligência artificial e machine learning",
            system_prompt="""Você é um especialista em inteligência artificial com vasto conhecimento 
            em machine learning, deep learning e processamento de linguagem natural. 
            Forneça explicações técnicas detalhadas e exemplos práticos sempre que possível.""",
            tools=["rag_query", "search_documents"],
            memory=True,
            temperature=0.3,
            model_name="gpt-3.5-turbo"
        )
        
        # Criar agente personalizado
        custom_agent = BaseAgent(custom_config, rag_system)
        
        # Testar agente personalizado
        test_questions = [
            "Explique o conceito de redes neurais artificiais",
            "Qual a diferença entre supervised e unsupervised learning?",
            "Como funciona o algoritmo de backpropagation?"
        ]
        
        for question in test_questions:
            print(f"\n🎯 Pergunta: {question}")
            
            # Processar pergunta
            response = custom_agent.process(question)
            
            print(f"🤖 Resposta: {response.content}")
            print(f"📊 Confiança: {response.confidence:.2f}")
        
        print("\n✅ Exemplo de agente personalizado concluído!")
        
    except Exception as e:
        print(f"❌ Erro no exemplo personalizado: {str(e)}")

def run_performance_test():
    """Teste de performance dos agentes"""
    print("\n" + "="*60)
    print("⚡ TESTE DE PERFORMANCE")
    print("="*60)
    
    try:
        import time
        
        # Criar sistema RAG
        rag_system = RAGSystem()
        
        # Criar agentes
        agents = {
            "Conversacional": ConversationalAgent(rag_system),
            "Pesquisa": ResearchAgent(rag_system),
            "Executor": TaskExecutorAgent(rag_system)
        }
        
        # Teste de consulta simples
        test_query = "Explique sobre inteligência artificial"
        
        results = {}
        
        for agent_name, agent in agents.items():
            print(f"\n⏱️  Testando {agent_name}...")
            
            start_time = time.time()
            response = agent.process(test_query)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            results[agent_name] = {
                "execution_time": execution_time,
                "confidence": response.confidence,
                "response_length": len(response.content)
            }
            
            print(f"  ⏱️  Tempo: {execution_time:.2f}s")
            print(f"  📊 Confiança: {response.confidence:.2f}")
            print(f"  📝 Tamanho: {len(response.content)} caracteres")
        
        # Resumo dos resultados
        print(f"\n📈 RESUMO DE PERFORMANCE:")
        print("-" * 40)
        
        fastest_agent = min(results.items(), key=lambda x: x[1]["execution_time"])
        most_confident = max(results.items(), key=lambda x: x[1]["confidence"])
        
        print(f"🚀 Mais rápido: {fastest_agent[0]} ({fastest_agent[1]['execution_time']:.2f}s)")
        print(f"🎯 Mais confiante: {most_confident[0]} ({most_confident[1]['confidence']:.2f})")
        
        print("\n✅ Teste de performance concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste de performance: {str(e)}")

def main():
    """Função principal que executa todos os exemplos"""
    print("🤖 SISTEMA DE AGENTES RAG - EXEMPLOS PRÁTICOS")
    print("=" * 60)
    
    # Configurar ambiente
    if not setup_environment():
        return
    
    # Executar exemplos
    examples = [
        ("Agente Conversacional", example_conversational_agent),
        ("Agente de Pesquisa", example_research_agent),
        ("Agente Executor", example_task_executor_agent),
        ("Sistema Multi-Agente", example_multi_agent_system),
        ("Integração RAGFlow", example_ragflow_integration),
        ("Agente Personalizado", example_custom_agent),
        ("Teste de Performance", run_performance_test)
    ]
    
    for name, example_func in examples:
        try:
            print(f"\n🚀 Executando exemplo: {name}")
            example_func()
        except Exception as e:
            print(f"❌ Erro no exemplo {name}: {str(e)}")
            continue
    
    print("\n" + "="*60)
    print("🎉 TODOS OS EXEMPLOS CONCLUÍDOS!")
    print("="*60)
    print("\n📚 Próximos passos:")
    print("  • Experimente com seus próprios documentos")
    print("  • Crie agentes personalizados para suas necessidades")
    print("  • Integre com outros sistemas via API")
    print("  • Otimize os prompts para melhor performance")
    print("  • Configure o sistema para produção")

if __name__ == "__main__":
    main() 