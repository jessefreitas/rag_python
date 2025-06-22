#!/usr/bin/env python3
"""
Microsoft Presidio Integration - RAG Python v1.4.0
Detecção avançada de PII usando Microsoft Presidio
"""

import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import logging

try:
    from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import RecognizerResult, OperatorConfig
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False
    print("⚠️ Microsoft Presidio não instalado. Use: pip install presidio-analyzer presidio-anonymizer")

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PresidioPrivacyManager:
    """
    Gerenciador de privacidade usando Microsoft Presidio
    Detecção avançada de PII com ML e regras customizadas
    """
    
    def __init__(self):
        """Inicializa o Presidio Privacy Manager"""
        if not PRESIDIO_AVAILABLE:
            raise ImportError("Microsoft Presidio não está disponível")
        
        self.setup_presidio()
        self.custom_recognizers = {}
        self.detection_history = []
        
        # Configurações brasileiras específicas
        self.setup_brazilian_patterns()
        
        logger.info("✅ Presidio Privacy Manager inicializado")
    
    def setup_presidio(self):
        """Configura engines do Presidio"""
        try:
            # Configuração do NLP Engine
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "pt", "model_name": "pt_core_news_sm"}]
            }
            
            # Fallback para inglês se português não disponível
            try:
                nlp_provider = NlpEngineProvider(nlp_configuration=configuration)
                nlp_engine = nlp_provider.create_engine()
            except:
                logger.warning("⚠️ Modelo português não encontrado, usando inglês")
                configuration["models"] = [{"lang_code": "en", "model_name": "en_core_web_sm"}]
                nlp_provider = NlpEngineProvider(nlp_configuration=configuration)
                nlp_engine = nlp_provider.create_engine()
            
            # Inicializa engines
            self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
            self.anonymizer = AnonymizerEngine()
            
            logger.info("✅ Presidio engines configurados")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar Presidio: {e}")
            # Fallback para configuração básica
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
    
    def setup_brazilian_patterns(self):
        """Configura padrões brasileiros específicos"""
        
        # Padrão CPF melhorado
        cpf_pattern = Pattern(
            name="cpf_pattern",
            regex=r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
            score=0.9
        )
        
        cpf_recognizer = PatternRecognizer(
            supported_entity="BR_CPF",
            patterns=[cpf_pattern],
            name="CPF_Recognizer"
        )
        
        # Padrão CNPJ melhorado
        cnpj_pattern = Pattern(
            name="cnpj_pattern",
            regex=r"\b\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}\b",
            score=0.9
        )
        
        cnpj_recognizer = PatternRecognizer(
            supported_entity="BR_CNPJ",
            patterns=[cnpj_pattern],
            name="CNPJ_Recognizer"
        )
        
        # Padrão RG brasileiro
        rg_pattern = Pattern(
            name="rg_pattern",
            regex=r"\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9xX]\b",
            score=0.8
        )
        
        rg_recognizer = PatternRecognizer(
            supported_entity="BR_RG",
            patterns=[rg_pattern],
            name="RG_Recognizer"
        )
        
        # Padrão CEP brasileiro
        cep_pattern = Pattern(
            name="cep_pattern",
            regex=r"\b\d{5}-?\d{3}\b",
            score=0.8
        )
        
        cep_recognizer = PatternRecognizer(
            supported_entity="BR_CEP",
            patterns=[cep_pattern],
            name="CEP_Recognizer"
        )
        
        # Padrão telefone brasileiro
        phone_pattern = Pattern(
            name="br_phone_pattern",
            regex=r"\b(?:\+55\s?)?(?:\(?[1-9]{2}\)?\s?)?(?:9\s?)?[0-9]{4}-?[0-9]{4}\b",
            score=0.7
        )
        
        phone_recognizer = PatternRecognizer(
            supported_entity="BR_PHONE",
            patterns=[phone_pattern],
            name="BR_Phone_Recognizer"
        )
        
        # Adiciona recognizers customizados
        self.analyzer.registry.add_recognizer(cpf_recognizer)
        self.analyzer.registry.add_recognizer(cnpj_recognizer)
        self.analyzer.registry.add_recognizer(rg_recognizer)
        self.analyzer.registry.add_recognizer(cep_recognizer)
        self.analyzer.registry.add_recognizer(phone_recognizer)
        
        # Armazena para referência
        self.custom_recognizers = {
            "BR_CPF": cpf_recognizer,
            "BR_CNPJ": cnpj_recognizer,
            "BR_RG": rg_recognizer,
            "BR_CEP": cep_recognizer,
            "BR_PHONE": phone_recognizer
        }
        
        logger.info("✅ Padrões brasileiros configurados")
    
    def analyze_text_advanced(self, text: str, language: str = "pt") -> Dict[str, Any]:
        """
        Análise avançada de texto usando Presidio
        
        Args:
            text: Texto para analisar
            language: Idioma do texto (pt/en)
            
        Returns:
            Dict com resultados da análise
        """
        try:
            # Análise com Presidio
            results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=None,  # Analisa todas as entidades
                return_decision_process=True
            )
            
            # Processa resultados
            detected_entities = {}
            total_score = 0
            
            for result in results:
                entity_type = result.entity_type
                
                if entity_type not in detected_entities:
                    detected_entities[entity_type] = {
                        "count": 0,
                        "confidence_scores": [],
                        "locations": [],
                        "samples": []
                    }
                
                detected_entities[entity_type]["count"] += 1
                detected_entities[entity_type]["confidence_scores"].append(result.score)
                detected_entities[entity_type]["locations"].append({
                    "start": result.start,
                    "end": result.end
                })
                
                # Extrai amostra do texto
                sample = text[result.start:result.end]
                if sample not in detected_entities[entity_type]["samples"]:
                    detected_entities[entity_type]["samples"].append(sample)
                
                total_score += result.score
            
            # Calcula score médio
            avg_score = total_score / len(results) if results else 0
            
            # Classifica risco
            risk_level = self._calculate_risk_level_presidio(detected_entities, avg_score)
            
            analysis_result = {
                "has_pii": len(results) > 0,
                "total_entities": len(results),
                "unique_entity_types": len(detected_entities),
                "detected_entities": detected_entities,
                "average_confidence": avg_score,
                "risk_level": risk_level,
                "analysis_timestamp": datetime.now().isoformat(),
                "language": language,
                "text_length": len(text)
            }
            
            # Salva no histórico
            self.detection_history.append(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise avançada: {e}")
            return {
                "error": str(e),
                "has_pii": False,
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def anonymize_text_advanced(self, text: str, language: str = "pt") -> Dict[str, Any]:
        """
        Anonimização avançada usando Presidio
        
        Args:
            text: Texto para anonimizar
            language: Idioma do texto
            
        Returns:
            Dict com texto anonimizado e metadados
        """
        try:
            # Primeiro analisa
            results = self.analyzer.analyze(text=text, language=language)
            
            if not results:
                return {
                    "original_text": text,
                    "anonymized_text": text,
                    "changes_made": False,
                    "entities_found": 0
                }
            
            # Configurações de anonimização personalizadas
            operators = {
                "PERSON": OperatorConfig("replace", {"new_value": "[PESSOA]"}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
                "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[TELEFONE]"}),
                "BR_CPF": OperatorConfig("replace", {"new_value": "[CPF]"}),
                "BR_CNPJ": OperatorConfig("replace", {"new_value": "[CNPJ]"}),
                "BR_RG": OperatorConfig("replace", {"new_value": "[RG]"}),
                "BR_CEP": OperatorConfig("replace", {"new_value": "[CEP]"}),
                "BR_PHONE": OperatorConfig("replace", {"new_value": "[TELEFONE_BR]"}),
                "CREDIT_CARD": OperatorConfig("replace", {"new_value": "[CARTÃO]"}),
                "IBAN_CODE": OperatorConfig("replace", {"new_value": "[CONTA_BANCÁRIA]"}),
                "IP_ADDRESS": OperatorConfig("replace", {"new_value": "[IP]"}),
                "DATE_TIME": OperatorConfig("replace", {"new_value": "[DATA]"}),
                "LOCATION": OperatorConfig("replace", {"new_value": "[LOCAL]"}),
                "URL": OperatorConfig("replace", {"new_value": "[URL]"})
            }
            
            # Anonimiza
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators=operators
            )
            
            # Prepara resultado
            entities_summary = {}
            for result in results:
                entity_type = result.entity_type
                entities_summary[entity_type] = entities_summary.get(entity_type, 0) + 1
            
            return {
                "original_text": text,
                "anonymized_text": anonymized_result.text,
                "changes_made": True,
                "entities_found": len(results),
                "entities_summary": entities_summary,
                "anonymization_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na anonimização avançada: {e}")
            return {
                "error": str(e),
                "original_text": text,
                "anonymized_text": text,
                "changes_made": False
            }
    
    def _calculate_risk_level_presidio(self, entities: Dict, avg_score: float) -> str:
        """Calcula nível de risco baseado em entidades detectadas"""
        
        high_risk_entities = ["BR_CPF", "BR_CNPJ", "CREDIT_CARD", "IBAN_CODE"]
        medium_risk_entities = ["EMAIL_ADDRESS", "PHONE_NUMBER", "BR_PHONE", "BR_RG"]
        
        high_risk_count = sum(1 for entity in entities.keys() if entity in high_risk_entities)
        medium_risk_count = sum(1 for entity in entities.keys() if entity in medium_risk_entities)
        
        total_entities = len(entities)
        
        if high_risk_count >= 2 or avg_score > 0.8:
            return "CRÍTICO"
        elif high_risk_count >= 1 or medium_risk_count >= 3 or avg_score > 0.6:
            return "ALTO"
        elif medium_risk_count >= 1 or total_entities >= 3 or avg_score > 0.4:
            return "MÉDIO"
        else:
            return "BAIXO"
    
    def get_supported_entities(self) -> List[str]:
        """Retorna lista de entidades suportadas"""
        try:
            # Entidades padrão do Presidio
            standard_entities = [
                "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
                "IBAN_CODE", "IP_ADDRESS", "DATE_TIME", "LOCATION", "URL"
            ]
            
            # Entidades customizadas brasileiras
            brazilian_entities = list(self.custom_recognizers.keys())
            
            return standard_entities + brazilian_entities
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter entidades suportadas: {e}")
            return []
    
    def validate_presidio_installation(self) -> Dict[str, Any]:
        """Valida instalação e configuração do Presidio"""
        try:
            test_text = "João Silva, CPF 123.456.789-00, email joao@email.com, telefone (11) 99999-9999"
            
            # Testa análise
            results = self.analyzer.analyze(text=test_text, language="pt")
            
            # Testa anonimização
            if results:
                anonymized = self.anonymizer.anonymize(text=test_text, analyzer_results=results)
                anonymization_working = True
            else:
                anonymization_working = False
            
            return {
                "presidio_available": True,
                "analyzer_working": True,
                "anonymizer_working": anonymization_working,
                "entities_detected": len(results),
                "custom_recognizers_loaded": len(self.custom_recognizers),
                "supported_entities": len(self.get_supported_entities()),
                "test_successful": True
            }
            
        except Exception as e:
            return {
                "presidio_available": PRESIDIO_AVAILABLE,
                "analyzer_working": False,
                "anonymizer_working": False,
                "error": str(e),
                "test_successful": False
            }
    
    def export_detection_history(self, filename: Optional[str] = None) -> str:
        """Exporta histórico de detecções"""
        if not filename:
            filename = f"presidio_detection_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.detection_history, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Histórico exportado para {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar histórico: {e}")
            return ""

# Instância global
presidio_manager = None

def get_presidio_manager() -> Optional[PresidioPrivacyManager]:
    """Retorna instância do Presidio Manager"""
    global presidio_manager
    
    if not PRESIDIO_AVAILABLE:
        return None
    
    if presidio_manager is None:
        try:
            presidio_manager = PresidioPrivacyManager()
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Presidio Manager: {e}")
            return None
    
    return presidio_manager

def test_presidio_integration():
    """Teste da integração com Presidio"""
    print("🧪 Testando integração Microsoft Presidio...")
    
    if not PRESIDIO_AVAILABLE:
        print("❌ Microsoft Presidio não está disponível")
        return False
    
    try:
        manager = get_presidio_manager()
        if not manager:
            print("❌ Falha ao inicializar Presidio Manager")
            return False
        
        # Validação
        validation = manager.validate_presidio_installation()
        print(f"✅ Validação: {validation}")
        
        # Teste com texto brasileiro
        test_text = """
        Cliente: Maria da Silva Santos
        CPF: 123.456.789-00
        CNPJ: 12.345.678/0001-90
        RG: 12.345.678-9
        Email: maria.santos@empresa.com.br
        Telefone: (11) 98765-4321
        CEP: 01310-100
        Endereço: Rua Augusta, 123 - São Paulo/SP
        """
        
        print("\n🔍 Análise avançada:")
        analysis = manager.analyze_text_advanced(test_text)
        print(f"Entidades detectadas: {analysis.get('unique_entity_types', 0)}")
        print(f"Nível de risco: {analysis.get('risk_level', 'N/A')}")
        print(f"Confiança média: {analysis.get('average_confidence', 0):.2f}")
        
        print("\n🔒 Anonimização:")
        anonymized = manager.anonymize_text_advanced(test_text)
        print(f"Texto anonimizado: {anonymized['anonymized_text'][:100]}...")
        
        print("\n✅ Teste do Presidio concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    test_presidio_integration() 