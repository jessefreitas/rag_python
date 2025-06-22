#!/usr/bin/env python3
"""
🚀 TESTE INTEGRAÇÃO COMPLETA v1.5.0
RAG Python - CrewAI + Documentos + Privacidade + LLM
"""

import json
import traceback
from datetime import datetime

def test_complete_integration():
    """Teste completo de integração de todos os sistemas"""
    
    print("🚀 === TESTE INTEGRAÇÃO COMPLETA v1.5.0 ===")
    print(f"📅 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.5.0",
        "tests": {}
    }
    
    # 1. TESTE DE IMPORTS
    print("\n1️⃣ === TESTE DE IMPORTS ===")
    try:
        from crew.orchestrator import crew_orchestrator
        from crew.pipelines import LegalDocumentPipeline, ContractGenerationPipeline
        from document_generation.services.doc_generator import document_generator
        from document_generation.models.document_models import DocRequest
        from privacy_system import PrivacyCompliance
        from llm_providers import llm_manager
        from agent_system import Agent
        
        print("✅ Todos os módulos importados com sucesso!")
        results["tests"]["imports"] = {"status": "success", "message": "All modules imported"}
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        results["tests"]["imports"] = {"status": "error", "message": str(e)}
        return results
    
    # 2. TESTE SISTEMA DE PRIVACIDADE
    print("\n2️⃣ === TESTE SISTEMA LGPD ===")
    try:
        privacy = PrivacyCompliance()
        test_text = """
        Contrato de João Silva, CPF 123.456.789-00, 
        telefone (11) 99999-9999, email joao@test.com,
        RG 12.345.678-9, CEP 01234-567
        """
        
        detected = privacy.detect_personal_data(test_text)
        total_found = sum(len(values) for values in detected.values())
        
        print(f"✅ Sistema LGPD funcionando!")
        print(f"   - Dados detectados: {total_found}")
        for data_type, values in detected.items():
            print(f"   - {data_type}: {len(values)} encontrados")
            
        results["tests"]["privacy"] = {
            "status": "success", 
            "data_types_found": len(detected),
            "total_items": total_found
        }
        
    except Exception as e:
        print(f"❌ Erro sistema LGPD: {e}")
        results["tests"]["privacy"] = {"status": "error", "message": str(e)}
    
    # 3. TESTE ORQUESTRADOR CREWAI
    print("\n3️⃣ === TESTE ORQUESTRADOR CREWAI ===")
    try:
        active_pipelines = len(crew_orchestrator.active_pipelines)
        history_count = len(crew_orchestrator.pipeline_history)
        
        print(f"✅ Orquestrador CrewAI funcionando!")
        print(f"   - Pipelines ativos: {active_pipelines}")
        print(f"   - Histórico: {history_count}")
        
        results["tests"]["orchestrator"] = {
            "status": "success",
            "active_pipelines": active_pipelines,
            "history_count": history_count
        }
        
    except Exception as e:
        print(f"❌ Erro orquestrador: {e}")
        results["tests"]["orchestrator"] = {"status": "error", "message": str(e)}
    
    # 4. TESTE LLM PROVIDERS
    print("\n4️⃣ === TESTE LLM PROVIDERS ===")
    try:
        providers = llm_manager.list_available_providers()
        print(f"✅ LLM Providers funcionando!")
        print(f"   - Providers disponíveis: {len(providers)}")
        for provider in providers:
            print(f"   - {provider}")
            
        results["tests"]["llm_providers"] = {
            "status": "success",
            "provider_count": len(providers),
            "providers": providers
        }
        
    except Exception as e:
        print(f"❌ Erro LLM providers: {e}")
        results["tests"]["llm_providers"] = {"status": "error", "message": str(e)}
    
    # 5. TESTE GERAÇÃO DE DOCUMENTOS
    print("\n5️⃣ === TESTE GERAÇÃO DE DOCUMENTOS ===")
    try:
        # Criar requisição de teste
        doc_request = DocRequest(
            agent_id="05b9bd04-28bc-4a1c-aa76-a2161b1ed1ac",
            tipo_documento="contrato_prestacao_servicos",
            variaveis={
                "contratante_nome": "Teste Empresa Ltda",
                "contratado_nome": "Teste Prestador",
                "objeto": "Teste de integração v1.5.0",
                "valor": "R$ 1.000,00",
                "prazo": "30 dias",
                "data": datetime.now().strftime("%d/%m/%Y")
            },
            formato="docx",
            use_ai_enhancement=False
        )
        
        # Gerar documento
        doc_response = document_generator.generate_document(doc_request)
        
        print(f"✅ Geração de documentos funcionando!")
        print(f"   - Documento: {doc_response.nome_arquivo}")
        print(f"   - Status: {doc_response.status}")
        print(f"   - Formato: {doc_response.formato}")
        
        results["tests"]["document_generation"] = {
            "status": "success",
            "document_name": doc_response.nome_arquivo,
            "document_status": doc_response.status,
            "format": doc_response.formato
        }
        
    except Exception as e:
        print(f"❌ Erro geração documentos: {e}")
        results["tests"]["document_generation"] = {"status": "error", "message": str(e)}
    
    # 6. TESTE AGENTES
    print("\n6️⃣ === TESTE SISTEMA DE AGENTES ===")
    try:
        # Verificar se existe agente configurado
        import json
        with open('agents_config.json', 'r', encoding='utf-8') as f:
            agents_config = json.load(f)
        
        agent_count = len(agents_config.get('agents', {}))
        print(f"✅ Sistema de agentes funcionando!")
        print(f"   - Agentes configurados: {agent_count}")
        
        for agent_id, agent_data in agents_config.get('agents', {}).items():
            print(f"   - {agent_data['name']}: {agent_data['document_count']} documentos")
        
        results["tests"]["agents"] = {
            "status": "success",
            "agent_count": agent_count
        }
        
    except Exception as e:
        print(f"❌ Erro sistema agentes: {e}")
        results["tests"]["agents"] = {"status": "error", "message": str(e)}
    
    # 7. RESUMO FINAL
    print("\n" + "=" * 60)
    print("📊 === RESUMO FINAL ===")
    
    success_count = sum(1 for test in results["tests"].values() if test["status"] == "success")
    total_tests = len(results["tests"])
    
    print(f"✅ Testes bem-sucedidos: {success_count}/{total_tests}")
    print(f"📈 Taxa de sucesso: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("\n🎉 TODOS OS SISTEMAS FUNCIONANDO PERFEITAMENTE!")
        print("🚀 RAG Python v1.5.0 PRONTO PARA PRODUÇÃO!")
        results["overall_status"] = "success"
    else:
        print(f"\n⚠️  {total_tests - success_count} sistema(s) com problemas")
        print("🔧 Verificar logs acima para correções")
        results["overall_status"] = "partial"
    
    print("\n" + "=" * 60)
    
    # Salvar resultados
    with open('test_results_v1.5.0.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Resultados salvos em: test_results_v1.5.0.json")
    
    return results

if __name__ == "__main__":
    try:
        test_complete_integration()
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO NO TESTE: {e}")
        traceback.print_exc() 