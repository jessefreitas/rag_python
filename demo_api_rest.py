#!/usr/bin/env python3
"""
Demonstração API REST - RAG Python v1.4.0
Testa todas as funcionalidades da API REST
"""

import os
import sys
import requests
import json
import time
import asyncio
from typing import Dict, Any
from datetime import datetime

# Configuração da API
API_BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def print_separator(title: str):
    """Imprime separador visual"""
    print(f"\n{'='*60}")
    print(f"🔥 {title}")
    print(f"{'='*60}")

def print_result(endpoint: str, response: Dict[Any, Any]):
    """Imprime resultado formatado"""
    print(f"\n📍 Endpoint: {endpoint}")
    print(f"✅ Status: {response.get('status_code', 'N/A')}")
    print(f"📊 Resposta: {json.dumps(response.get('json', {}), indent=2, ensure_ascii=False)[:500]}...")

class APIRestDemo:
    """Demonstração completa da API REST"""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.results = []
    
    def test_health_status(self) -> bool:
        """Testa endpoints de saúde e status"""
        print_separator("HEALTH & STATUS ENDPOINTS")
        
        try:
            # Health check
            response = self.session.get(f"{self.base_url}/health")
            health_result = {
                "endpoint": "/health",
                "status_code": response.status_code,
                "json": response.json() if response.status_code == 200 else {"error": response.text}
            }
            print_result("/health", health_result)
            self.results.append(health_result)
            
            # System status
            response = self.session.get(f"{self.base_url}/status")
            status_result = {
                "endpoint": "/status", 
                "status_code": response.status_code,
                "json": response.json() if response.status_code == 200 else {"error": response.text}
            }
            print_result("/status", status_result)
            self.results.append(status_result)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro nos testes de health/status: {e}")
            return False
    
    def test_privacy_endpoints(self) -> bool:
        """Testa endpoints de privacidade"""
        print_separator("PRIVACY ENDPOINTS")
        
        # Texto de teste com dados pessoais brasileiros
        test_content = """
        Cliente: João da Silva Santos
        CPF: 123.456.789-00
        CNPJ: 12.345.678/0001-90
        RG: 12.345.678-9
        Email: joao.santos@empresa.com.br
        Telefone: (11) 98765-4321
        Celular: +55 11 99999-8888
        CEP: 01310-100
        Endereço: Rua Augusta, 123 - São Paulo/SP
        Conta Bancária: 1234-5 / 67890-1
        """
        
        try:
            # Detecção de dados pessoais
            detection_payload = {
                "content": test_content,
                "detailed": True
            }
            
            response = self.session.post(f"{self.base_url}/privacy/detect", json=detection_payload)
            detection_result = {
                "endpoint": "/privacy/detect",
                "status_code": response.status_code,
                "json": response.json() if response.status_code == 200 else {"error": response.text}
            }
            print_result("/privacy/detect", detection_result)
            self.results.append(detection_result)
            
            # Análise de risco
            response = self.session.post(f"{self.base_url}/privacy/analyze-risk", json=detection_payload)
            risk_result = {
                "endpoint": "/privacy/analyze-risk",
                "status_code": response.status_code,
                "json": response.json() if response.status_code == 200 else {"error": response.text}
            }
            print_result("/privacy/analyze-risk", risk_result)
            self.results.append(risk_result)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro nos testes de privacidade: {e}")
            return False
    
    def test_llm_endpoints(self) -> bool:
        """Testa endpoints de LLM"""
        print_separator("LLM ENDPOINTS")
        
        try:
            # Lista provedores
            response = self.session.get(f"{self.base_url}/llm/providers")
            providers_result = {
                "endpoint": "/llm/providers",
                "status_code": response.status_code,
                "json": response.json() if response.status_code == 200 else {"error": response.text}
            }
            print_result("/llm/providers", providers_result)
            self.results.append(providers_result)
            
            # Query LLM
            query_payload = {
                "query": "Explique brevemente o que é LGPD",
                "provider": "openai"
            }
            
            response = self.session.post(f"{self.base_url}/llm/query", json=query_payload)
            query_result = {
                "endpoint": "/llm/query",
                "status_code": response.status_code,
                "json": response.json() if response.status_code == 200 else {"error": response.text}
            }
            print_result("/llm/query", query_result)
            self.results.append(query_result)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro nos testes de LLM: {e}")
            return False
    
    def test_api_documentation(self) -> bool:
        """Testa acesso à documentação da API"""
        print_separator("API DOCUMENTATION")
        
        try:
            # Swagger UI
            response = self.session.get(f"{self.base_url}/docs")
            docs_result = {
                "endpoint": "/docs",
                "status_code": response.status_code,
                "accessible": response.status_code == 200
            }
            print(f"📖 Swagger UI: {'✅ Acessível' if docs_result['accessible'] else '❌ Inacessível'}")
            
            # ReDoc
            response = self.session.get(f"{self.base_url}/redoc")
            redoc_result = {
                "endpoint": "/redoc", 
                "status_code": response.status_code,
                "accessible": response.status_code == 200
            }
            print(f"📖 ReDoc: {'✅ Acessível' if redoc_result['accessible'] else '❌ Inacessível'}")
            
            self.results.extend([docs_result, redoc_result])
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste de documentação: {e}")
            return False
    
    def performance_test(self) -> bool:
        """Teste de performance básico"""
        print_separator("PERFORMANCE TEST")
        
        try:
            # Teste de múltiplas requisições
            test_payload = {
                "content": "Email: teste@email.com, Telefone: (11) 99999-9999",
                "detailed": False
            }
            
            start_time = time.time()
            responses = []
            
            for i in range(5):
                response = self.session.post(f"{self.base_url}/privacy/detect", json=test_payload)
                responses.append(response.status_code)
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / 5
            
            performance_result = {
                "total_requests": 5,
                "total_time": round(total_time, 2),
                "average_time": round(avg_time, 2),
                "successful_requests": sum(1 for r in responses if r == 200),
                "success_rate": (sum(1 for r in responses if r == 200) / 5) * 100
            }
            
            print(f"⚡ Performance:")
            print(f"   Total: {performance_result['total_time']}s")
            print(f"   Média: {performance_result['average_time']}s")
            print(f"   Taxa de sucesso: {performance_result['success_rate']}%")
            
            self.results.append(performance_result)
            return True
            
        except Exception as e:
            print(f"❌ Erro no teste de performance: {e}")
            return False
    
    def generate_report(self):
        """Gera relatório completo dos testes"""
        print_separator("RELATÓRIO FINAL")
        
        # Estatísticas gerais
        total_tests = len([r for r in self.results if 'endpoint' in r])
        successful_tests = len([r for r in self.results if r.get('status_code') == 200])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Estatísticas Gerais:")
        print(f"   Total de testes: {total_tests}")
        print(f"   Testes bem-sucedidos: {successful_tests}")
        print(f"   Taxa de sucesso: {success_rate:.1f}%")
        
        # Endpoints testados
        print(f"\n🔍 Endpoints testados:")
        for result in self.results:
            if 'endpoint' in result:
                status = "✅" if result.get('status_code') == 200 else "❌"
                print(f"   {status} {result['endpoint']} - {result.get('status_code', 'N/A')}")
        
        # Salva relatório
        report_filename = f"api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump({
                "test_summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "success_rate": success_rate,
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: {report_filename}")
    
    def run_full_demo(self):
        """Executa demonstração completa"""
        print("🚀 INICIANDO DEMONSTRAÇÃO API REST v1.4.0")
        print(f"🌐 URL Base: {self.base_url}")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verifica se API está rodando
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                print("❌ API não está respondendo. Certifique-se de que está rodando:")
                print("   python api_server.py")
                return False
        except:
            print("❌ Não foi possível conectar à API. Verifique se está rodando:")
            print("   python api_server.py")
            return False
        
        # Executa testes
        tests = [
            ("Health & Status", self.test_health_status),
            ("Privacy Endpoints", self.test_privacy_endpoints), 
            ("LLM Endpoints", self.test_llm_endpoints),
            ("API Documentation", self.test_api_documentation),
            ("Performance Test", self.performance_test)
        ]
        
        results_summary = []
        for test_name, test_func in tests:
            print(f"\n🧪 Executando: {test_name}")
            try:
                result = test_func()
                results_summary.append((test_name, result))
                print(f"{'✅' if result else '❌'} {test_name}: {'PASSOU' if result else 'FALHOU'}")
            except Exception as e:
                print(f"❌ {test_name}: ERRO - {e}")
                results_summary.append((test_name, False))
        
        # Relatório final
        self.generate_report()
        
        # Resumo
        passed = sum(1 for _, result in results_summary if result)
        total = len(results_summary)
        
        print(f"\n🎯 RESUMO FINAL:")
        print(f"   Testes executados: {total}")
        print(f"   Testes aprovados: {passed}")
        print(f"   Taxa de sucesso: {(passed/total*100):.1f}%")
        
        if passed == total:
            print("\n🎉 TODOS OS TESTES PASSARAM! API REST v1.4.0 FUNCIONANDO PERFEITAMENTE!")
        else:
            print(f"\n⚠️ {total-passed} teste(s) falharam. Verifique os logs acima.")
        
        return passed == total

def main():
    """Função principal"""
    print("🔥 RAG Python v1.4.0 - Demo API REST")
    print("=" * 60)
    
    # Verifica se deve iniciar a API
    if len(sys.argv) > 1 and sys.argv[1] == "--start-api":
        print("🚀 Iniciando API REST...")
        os.system("python api_server.py &")
        time.sleep(5)  # Aguarda API inicializar
    
    # Executa demonstração
    demo = APIRestDemo()
    success = demo.run_full_demo()
    
    if success:
        print("\n🌟 API REST v1.4.0 validada com sucesso!")
        print("📖 Acesse a documentação em: http://localhost:8000/docs")
    else:
        print("\n❌ Alguns testes falharam. Verifique a configuração.")
    
    return success

if __name__ == "__main__":
    main() 