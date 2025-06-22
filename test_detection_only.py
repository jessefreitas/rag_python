#!/usr/bin/env python3
"""
Teste do Modo Detecção Apenas - RAG Python
Validação da detecção de dados pessoais SEM anonimização
"""

import os
import sys
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_system_privacy import privacy_agent_system, PrivacyAwareAgent
from privacy_system import privacy_manager

def test_detection_only_functionality():
    """Testa funcionalidades básicas de detecção apenas"""
    print("🔍 Testando funcionalidades de detecção apenas...")
    
    # Documento de teste com vários tipos de dados pessoais
    test_document = """
    RELATÓRIO MÉDICO CONFIDENCIAL
    
    Paciente: Maria Silva Santos
    CPF: 123.456.789-10
    RG: 12.345.678-9
    E-mail: maria.silva@email.com
    Telefone: (11) 98765-4321
    Endereço: Rua das Flores, 123, CEP: 01234-567, São Paulo, SP
    
    CNPJ da Clínica: 12.345.678/0001-90
    
    Diagnóstico: O paciente apresenta sintomas compatíveis com...
    Tratamento recomendado: Medicação específica para...
    """
    
    # 1. Teste básico de detecção
    print("\n📋 1. Teste básico de detecção:")
    detection_result = privacy_manager.detect_personal_data_only(test_document, detailed=True)
    
    print(f"   📊 Dados pessoais detectados: {'SIM' if detection_result['has_personal_data'] else 'NÃO'}")
    print(f"   📂 Categoria: {detection_result['data_category']}")
    print(f"   🔢 Total de ocorrências: {detection_result['total_occurrences']}")
    print(f"   📝 Tipos detectados: {', '.join(detection_result['detected_types'])}")
    
    if detection_result.get('details'):
        print("\n   📋 Detalhes por tipo:")
        for data_type, details in detection_result['details'].items():
            print(f"      {data_type.upper()}: {details['count']} ocorrências")
            print(f"         Exemplos: {details['examples']}")
    
    # 2. Teste de análise de riscos
    print("\n⚠️  2. Análise de riscos de privacidade:")
    risk_analysis = privacy_manager.analyze_document_privacy_risks(test_document)
    
    print(f"   🎯 Nível de risco: {risk_analysis['risk_level']}")
    print(f"   📊 Score de risco: {risk_analysis['risk_score']}")
    print(f"   📝 Descrição: {risk_analysis['risk_description']}")
    print(f"   ⚖️  Compliance LGPD obrigatório: {'SIM' if risk_analysis['lgpd_compliance_required'] else 'NÃO'}")
    
    print("\n   💡 Recomendações:")
    for rec in risk_analysis['recommendations']:
        print(f"      - {rec}")
    
    return detection_result, risk_analysis

def test_detection_only_agent():
    """Testa agente configurado apenas para detecção"""
    print("\n🤖 Testando agente em modo detecção apenas...")
    
    # Cria agente específico para detecção
    detection_agent = privacy_agent_system.create_privacy_agent(
        name="Agente Detecção Jurídica",
        description="Agente que detecta dados pessoais sem anonimizar",
        system_prompt="Você é um assistente jurídico que identifica dados pessoais em documentos.",
        privacy_level="detection_only"
    )
    
    print(f"✅ Agente criado: {detection_agent.name}")
    print(f"   🔧 Modo: {detection_agent.privacy_level}")
    print(f"   🔍 Detecção apenas: {detection_agent.detection_only}")
    print(f"   🔒 Auto-anonimização: {detection_agent.auto_anonymize}")
    
    # Documento de contrato
    contract_content = """
    CONTRATO DE PRESTAÇÃO DE SERVIÇOS ADVOCATÍCIOS
    
    CONTRATANTE:
    Nome: João Carlos da Silva
    CPF: 987.654.321-00
    RG: 98.765.432-1
    E-mail: joao.carlos@empresa.com.br
    Telefone: (21) 99888-7766
    
    CONTRATADO:
    Escritório de Advocacia Silva & Associados
    CNPJ: 98.765.432/0001-10
    Responsável: Dr. Pedro Silva (OAB/SP 123456)
    
    Objeto: Prestação de serviços jurídicos especializados...
    """
    
    # Teste de processamento de documento
    print(f"\n📄 Processando documento com agente de detecção:")
    doc_result = detection_agent.detect_document_data_only(
        content=contract_content,
        filename="contrato_servicos.txt"
    )
    
    if doc_result['success']:
        print(f"   ✅ Documento processado com sucesso")
        print(f"   📁 Arquivo: {doc_result['filename']}")
        print(f"   🔍 Conteúdo original preservado: {doc_result['original_content_preserved']}")
        
        detection = doc_result['detection_result']
        print(f"   📊 Dados detectados: {detection['detected_types']}")
        print(f"   🔢 Total de ocorrências: {detection['total_occurrences']}")
        print(f"   📂 Categoria: {detection['data_category']}")
    else:
        print(f"   ❌ Falha: {doc_result.get('error')}")
    
    # Teste de query
    print(f"\n❓ Testando query com dados pessoais:")
    query = "Analise o contrato do João Carlos (CPF 987.654.321-00) e identifique as cláusulas principais."
    
    query_result = detection_agent.query_with_detection_only(query)
    
    if query_result['success']:
        print(f"   ✅ Query processada")
        print(f"   🔍 Query original preservada: {query_result['privacy_info']['original_query_preserved']}")
        print(f"   📊 Dados detectados na query: {query_result['query_detection']['detected_types']}")
        print(f"   💬 Resposta (primeiros 100 chars): {query_result['response'][:100]}...")
    else:
        print(f"   ❌ Falha: {query_result.get('error')}")
    
    return detection_agent

def test_risk_analysis_scenarios():
    """Testa análise de riscos em diferentes cenários"""
    print("\n📊 Testando análise de riscos em diferentes cenários...")
    
    scenarios = {
        "Documento Seguro": "Este é um documento público sobre políticas da empresa, sem dados pessoais.",
        
        "Baixo Risco": """
        Lista de participantes do evento:
        - João (joao@email.com)
        - Maria (maria@email.com)
        """,
        
        "Médio Risco": """
        Cadastro de cliente:
        Nome: Ana Silva
        E-mail: ana@email.com
        Telefone: (11) 99999-8888
        CEP: 01234-567
        """,
        
        "Alto Risco": """
        Ficha médica:
        Paciente: Carlos Santos
        CPF: 111.222.333-44
        RG: 11.222.333-4
        Telefone: (11) 88888-7777
        Diagnóstico: Diabetes tipo 2
        """,
        
        "Crítico": """
        Base de dados completa:
        1. Maria Silva - CPF: 123.456.789-10 - RG: 12.345.678-9 - Tel: (11) 99999-8888
        2. João Santos - CPF: 987.654.321-00 - RG: 98.765.432-1 - Tel: (21) 88888-7777
        3. Ana Costa - CPF: 555.666.777-88 - RG: 55.666.777-8 - Tel: (31) 77777-6666
        CNPJ Empresa: 12.345.678/0001-90
        """
    }
    
    for scenario_name, content in scenarios.items():
        print(f"\n   📋 Cenário: {scenario_name}")
        
        risk = privacy_manager.analyze_document_privacy_risks(content)
        
        print(f"      🎯 Risco: {risk['risk_level']} (Score: {risk['risk_score']})")
        print(f"      📝 {risk['risk_description']}")
        print(f"      📊 Tipos detectados: {risk['detection_summary']['detected_types']}")
        
        if risk['recommendations']:
            print(f"      💡 Primeira recomendação: {risk['recommendations'][0]}")

def test_comparison_modes():
    """Compara diferentes modos de privacidade"""
    print("\n🔄 Comparando modos de privacidade...")
    
    test_content = """
    Relatório de análise:
    Cliente: Pedro Silva (CPF: 999.888.777-66)
    E-mail: pedro@empresa.com
    Telefone: (11) 95555-4444
    """
    
    # Cria agentes com diferentes modos
    agents = {
        "Standard": privacy_agent_system.create_privacy_agent(
            name="Agente Standard", description="Modo padrão",
            system_prompt="Assistente padrão", privacy_level="standard"
        ),
        "High Privacy": privacy_agent_system.create_privacy_agent(
            name="Agente High", description="Alta privacidade",
            system_prompt="Assistente alta privacidade", privacy_level="high"
        ),
        "Detection Only": privacy_agent_system.create_privacy_agent(
            name="Agente Detection", description="Apenas detecção",
            system_prompt="Assistente detecção", privacy_level="detection_only"
        )
    }
    
    print(f"\n📊 Comparação de processamento:")
    
    for mode_name, agent in agents.items():
        print(f"\n   🤖 {mode_name}:")
        print(f"      🔧 Anonimização automática: {agent.auto_anonymize}")
        print(f"      🔍 Apenas detecção: {agent.detection_only}")
        print(f"      ⚖️  Requer consentimento: {agent.require_consent}")
        
        if agent.detection_only:
            # Usa método específico para detecção
            result = agent.detect_document_data_only(test_content, "test.txt")
            if result['success']:
                print(f"      ✅ Conteúdo original preservado: {result['original_content_preserved']}")
                print(f"      📊 Dados detectados: {result['detection_result']['detected_types']}")
        else:
            # Usa método normal (pode anonimizar)
            result = agent.process_document_with_privacy(
                test_content, "test.txt", user_consent=True
            )
            if result['success']:
                print(f"      🔒 Anonimização aplicada: {result['privacy_info']['anonymization_applied']}")
                print(f"      📊 Dados detectados: {list(result['privacy_info']['detected_data'].keys())}")

def main():
    """Função principal de teste"""
    print("🔍 Iniciando testes do modo Detecção Apenas")
    print("=" * 60)
    print("🎯 Objetivo: Detectar dados pessoais SEM anonimizar")
    print("=" * 60)
    
    try:
        # Teste 1: Funcionalidades básicas
        detection_result, risk_analysis = test_detection_only_functionality()
        
        # Teste 2: Agente específico
        detection_agent = test_detection_only_agent()
        
        # Teste 3: Cenários de risco
        test_risk_analysis_scenarios()
        
        # Teste 4: Comparação de modos
        test_comparison_modes()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES DE DETECÇÃO CONCLUÍDOS!")
        print("🎯 Funcionalidades validadas:")
        print("   🔍 Detecção sem anonimização")
        print("   📊 Análise de riscos de privacidade")
        print("   🤖 Agentes em modo detection_only")
        print("   📋 Preservação do conteúdo original")
        print("   ⚖️  Compliance LGPD com transparência")
        
        # Relatório final
        print(f"\n📋 Resumo dos agentes criados:")
        system_report = privacy_agent_system.get_system_privacy_report()
        detection_agents = [
            agent for agent in privacy_agent_system.agents.values()
            if isinstance(agent, PrivacyAwareAgent) and agent.detection_only
        ]
        
        print(f"   🔍 Agentes detection_only: {len(detection_agents)}")
        print(f"   📁 Total de registros: {system_report['compliance_summary']['total_data_records']}")
        
    except Exception as e:
        print(f"\n❌ ERRO durante os testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 