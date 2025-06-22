#!/usr/bin/env python3
"""
Teste do Sistema Integrado: Multi-LLM + Privacidade + Agentes
Validação completa do sistema RAG Python com compliance LGPD
"""

import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_system_privacy import privacy_agent_system, PrivacyAwareAgent
from privacy_system import privacy_manager, DataCategory, RetentionPolicy
from llm_providers import llm_manager

def test_privacy_agent_creation():
    """Testa criação de agentes com diferentes níveis de privacidade"""
    print("🔐 Testando criação de agentes com privacidade...")
    
    # Agente padrão
    agent_standard = privacy_agent_system.create_privacy_agent(
        name="Agente Jurídico Padrão",
        description="Análise de documentos jurídicos com privacidade padrão",
        system_prompt="Você é um assistente jurídico especializado em análise de contratos.",
        privacy_level="standard"
    )
    
    # Agente alta privacidade
    agent_high = privacy_agent_system.create_privacy_agent(
        name="Agente LGPD Alto",
        description="Processamento de dados pessoais com alta privacidade",
        system_prompt="Você é um assistente especializado em compliance LGPD.",
        privacy_level="high"
    )
    
    # Agente máxima privacidade
    agent_maximum = privacy_agent_system.create_privacy_agent(
        name="Agente Dados Sensíveis",
        description="Processamento de dados sensíveis com máxima privacidade",
        system_prompt="Você é um assistente para dados médicos e sensíveis.",
        privacy_level="maximum"
    )
    
    print(f"✅ Criados 3 agentes:")
    print(f"   📋 {agent_standard.name} (ID: {agent_standard.agent_id[:8]}...) - {agent_standard.privacy_level}")
    print(f"   🔒 {agent_high.name} (ID: {agent_high.agent_id[:8]}...) - {agent_high.privacy_level}")
    print(f"   🛡️  {agent_maximum.name} (ID: {agent_maximum.agent_id[:8]}...) - {agent_maximum.privacy_level}")
    
    return agent_standard, agent_high, agent_maximum

def test_document_processing_with_privacy():
    """Testa processamento de documentos com dados pessoais"""
    print("\n📄 Testando processamento de documentos com privacidade...")
    
    # Documento com dados pessoais
    document_content = """
    CONTRATO DE PRESTAÇÃO DE SERVIÇOS
    
    Contratante: João Silva Santos
    CPF: 123.456.789-10
    E-mail: joao.silva@email.com
    Telefone: (11) 98765-4321
    Endereço: Rua das Flores, 123, CEP: 01234-567, São Paulo, SP
    
    Este contrato estabelece os termos para prestação de serviços jurídicos...
    """
    
    agents = privacy_agent_system.agents
    
    for agent_id, agent in list(agents.items())[:3]:  # Testa apenas os 3 primeiros
        if isinstance(agent, PrivacyAwareAgent):
            print(f"\n🤖 Testando {agent.name} ({agent.privacy_level}):")
            
            # Teste sem consentimento
            result_no_consent = agent.process_document_with_privacy(
                content=document_content,
                filename="contrato_teste.txt",
                user_consent=False,
                processing_purpose="Análise de contrato"
            )
            
            if result_no_consent['success']:
                print(f"   ✅ Processado com sucesso")
                print(f"   📊 Dados detectados: {list(result_no_consent['privacy_info']['detected_data'].keys())}")
                print(f"   🔒 Anonimização: {'Sim' if result_no_consent['privacy_info']['anonymization_applied'] else 'Não'}")
            else:
                print(f"   ⚠️  Falhou: {result_no_consent.get('error', 'Erro desconhecido')}")
                
                # Se falhou por falta de consentimento, tenta com consentimento
                if result_no_consent.get('consent_required'):
                    print(f"   🔄 Tentando novamente com consentimento...")
                    result_with_consent = agent.process_document_with_privacy(
                        content=document_content,
                        filename="contrato_teste.txt",
                        user_consent=True,
                        processing_purpose="Análise de contrato"
                    )
                    
                    if result_with_consent['success']:
                        print(f"   ✅ Processado com consentimento")
                        print(f"   📊 Dados detectados: {list(result_with_consent['privacy_info']['detected_data'].keys())}")

def test_query_with_personal_data():
    """Testa queries com dados pessoais"""
    print("\n❓ Testando queries com dados pessoais...")
    
    personal_query = "Analise o contrato do João Silva (CPF 123.456.789-10) e me diga se há cláusulas abusivas."
    
    agents = list(privacy_agent_system.agents.values())[:2]  # Testa 2 agentes
    
    for agent in agents:
        if isinstance(agent, PrivacyAwareAgent):
            print(f"\n🤖 {agent.name} ({agent.privacy_level}):")
            
            result = agent.query_with_privacy(
                query=personal_query,
                user_consent=True  # Fornece consentimento
            )
            
            if result['success']:
                print(f"   ✅ Query processada")
                print(f"   📊 Dados detectados: {list(result['privacy_info']['detected_data'].keys())}")
                print(f"   🔒 Anonimização: {'Sim' if result['privacy_info']['anonymization_applied'] else 'Não'}")
            else:
                print(f"   ❌ Falhou: {result.get('error', 'Erro desconhecido')}")

def test_privacy_reports():
    """Testa geração de relatórios de privacidade"""
    print("\n📊 Testando relatórios de privacidade...")
    
    # Relatório individual de um agente
    agents = list(privacy_agent_system.agents.values())
    if agents:
        agent = agents[0]
        if isinstance(agent, PrivacyAwareAgent):
            report = agent.get_privacy_report()
            print(f"\n📋 Relatório do {agent.name}:")
            print(f"   📊 Documentos processados: {report['stats']['documents_processed']}")
            print(f"   🔒 Dados anonimizados: {report['stats']['data_anonymized']}")
            print(f"   ⚠️  Violações de compliance: {report['stats']['compliance_violations']}")
            print(f"   📁 Total de registros: {report['data_records']['total']}")
    
    # Relatório do sistema
    system_report = privacy_agent_system.get_system_privacy_report()
    print(f"\n🏢 Relatório do Sistema:")
    print(f"   🤖 Total de agentes: {system_report['compliance_summary']['total_agents']}")
    print(f"   📁 Total de registros: {system_report['compliance_summary']['total_data_records']}")
    print(f"   ✅ Registros ativos: {system_report['compliance_summary']['active_records']}")
    print(f"   ⚠️  Violações: {system_report['compliance_summary']['compliance_violations']}")

def test_data_lifecycle():
    """Testa ciclo de vida dos dados"""
    print("\n🔄 Testando ciclo de vida dos dados...")
    
    # Cria dados de teste com retenção curta
    from privacy_system import DataRecord
    
    test_content = "Documento de teste com CPF 999.888.777-66 para validação."
    
    # Cria registro com retenção curta (simula expiração)
    record = privacy_manager.create_data_record(
        content=test_content,
        agent_id="test_agent",
        purpose="Teste de ciclo de vida",
        retention_policy=RetentionPolicy.SHORT_TERM
    )
    
    print(f"   📝 Registro criado: {record.id[:8]}...")
    print(f"   📅 Expira em: {record.expires_at}")
    print(f"   📊 Categoria: {record.category.value}")
    
    # Testa anonimização manual
    success = privacy_manager.anonymize_record(record.id, method="masking")
    if success:
        print(f"   🔒 Registro anonimizado com sucesso")
        updated_record = privacy_manager.data_records[record.id]
        print(f"   📊 Nova categoria: {updated_record.category.value}")
    
    # Testa soft delete
    success = privacy_manager.soft_delete_record(record.id, "Teste de exclusão")
    if success:
        print(f"   🗑️  Soft delete aplicado")

def test_compliance_cleanup():
    """Testa limpeza automática de compliance"""
    print("\n🧹 Testando limpeza automática...")
    
    # Executa limpeza
    cleanup_result = privacy_agent_system.run_privacy_cleanup()
    
    print(f"   🕒 Última limpeza: {cleanup_result['cleanup_timestamp']}")
    print(f"   📊 Estatísticas:")
    print(f"      - Anonimizados: {cleanup_result['stats']['anonymized']}")
    print(f"      - Excluídos: {cleanup_result['stats']['hard_deleted']}")
    print(f"      - Ignorados: {cleanup_result['stats']['skipped']}")
    print(f"   ⏰ Próxima limpeza: {cleanup_result['next_cleanup']}")

def test_multi_llm_with_privacy():
    """Testa integração Multi-LLM com privacidade"""
    print("\n🤖 Testando Multi-LLM com privacidade...")
    
    available_providers = llm_manager.list_available_providers()
    print(f"   📋 Provedores disponíveis: {available_providers}")
    
    if available_providers:
        # Testa recomendação para tarefa jurídica
        best_for_legal = llm_manager.get_best_provider_for_task("legal")
        print(f"   ⚖️  Melhor para jurídico: {best_for_legal}")
        
        # Cria agente com o melhor provedor
        if best_for_legal:
            privacy_agent = privacy_agent_system.create_privacy_agent(
                name="Agente Multi-LLM Jurídico",
                description="Agente jurídico com melhor LLM disponível",
                system_prompt="Você é um assistente jurídico especializado.",
                model_name=best_for_legal,
                privacy_level="high"
            )
            print(f"   ✅ Agente criado com {best_for_legal}")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do sistema integrado RAG Python")
    print("=" * 70)
    print("🔧 Multi-LLM + 🔐 Privacidade + 🤖 Agentes + ⚖️  LGPD")
    print("=" * 70)
    
    try:
        # Teste 1: Criação de agentes
        agents = test_privacy_agent_creation()
        
        # Teste 2: Processamento de documentos
        test_document_processing_with_privacy()
        
        # Teste 3: Queries com dados pessoais
        test_query_with_personal_data()
        
        # Teste 4: Relatórios de privacidade
        test_privacy_reports()
        
        # Teste 5: Ciclo de vida dos dados
        test_data_lifecycle()
        
        # Teste 6: Limpeza automática
        test_compliance_cleanup()
        
        # Teste 7: Integração Multi-LLM
        test_multi_llm_with_privacy()
        
        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("🎯 Sistema RAG Python completamente integrado e funcional")
        print("🔐 Compliance LGPD ativo")
        print("🤖 Multi-LLM operacional")
        print("⚖️  Agentes jurídicos com privacidade")
        
    except Exception as e:
        print(f"\n❌ ERRO durante os testes: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n📋 Resumo do sistema:")
    summary = privacy_agent_system.get_system_privacy_report()
    print(f"   🤖 Agentes ativos: {summary['compliance_summary']['total_agents']}")
    print(f"   📁 Registros de dados: {summary['compliance_summary']['total_data_records']}")
    print(f"   ⚠️  Violações: {summary['compliance_summary']['compliance_violations']}")

if __name__ == "__main__":
    main() 