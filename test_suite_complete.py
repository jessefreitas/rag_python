#!/usr/bin/env python3
"""
Suite Completa de Testes - RAG Python v1.3.0
Testes automatizados para validação de todo o sistema
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports do sistema
from privacy_system import privacy_manager, DataCategory, RetentionPolicy
from llm_providers import LLMProviderManager
from rag_system import RAGSystem

class TestPrivacySystem(unittest.TestCase):
    """Testes do sistema de privacidade"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        # Limpa registros existentes para testes isolados
        privacy_manager.data_records.clear()
    
    def test_detect_personal_data_only(self):
        """Testa detecção sem anonimização"""
        test_content = "João Silva, CPF: 123.456.789-10, email: joao@test.com"
        
        result = privacy_manager.detect_personal_data_only(test_content, detailed=True)
        
        self.assertTrue(result['has_personal_data'])
        self.assertIn('cpf', result['detected_types'])
        self.assertIn('email', result['detected_types'])
        self.assertIn('nome_proprio', result['detected_types'])
        self.assertEqual(result['total_occurrences'], 3)
    
    def test_risk_analysis(self):
        """Testa análise de riscos"""
        high_risk_content = """
        Paciente: Maria Silva
        CPF: 123.456.789-10
        RG: 12.345.678-9
        Telefone: (11) 99999-8888
        """
        
        risk = privacy_manager.analyze_document_privacy_risks(high_risk_content)
        
        self.assertIn(risk['risk_level'], ['ALTO', 'CRÍTICO'])
        self.assertTrue(risk['lgpd_compliance_required'])
        self.assertGreater(len(risk['recommendations']), 0)
    
    def test_create_detection_only_record(self):
        """Testa criação de registro sem anonimização"""
        content = "Cliente: Pedro (CPF: 999.888.777-66)"
        
        record_info = privacy_manager.create_detection_only_record(
            content=content,
            agent_id="test_agent",
            purpose="Teste unitário"
        )
        
        self.assertTrue(record_info['original_content_preserved'])
        self.assertIn('record_id', record_info)
        self.assertEqual(len(privacy_manager.data_records), 1)
        
        # Verifica se o conteúdo original foi preservado
        record = privacy_manager.data_records[record_info['record_id']]
        self.assertEqual(record.content, content)
    
    def test_data_lifecycle(self):
        """Testa ciclo de vida completo dos dados"""
        content = "Teste: Maria (email: maria@test.com)"
        
        # Criar registro
        record_info = privacy_manager.create_detection_only_record(
            content=content,
            agent_id="lifecycle_test",
            purpose="Teste de ciclo de vida"
        )
        
        record_id = record_info['record_id']
        
        # Verificar criação
        self.assertIn(record_id, privacy_manager.data_records)
        
        # Soft delete
        privacy_manager.delete_data_record(record_id, hard_delete=False)
        record = privacy_manager.data_records[record_id]
        self.assertTrue(record.is_deleted)
        
        # Hard delete
        privacy_manager.delete_data_record(record_id, hard_delete=True)
        self.assertNotIn(record_id, privacy_manager.data_records)

class TestLLMProviders(unittest.TestCase):
    """Testes do sistema Multi-LLM"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.llm_manager = LLMProviderManager()
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'OPENROUTER_API_KEY': 'test_key',
        'GOOGLE_API_KEY': 'test_key',
        'DEEPSEEK_API_KEY': 'test_key'
    })
    def test_provider_initialization(self):
        """Testa inicialização dos provedores"""
        providers = self.llm_manager.get_available_providers()
        
        expected_providers = ['openai', 'openrouter', 'google', 'deepseek']
        for provider in expected_providers:
            self.assertIn(provider, providers)
    
    def test_get_best_provider_for_task(self):
        """Testa recomendação de melhor provedor"""
        recommendations = {
            'general': self.llm_manager.get_best_provider_for_task('general'),
            'coding': self.llm_manager.get_best_provider_for_task('coding'),
            'creative': self.llm_manager.get_best_provider_for_task('creative'),
            'analysis': self.llm_manager.get_best_provider_for_task('analysis'),
            'legal': self.llm_manager.get_best_provider_for_task('legal')
        }
        
        for task, recommendation in recommendations.items():
            self.assertIn('provider', recommendation)
            self.assertIn('model', recommendation)
            self.assertIn('reason', recommendation)
    
    @patch('llm_providers.LLMProviderManager.query_provider')
    def test_compare_multi_llm(self, mock_query):
        """Testa comparação entre múltiplos LLMs"""
        # Mock das respostas
        mock_query.side_effect = [
            ("Resposta OpenAI", 1.2),
            ("Resposta Google", 0.8),
            ("Resposta DeepSeek", 1.5)
        ]
        
        providers = ['openai', 'google', 'deepseek']
        query = "Teste de comparação"
        
        results = self.llm_manager.compare_multi_llm(query, providers)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIn('provider', result)
            self.assertIn('response', result)
            self.assertIn('response_time', result)

class TestRAGSystem(unittest.TestCase):
    """Testes do sistema RAG"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.rag_system = RAGSystem(
            agent_id="test_agent",
            vector_db_path=os.path.join(self.temp_dir, "test_db")
        )
    
    def tearDown(self):
        """Limpeza após cada teste"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_document(self):
        """Testa adição de documento"""
        test_content = "Este é um documento de teste para o sistema RAG."
        
        result = self.rag_system.add_document(
            content=test_content,
            metadata={"source": "test", "type": "text"}
        )
        
        self.assertTrue(result)
    
    def test_query_system(self):
        """Testa consulta ao sistema"""
        # Adiciona documento primeiro
        test_content = "Python é uma linguagem de programação versátil."
        self.rag_system.add_document(test_content, {"source": "test"})
        
        # Testa consulta
        with patch('llm_providers.LLMProviderManager.query_provider') as mock_query:
            mock_query.return_value = ("Resposta sobre Python", 1.0)
            
            response = self.rag_system.query(
                "O que é Python?",
                provider="openai"
            )
            
            self.assertIsNotNone(response)

class TestSystemIntegration(unittest.TestCase):
    """Testes de integração do sistema completo"""
    
    def test_privacy_rag_integration(self):
        """Testa integração entre sistema de privacidade e RAG"""
        # Conteúdo com dados pessoais
        content_with_pii = "Relatório do cliente João Silva (CPF: 123.456.789-10)"
        
        # Detecta dados pessoais
        detection = privacy_manager.detect_personal_data_only(content_with_pii)
        self.assertTrue(detection['has_personal_data'])
        
        # Cria registro preservando original
        record_info = privacy_manager.create_detection_only_record(
            content=content_with_pii,
            agent_id="integration_test",
            purpose="Teste de integração"
        )
        
        self.assertTrue(record_info['original_content_preserved'])
        
        # Verifica se pode ser usado no RAG (conteúdo original preservado)
        record = privacy_manager.data_records[record_info['record_id']]
        self.assertEqual(record.content, content_with_pii)
    
    def test_multi_llm_privacy_integration(self):
        """Testa integração Multi-LLM com sistema de privacidade"""
        query_with_pii = "Analise o contrato do João (CPF: 999.888.777-66)"
        
        # Detecta dados na query
        detection = privacy_manager.detect_personal_data_only(query_with_pii)
        self.assertTrue(detection['has_personal_data'])
        
        # Registra query preservando original
        record_info = privacy_manager.create_detection_only_record(
            content=query_with_pii,
            agent_id="multi_llm_test",
            purpose="Query com dados pessoais"
        )
        
        # Verifica que pode usar query original com LLMs se necessário
        self.assertTrue(record_info['original_content_preserved'])

class TestSystemPerformance(unittest.TestCase):
    """Testes de performance do sistema"""
    
    def test_detection_performance(self):
        """Testa performance da detecção de dados"""
        # Documento grande com múltiplos dados pessoais
        large_content = "\n".join([
            f"Cliente {i}: João Silva {i} (CPF: 123.456.{i:03d}-10, email: joao{i}@test.com)"
            for i in range(100)
        ])
        
        start_time = datetime.now()
        detection = privacy_manager.detect_personal_data_only(large_content)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        # Deve processar em menos de 5 segundos
        self.assertLess(processing_time, 5.0)
        self.assertTrue(detection['has_personal_data'])
        self.assertEqual(detection['total_occurrences'], 300)  # 100 * 3 tipos

def run_all_tests():
    """Executa todos os testes"""
    print("🧪 Iniciando Suite Completa de Testes - RAG Python v1.3.0")
    print("=" * 60)
    
    # Cria suite de testes
    test_classes = [
        TestPrivacySystem,
        TestLLMProviders, 
        TestRAGSystem,
        TestSystemIntegration,
        TestSystemPerformance
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Executa testes
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True
    )
    
    print(f"\n🔍 Executando {suite.countTestCases()} testes...")
    result = runner.run(suite)
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("✅ TODOS OS TESTES PASSARAM!")
        print(f"   🎯 {result.testsRun} testes executados com sucesso")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print(f"   📊 {result.testsRun} testes executados")
        print(f"   ❌ {len(result.failures)} falhas")
        print(f"   🚫 {len(result.errors)} erros")
        
        if result.failures:
            print("\n📋 FALHAS:")
            for test, traceback in result.failures:
                print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\n🚫 ERROS:")
            for test, traceback in result.errors:
                print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 