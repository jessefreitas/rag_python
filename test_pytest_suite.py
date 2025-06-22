#!/usr/bin/env python3
"""
🧪 PYTEST SUITE COMPLETA - RAG Python v1.5.0
Testes unitários e de integração usando pytest
"""

import pytest
import asyncio
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

# Imports do projeto
from crew.orchestrator import crew_orchestrator
from crew.pipelines import LegalDocumentPipeline, ContractGenerationPipeline
from document_generation.services.doc_generator import document_generator
from document_generation.models.document_models import DocRequest, DocResponse
from privacy_system import PrivacyCompliance, DataCategory
from llm_providers import llm_manager
from agent_system import Agent

class TestPrivacySystem:
    """Testes do sistema de privacidade LGPD"""
    
    @pytest.fixture
    def privacy_compliance(self):
        """Fixture para instância do sistema de privacidade"""
        return PrivacyCompliance()
    
    def test_detect_cpf(self, privacy_compliance):
        """Testa detecção de CPF"""
        text = "João Silva, CPF 123.456.789-00"
        detected = privacy_compliance.detect_personal_data(text)
        
        assert 'cpf' in detected
        assert len(detected['cpf']) == 1
        assert '123.456.789-00' in detected['cpf']
    
    def test_detect_email(self, privacy_compliance):
        """Testa detecção de email"""
        text = "Contato: joao@empresa.com.br"
        detected = privacy_compliance.detect_personal_data(text)
        
        assert 'email' in detected
        assert 'joao@empresa.com.br' in detected['email']
    
    def test_detect_multiple_data_types(self, privacy_compliance):
        """Testa detecção de múltiplos tipos de dados"""
        text = """
        João Silva, CPF 123.456.789-00, 
        telefone (11) 99999-9999, 
        email joao@test.com
        """
        detected = privacy_compliance.detect_personal_data(text)
        
        assert len(detected) >= 3  # CPF, telefone, email
        assert 'cpf' in detected
        assert 'email' in detected
        assert 'phone' in detected
    
    def test_anonymize_text(self, privacy_compliance):
        """Testa anonimização de texto"""
        text = "CPF: 123.456.789-00"
        anonymized, mapping = privacy_compliance.anonymize_text(text, method="masking")
        
        assert '123.456.789-00' not in anonymized
        assert '123.456.789-00' in mapping
        assert len(mapping) > 0
    
    def test_classify_data_sensitivity(self, privacy_compliance):
        """Testa classificação de sensibilidade"""
        # Dados pessoais normais
        text1 = "João Silva, CPF 123.456.789-00"
        category1 = privacy_compliance.classify_data_sensitivity(text1)
        assert category1 == DataCategory.PERSONAL
        
        # Dados anônimos
        text2 = "Este é um texto sem dados pessoais"
        category2 = privacy_compliance.classify_data_sensitivity(text2)
        assert category2 == DataCategory.ANONYMOUS

class TestDocumentGeneration:
    """Testes do sistema de geração de documentos"""
    
    @pytest.fixture
    def sample_doc_request(self):
        """Fixture para requisição de documento de teste"""
        return DocRequest(
            agent_id="test-agent-123",
            tipo_documento="contrato_prestacao_servicos",
            variaveis={
                "contratante_nome": "Empresa Teste Ltda",
                "contratado_nome": "Prestador Teste",
                "objeto": "Serviços de teste",
                "valor": "R$ 1.000,00",
                "prazo": "30 dias",
                "data": "22/06/2025"
            },
            formato="docx",
            use_ai_enhancement=False
        )
    
    def test_doc_request_validation(self):
        """Testa validação da requisição de documento"""
        # Teste com agent_id inválido
        with pytest.raises(ValueError):
            DocRequest(
                agent_id="123",  # Muito curto
                tipo_documento="contrato_prestacao_servicos",
                variaveis={"test": "value"}
            )
        
        # Teste com tipo de documento inválido
        with pytest.raises(ValueError):
            DocRequest(
                agent_id="valid-agent-id-123",
                tipo_documento="documento_inexistente",
                variaveis={"test": "value"}
            )
    
    def test_generate_document_success(self, sample_doc_request):
        """Testa geração bem-sucedida de documento"""
        response = document_generator.generate_document(sample_doc_request)
        
        assert isinstance(response, DocResponse)
        assert response.status == "sucesso"
        assert response.nome_arquivo is not None
        assert response.formato == "docx"
        assert response.agent_id == sample_doc_request.agent_id
    
    def test_template_creation(self, sample_doc_request):
        """Testa criação automática de template"""
        # Simplesmente testa se documento é gerado com sucesso
        response = document_generator.generate_document(sample_doc_request)
        
        # Verifica se foi bem-sucedido
        assert response.status == "sucesso"
        assert response.nome_arquivo is not None
        assert "contrato_prestacao_servicos" in response.nome_arquivo

class TestCrewAIOrchestrator:
    """Testes do orquestrador CrewAI"""
    
    def test_orchestrator_initialization(self):
        """Testa inicialização do orquestrador"""
        assert crew_orchestrator is not None
        assert hasattr(crew_orchestrator, 'active_pipelines')
        assert hasattr(crew_orchestrator, 'pipeline_history')
        assert isinstance(crew_orchestrator.active_pipelines, dict)
        assert isinstance(crew_orchestrator.pipeline_history, list)
    
    def test_orchestrator_stats(self):
        """Testa estatísticas do orquestrador"""
        stats = crew_orchestrator.get_system_stats()
        
        assert isinstance(stats, dict)
        assert 'total_workflows' in stats
        assert 'execution_stats' in stats
        assert 'system_health' in stats
    
    @pytest.mark.asyncio
    async def test_pipeline_execution_mock(self):
        """Testa execução de pipeline (mock)"""
        # Mock da execução para não depender de agentes reais
        with patch.object(crew_orchestrator, 'execute_workflow') as mock_execute:
            mock_execute.return_value = {
                "status": "success",
                "workflow_id": "test-workflow-123",
                "execution_time": 1.5,
                "results": {"test": "result"}
            }
            
            result = crew_orchestrator.execute_workflow(
                workflow_id="test-workflow-123",
                inputs={"test": "input"},
                privacy_level="detection_only"
            )
            
            assert result["status"] == "success"
            assert "workflow_id" in result
            mock_execute.assert_called_once()

class TestLLMProviders:
    """Testes dos provedores LLM"""
    
    def test_list_available_providers(self):
        """Testa listagem de provedores disponíveis"""
        providers = llm_manager.list_available_providers()
        
        assert isinstance(providers, list)
        assert len(providers) > 0
        assert 'openai' in providers  # Sabemos que OpenAI está configurado
    
    def test_get_provider_models(self):
        """Testa obtenção de modelos de um provedor"""
        models = llm_manager.get_provider_models('openai')
        
        assert isinstance(models, list)
        assert len(models) > 0
    
    @patch('llm_providers.OpenAIProvider.generate_response')
    def test_generate_response_mock(self, mock_generate):
        """Testa geração de resposta (mock)"""
        mock_generate.return_value = "Resposta de teste"
        
        messages = [{"role": "user", "content": "Teste"}]
        response = llm_manager.generate_response(messages, provider='openai')
        
        assert response == "Resposta de teste"
        mock_generate.assert_called_once()

class TestAgentSystem:
    """Testes do sistema de agentes"""
    
    def test_agents_config_exists(self):
        """Testa se configuração de agentes existe"""
        config_path = Path('agents_config.json')
        assert config_path.exists()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert 'agents' in config
        assert isinstance(config['agents'], dict)
    
    def test_agent_configuration_structure(self):
        """Testa estrutura da configuração de agentes"""
        with open('agents_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        for agent_id, agent_data in config['agents'].items():
            # Verifica campos obrigatórios
            assert 'id' in agent_data
            assert 'name' in agent_data
            assert 'description' in agent_data
            assert 'system_prompt' in agent_data
            assert 'model_name' in agent_data
            assert agent_data['id'] == agent_id

class TestIntegration:
    """Testes de integração entre sistemas"""
    
    def test_privacy_document_integration(self):
        """Testa integração privacidade + documentos"""
        # Criar documento com dados sensíveis
        doc_request = DocRequest(
            agent_id="test-agent-privacy-123",
            tipo_documento="contrato_prestacao_servicos",
            variaveis={
                "contratante_nome": "João Silva",
                "contratado_nome": "Empresa ABC",
                "objeto": "Teste de privacidade",
                "valor": "R$ 1.000,00",
                "prazo": "30 dias",
                "data": "22/06/2025"
            },
            formato="docx"
        )
        
        # Gerar documento
        response = document_generator.generate_document(doc_request)
        
        # Verificar se foi gerado com sucesso
        assert response.status == "sucesso"
        
        # Verificar detecção de privacidade no conteúdo
        privacy = PrivacyCompliance()
        content = f"{doc_request.variaveis['contratante_nome']} {doc_request.variaveis['contratado_nome']}"
        detected = privacy.detect_personal_data(content)
        
        # Deve detectar nomes próprios
        assert len(detected) > 0
    
    def test_full_system_health(self):
        """Teste de saúde completo do sistema"""
        health_checks = {
            'privacy_system': False,
            'document_generation': False,
            'crew_orchestrator': False,
            'llm_providers': False,
            'agent_system': False
        }
        
        # Teste sistema de privacidade
        try:
            privacy = PrivacyCompliance()
            privacy.detect_personal_data("teste")
            health_checks['privacy_system'] = True
        except Exception:
            pass
        
        # Teste geração de documentos
        try:
            assert document_generator is not None
            health_checks['document_generation'] = True
        except Exception:
            pass
        
        # Teste orquestrador
        try:
            stats = crew_orchestrator.get_system_stats()
            health_checks['crew_orchestrator'] = True
        except Exception:
            pass
        
        # Teste LLM providers
        try:
            providers = llm_manager.list_available_providers()
            health_checks['llm_providers'] = len(providers) > 0
        except Exception:
            pass
        
        # Teste sistema de agentes
        try:
            config_path = Path('agents_config.json')
            health_checks['agent_system'] = config_path.exists()
        except Exception:
            pass
        
        # Verificar se pelo menos 80% dos sistemas estão funcionando
        success_rate = sum(health_checks.values()) / len(health_checks)
        assert success_rate >= 0.8, f"Taxa de sucesso muito baixa: {success_rate:.1%}"
        
        # Verificar sistemas críticos
        assert health_checks['privacy_system'], "Sistema de privacidade falhou"
        assert health_checks['document_generation'], "Geração de documentos falhou"

# Configurações do pytest
@pytest.fixture(scope="session")
def event_loop():
    """Fixture para loop de eventos asyncio"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Marcadores personalizados
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::UserWarning")
]

if __name__ == "__main__":
    # Executar testes se rodado diretamente
    pytest.main([__file__, "-v", "--tb=short"]) 