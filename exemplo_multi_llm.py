#!/usr/bin/env python3
"""
Exemplo prático de uso da funcionalidade Multi-LLM
Demonstra como comparar respostas de diferentes provedores de IA
"""

import requests
import json
import time
from typing import Dict, List, Any

class MultiLLMExample:
    """Exemplo de uso da funcionalidade Multi-LLM"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.agent_id = None
        
    def setup_agent(self) -> bool:
        """Configura um agente para os testes"""
        print("🔧 Configurando agente para testes...")
        
        # Criar um agente de teste
        agent_data = {
            "name": "Agente Multi-LLM Teste",
            "description": "Agente para testar comparação de múltiplos LLMs",
            "system_prompt": "Você é um assistente especializado em explicar conceitos técnicos de forma clara e concisa.",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
            "provider": "openai"
        }
        
        try:
            response = requests.post(f"{self.api_base}/agents", json=agent_data)
            if response.status_code == 201:
                result = response.json()
                self.agent_id = result['agent_id']
                print(f"✅ Agente criado com ID: {self.agent_id}")
                return True
            else:
                print(f"❌ Erro ao criar agente: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erro na configuração: {e}")
            return False
    
    def get_existing_agent(self) -> bool:
        """Obtém um agente existente"""
        try:
            response = requests.get(f"{self.api_base}/agents")
            agents = response.json()
            
            if agents:
                self.agent_id = agents[0]['id']
                print(f"✅ Usando agente existente: {agents[0]['name']} (ID: {self.agent_id})")
                return True
            else:
                print("❌ Nenhum agente encontrado")
                return False
        except Exception as e:
            print(f"❌ Erro ao obter agentes: {e}")
            return False
    
    def compare_single_vs_multi(self, question: str):
        """Compara resposta única vs múltiplas respostas"""
        print(f"\n🔄 Comparando: Single LLM vs Multi-LLM")
        print(f"📝 Pergunta: {question}")
        print("-" * 60)
        
        # 1. Resposta única (OpenAI)
        print("\n1️⃣ Resposta Única (OpenAI):")
        try:
            response = requests.post(f"{self.api_base}/agents/{self.agent_id}/query", 
                                   json={"question": question, "use_multi_llm": False})
            result = response.json()
            
            if "error" not in result:
                print(f"   Modelo: {result['model_name']}")
                print(f"   Resposta: {result['response'][:200]}...")
                print(f"   Tamanho: {len(result['response'])} caracteres")
            else:
                print(f"   ❌ Erro: {result['error']}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 2. Respostas múltiplas
        print("\n2️⃣ Respostas Múltiplas:")
        try:
            response = requests.post(f"{self.api_base}/agents/{self.agent_id}/query", 
                                   json={
                                       "question": question,
                                       "use_multi_llm": True,
                                       "providers": ["openai", "openrouter"]
                                   })
            result = response.json()
            
            if "error" not in result:
                print(f"   Provedores usados: {result['providers_used']}")
                
                for provider, response_data in result['responses'].items():
                    print(f"\n   📡 {provider.upper()}:")
                    print(f"      Modelo: {response_data['model']}")
                    print(f"      Resposta: {response_data['response'][:150]}...")
                    print(f"      Tamanho: {len(response_data['response'])} caracteres")
                
                # Estatísticas de comparação
                if result.get('comparison'):
                    comparison = result['comparison']
                    print(f"\n   📊 Estatísticas:")
                    print(f"      Respostas únicas: {comparison['unique_responses']}")
                    print(f"      Tamanhos: {comparison['response_lengths']}")
            else:
                print(f"   ❌ Erro: {result['error']}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    def test_different_question_types(self):
        """Testa diferentes tipos de perguntas"""
        questions = [
            {
                "category": "Conceitos Básicos",
                "question": "O que é inteligência artificial?"
            },
            {
                "category": "Técnico",
                "question": "Explique o que é um algoritmo de machine learning."
            },
            {
                "category": "Comparativo",
                "question": "Qual a diferença entre supervised e unsupervised learning?"
            },
            {
                "category": "Aplicação Prática",
                "question": "Como a IA pode ser aplicada na medicina?"
            },
            {
                "category": "Complexo",
                "question": "Explique o funcionamento de uma rede neural convolucional para processamento de imagens."
            }
        ]
        
        print(f"\n🧪 Testando Diferentes Tipos de Perguntas")
        print("=" * 60)
        
        for i, q_data in enumerate(questions, 1):
            print(f"\n{i}. {q_data['category']}: {q_data['question']}")
            
            try:
                response = requests.post(f"{self.api_base}/agents/{self.agent_id}/query", 
                                       json={
                                           "question": q_data['question'],
                                           "use_multi_llm": True,
                                           "providers": ["openai", "openrouter"]
                                       })
                result = response.json()
                
                if "error" not in result:
                    # Comparar tamanhos
                    lengths = result['comparison']['response_lengths']
                    longest = max(lengths, key=lengths.get)
                    shortest = min(lengths, key=lengths.get)
                    
                    print(f"   ✅ Respostas obtidas de {len(result['responses'])} provedores")
                    print(f"   📏 Tamanhos: {lengths}")
                    print(f"   📈 Mais detalhada: {longest} ({lengths[longest]} chars)")
                    print(f"   📉 Mais concisa: {shortest} ({lengths[shortest]} chars)")
                    
                    # Verificar se as respostas são únicas
                    unique_count = result['comparison']['unique_responses']
                    if unique_count > 1:
                        print(f"   🔄 Respostas diferentes: {unique_count} versões únicas")
                    else:
                        print(f"   🔄 Respostas similares: {unique_count} versão única")
                else:
                    print(f"   ❌ Erro: {result['error']}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
            
            # Pausa entre perguntas
            time.sleep(2)
    
    def test_provider_specific_analysis(self):
        """Análise específica por provedor"""
        print(f"\n🔍 Análise Específica por Provedor")
        print("=" * 60)
        
        question = "Explique o conceito de overfitting em machine learning."
        
        providers = ["openai", "openrouter"]
        
        for provider in providers:
            print(f"\n📡 Analisando {provider.upper()}:")
            
            try:
                response = requests.post(f"{self.api_base}/agents/{self.agent_id}/query", 
                                       json={
                                           "question": question,
                                           "use_multi_llm": True,
                                           "providers": [provider]
                                       })
                result = response.json()
                
                if "error" not in result and provider in result['responses']:
                    response_data = result['responses'][provider]
                    
                    # Análise da resposta
                    response_text = response_data['response']
                    word_count = len(response_text.split())
                    sentence_count = response_text.count('.') + response_text.count('!') + response_text.count('?')
                    
                    print(f"   Modelo: {response_data['model']}")
                    print(f"   Palavras: {word_count}")
                    print(f"   Frases: {sentence_count}")
                    print(f"   Caracteres: {len(response_text)}")
                    print(f"   Média palavras/frase: {word_count/sentence_count:.1f}" if sentence_count > 0 else "   Média palavras/frase: N/A")
                    
                    # Identificar características da resposta
                    if "overfitting" in response_text.lower():
                        print(f"   ✅ Menciona o termo 'overfitting'")
                    if "training" in response_text.lower():
                        print(f"   ✅ Menciona 'training'")
                    if "validation" in response_text.lower():
                        print(f"   ✅ Menciona 'validation'")
                        
                else:
                    print(f"   ❌ Erro ou provedor não disponível")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    def test_feedback_system(self):
        """Testa o sistema de feedback"""
        print(f"\n👍 Testando Sistema de Feedback")
        print("=" * 60)
        
        question = "O que é deep learning?"
        
        try:
            # Fazer consulta
            response = requests.post(f"{self.api_base}/agents/{self.agent_id}/query", 
                                   json={
                                       "question": question,
                                       "use_multi_llm": True,
                                       "providers": ["openai", "openrouter"]
                                   })
            result = response.json()
            
            if "error" not in result:
                print(f"📝 Pergunta: {question}")
                print(f"📡 Provedores: {result['providers_used']}")
                
                # Enviar feedback para cada resposta
                for provider, response_data in result['responses'].items():
                    print(f"\n   Avaliando {provider.upper()}:")
                    
                    # Simular avaliação baseada no tamanho da resposta
                    response_length = len(response_data['response'])
                    if response_length > 200:
                        rating = "good"
                        reason = "resposta detalhada"
                    else:
                        rating = "bad"
                        reason = "resposta muito curta"
                    
                    # Enviar feedback
                    feedback_response = requests.post(f"{self.api_base}/agents/{self.agent_id}/feedback", 
                                                    json={
                                                        "user_input": question,
                                                        "agent_response": response_data['response'],
                                                        "rating": rating,
                                                        "provider": provider
                                                    })
                    
                    if feedback_response.json().get('success'):
                        print(f"   ✅ Feedback {rating} enviado ({reason})")
                    else:
                        print(f"   ❌ Erro ao enviar feedback")
                        
            else:
                print(f"❌ Erro na consulta: {result['error']}")
                
        except Exception as e:
            print(f"❌ Erro no teste de feedback: {e}")
    
    def run_complete_demo(self):
        """Executa demonstração completa"""
        print("🚀 Demonstração Completa - Sistema Multi-LLM")
        print("=" * 70)
        
        # Verificar se o servidor está rodando
        try:
            response = requests.get(f"{self.base_url}/")
            print("✅ Servidor está rodando")
        except Exception as e:
            print(f"❌ Servidor não está rodando: {e}")
            print("   Execute: python web_agent_manager.py")
            return
        
        # Configurar agente
        if not self.get_existing_agent():
            if not self.setup_agent():
                return
        
        # Executar testes
        self.compare_single_vs_multi("Explique o que é machine learning em termos simples.")
        self.test_different_question_types()
        self.test_provider_specific_analysis()
        self.test_feedback_system()
        
        print(f"\n" + "=" * 70)
        print("🎉 Demonstração concluída!")
        print("\n💡 Próximos passos:")
        print("   - Acesse http://localhost:5000 para usar a interface web")
        print("   - Teste diferentes combinações de provedores")
        print("   - Monitore as estatísticas no dashboard")
        print("   - Use o sistema de feedback para melhorar as respostas")

def main():
    """Função principal"""
    demo = MultiLLMExample()
    demo.run_complete_demo()

if __name__ == "__main__":
    main() 