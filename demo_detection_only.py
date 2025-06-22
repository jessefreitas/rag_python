#!/usr/bin/env python3
"""
Demo: Detecção de Dados Pessoais SEM Anonimização
Demonstração das novas funcionalidades implementadas
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from privacy_system import privacy_manager

def demo_basic_detection():
    """Demonstração básica de detecção sem anonimização"""
    print("🔍 DEMO: Detecção de Dados Pessoais SEM Anonimização")
    print("=" * 60)
    
    # Documento de exemplo com dados pessoais
    document = """
    CONTRATO DE PRESTAÇÃO DE SERVIÇOS
    
    CONTRATANTE:
    Nome: João Silva Santos
    CPF: 123.456.789-10
    RG: 12.345.678-9
    E-mail: joao.silva@email.com
    Telefone: (11) 98765-4321
    Endereço: Rua das Flores, 123, CEP: 01234-567, São Paulo, SP
    
    CONTRATADO:
    Empresa ABC Ltda
    CNPJ: 12.345.678/0001-90
    
    Este contrato estabelece os termos para prestação de serviços...
    """
    
    print("📄 Documento Original:")
    print(document)
    
    print("\n🔍 DETECÇÃO SEM ANONIMIZAÇÃO:")
    print("-" * 40)
    
    # 1. Detecção básica
    detection = privacy_manager.detect_personal_data_only(document, detailed=True)
    
    print(f"✅ Dados pessoais detectados: {'SIM' if detection['has_personal_data'] else 'NÃO'}")
    print(f"📂 Categoria de dados: {detection['data_category']}")
    print(f"🔢 Total de ocorrências: {detection['total_occurrences']}")
    print(f"📝 Tipos detectados: {', '.join(detection['detected_types'])}")
    
    print(f"\n📋 Detalhes por tipo de dado:")
    for data_type, details in detection.get('details', {}).items():
        print(f"   {data_type.upper()}:")
        print(f"      Quantidade: {details['count']}")
        print(f"      Exemplos: {details['examples']}")
    
    # 2. Análise de riscos
    print(f"\n⚠️  ANÁLISE DE RISCOS:")
    print("-" * 40)
    
    risk_analysis = privacy_manager.analyze_document_privacy_risks(document)
    
    print(f"🎯 Nível de risco: {risk_analysis['risk_level']}")
    print(f"📊 Score de risco: {risk_analysis['risk_score']}")
    print(f"📝 Descrição: {risk_analysis['risk_description']}")
    print(f"⚖️  Compliance LGPD obrigatório: {'SIM' if risk_analysis['lgpd_compliance_required'] else 'NÃO'}")
    
    print(f"\n💡 Recomendações:")
    for i, recommendation in enumerate(risk_analysis['recommendations'], 1):
        print(f"   {i}. {recommendation}")
    
    # 3. Criação de registro sem anonimização
    print(f"\n📁 CRIAÇÃO DE REGISTRO (sem anonimização):")
    print("-" * 40)
    
    record_info = privacy_manager.create_detection_only_record(
        content=document,
        agent_id="demo_agent",
        purpose="Demonstração de detecção apenas"
    )
    
    print(f"✅ Registro criado: {record_info['record_id'][:8]}...")
    print(f"🔍 Conteúdo original preservado: {record_info['original_content_preserved']}")
    print(f"📅 Criado em: {record_info['created_at']}")
    
    detection_result = record_info['detection_result']
    print(f"📊 Dados detectados: {detection_result['detected_types']}")
    print(f"🔢 Total de ocorrências: {detection_result['total_occurrences']}")
    
    return record_info

def demo_risk_scenarios():
    """Demonstração de diferentes cenários de risco"""
    print(f"\n📊 DEMO: Cenários de Risco de Privacidade")
    print("=" * 60)
    
    scenarios = {
        "🟢 BAIXO RISCO": "Documento público sobre políticas da empresa, sem dados pessoais específicos.",
        
        "🟡 MÉDIO RISCO": """
        Lista de contatos:
        - João (joao@empresa.com)
        - Maria (maria@empresa.com)
        CEP da empresa: 01234-567
        """,
        
        "🟠 ALTO RISCO": """
        Cadastro de funcionário:
        Nome: Carlos Silva
        CPF: 111.222.333-44
        E-mail: carlos@empresa.com
        Telefone: (11) 99999-8888
        """,
        
        "🔴 CRÍTICO": """
        Base de dados de clientes:
        1. Ana Santos - CPF: 123.456.789-10 - RG: 12.345.678-9
        2. Pedro Costa - CPF: 987.654.321-00 - RG: 98.765.432-1
        CNPJ: 12.345.678/0001-90
        """
    }
    
    for scenario_name, content in scenarios.items():
        print(f"\n{scenario_name}")
        print("-" * 30)
        
        risk = privacy_manager.analyze_document_privacy_risks(content)
        
        print(f"🎯 Risco: {risk['risk_level']} (Score: {risk['risk_score']})")
        print(f"📝 {risk['risk_description']}")
        
        if risk['detection_summary']['detected_types']:
            print(f"📊 Dados detectados: {', '.join(risk['detection_summary']['detected_types'])}")
        else:
            print(f"📊 Nenhum dado pessoal detectado")
        
        print(f"💡 Recomendação principal: {risk['recommendations'][0] if risk['recommendations'] else 'Nenhuma'}")

def demo_comparison():
    """Demonstração da diferença entre detecção e anonimização"""
    print(f"\n🔄 DEMO: Comparação Detecção vs Anonimização")
    print("=" * 60)
    
    test_text = "Cliente: Maria Silva (CPF: 123.456.789-10, email: maria@email.com)"
    
    print(f"📄 Texto original:")
    print(f"   {test_text}")
    
    # 1. Apenas detecção (novo)
    print(f"\n🔍 MODO DETECÇÃO APENAS (NOVO):")
    detection = privacy_manager.detect_personal_data_only(test_text)
    print(f"   ✅ Texto preservado: {test_text}")
    print(f"   📊 Dados detectados: {detection['detected_types']}")
    print(f"   🔢 Ocorrências: {detection['total_occurrences']}")
    
    # 2. Com anonimização (existente)
    print(f"\n🔒 MODO COM ANONIMIZAÇÃO (existente):")
    anonymized, mapping = privacy_manager.privacy_compliance.anonymize_text(test_text, method="masking")
    print(f"   🔒 Texto anonimizado: {anonymized}")
    print(f"   🗂️  Mapeamento aplicado: {len(mapping)} substituições")
    
    print(f"\n💡 DIFERENÇA:")
    print(f"   🔍 Detecção apenas: Identifica dados mas PRESERVA o conteúdo original")
    print(f"   🔒 Anonimização: Identifica dados e MODIFICA o conteúdo para proteção")

def main():
    """Função principal da demonstração"""
    try:
        # Demo 1: Funcionalidade básica
        record_info = demo_basic_detection()
        
        # Demo 2: Cenários de risco
        demo_risk_scenarios()
        
        # Demo 3: Comparação de modos
        demo_comparison()
        
        print(f"\n" + "=" * 60)
        print("✅ DEMONSTRAÇÃO CONCLUÍDA!")
        print("🎯 Funcionalidades implementadas:")
        print("   🔍 Detecção de dados pessoais SEM modificação")
        print("   📊 Análise de riscos com score automático")
        print("   💡 Recomendações de compliance LGPD")
        print("   📁 Registros que preservam conteúdo original")
        print("   ⚖️  Transparência total para auditoria")
        
        # Estatísticas finais
        summary = privacy_manager.get_data_summary()
        print(f"\n📋 Estatísticas do sistema:")
        print(f"   📁 Total de registros: {summary['total_records']}")
        print(f"   ✅ Registros ativos: {summary['active_records']}")
        
    except Exception as e:
        print(f"\n❌ ERRO na demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 