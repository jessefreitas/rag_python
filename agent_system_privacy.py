#!/usr/bin/env python3
"""
Sistema de Agentes com Privacidade Integrada - RAG Python
Integração do privacy_system.py com agent_system.py para compliance LGPD
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

# Importações do sistema existente
from agent_system import AgentSystem, Agent
from privacy_system import privacy_manager, DataCategory, RetentionPolicy, DataRecord
from llm_providers import llm_manager

logger = logging.getLogger(__name__)

class PrivacyAwareAgent(Agent):
    """Agente com consciência de privacidade e compliance LGPD"""
    
    def __init__(self, agent_id: str, name: str, description: str, 
                 system_prompt: str, model_name: str = "gpt-3.5-turbo",
                 privacy_level: str = "standard"):
        super().__init__(agent_id, name, description, system_prompt, model_name)
        
        # Configurações de privacidade
        self.privacy_level = privacy_level  # standard, high, maximum
        self.data_retention_policy = self._get_retention_policy(privacy_level)
        self.auto_anonymize = privacy_level in ["high", "maximum"]
        self.require_consent = privacy_level == "maximum"
        
        # Estatísticas de privacidade
        self.privacy_stats = {
            'documents_processed': 0,
            'data_anonymized': 0,
            'consent_requests': 0,
            'compliance_violations': 0
        }
    
    def _get_retention_policy(self, privacy_level: str) -> RetentionPolicy:
        """Define política de retenção baseada no nível de privacidade"""
        policies = {
            "standard": RetentionPolicy.MEDIUM_TERM,  # 6 meses
            "high": RetentionPolicy.SHORT_TERM,       # 30 dias
            "maximum": RetentionPolicy.SHORT_TERM     # 30 dias + auto-delete
        }
        return policies.get(privacy_level, RetentionPolicy.MEDIUM_TERM)
    
    def process_document_with_privacy(self, content: str, filename: str,
                                    user_consent: bool = False,
                                    processing_purpose: str = "Document analysis") -> Dict[str, Any]:
        """Processa documento com verificações de privacidade"""
        
        # 1. Verifica se precisa de consentimento
        if self.require_consent and not user_consent:
            logger.warning(f"Agente {self.agent_id}: Consentimento necessário mas não fornecido")
            self.privacy_stats['consent_requests'] += 1
            return {
                'success': False,
                'error': 'User consent required for maximum privacy level',
                'consent_required': True
            }
        
        # 2. Detecta dados pessoais
        detected_data = privacy_manager.privacy_compliance.detect_personal_data(content)
        data_category = privacy_manager.privacy_compliance.classify_data_sensitivity(content)
        
        # 3. Cria registro de dados
        data_record = privacy_manager.create_data_record(
            content=content,
            agent_id=self.agent_id,
            purpose=processing_purpose,
            user_consent=user_consent,
            retention_policy=self.data_retention_policy
        )
        
        # 4. Processa baseado no nível de privacidade
        processed_content = content
        anonymization_applied = False
        
        if detected_data and self.auto_anonymize:
            # Anonimiza automaticamente se configurado
            anonymized_content, mapping = privacy_manager.privacy_compliance.anonymize_text(
                content, method="masking"
            )
            processed_content = anonymized_content
            anonymization_applied = True
            
            # Atualiza registro
            privacy_manager.anonymize_record(data_record.id, method="masking")
            self.privacy_stats['data_anonymized'] += 1
        
        # 5. Processa documento normalmente
        try:
            result = self.process_document(processed_content, filename)
            self.privacy_stats['documents_processed'] += 1
            
            # 6. Log de compliance
            privacy_manager.privacy_compliance.log_processing_activity(
                operation="DOCUMENT_PROCESS",
                data_id=data_record.id,
                purpose=processing_purpose,
                user_consent=user_consent,
                details={
                    'filename': filename,
                    'data_category': data_category.value,
                    'detected_data_types': list(detected_data.keys()),
                    'anonymization_applied': anonymization_applied,
                    'privacy_level': self.privacy_level
                }
            )
            
            return {
                'success': True,
                'result': result,
                'data_record_id': data_record.id,
                'privacy_info': {
                    'data_category': data_category.value,
                    'detected_data': detected_data,
                    'anonymization_applied': anonymization_applied,
                    'retention_expires': data_record.expires_at.isoformat() if data_record.expires_at else None
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar documento com privacidade: {e}")
            self.privacy_stats['compliance_violations'] += 1
            
            # Soft delete em caso de erro para segurança
            privacy_manager.soft_delete_record(data_record.id, "Processing error - safety measure")
            
            return {
                'success': False,
                'error': str(e),
                'data_record_id': data_record.id
            }
    
    def query_with_privacy(self, query: str, user_consent: bool = False) -> Dict[str, Any]:
        """Executa query com verificações de privacidade"""
        
        # 1. Verifica dados pessoais na query
        detected_data = privacy_manager.privacy_compliance.detect_personal_data(query)
        
        if detected_data and self.require_consent and not user_consent:
            return {
                'success': False,
                'error': 'Query contains personal data but no consent provided',
                'detected_data': detected_data,
                'consent_required': True
            }
        
        # 2. Anonimiza query se necessário
        processed_query = query
        if detected_data and self.auto_anonymize:
            processed_query, _ = privacy_manager.privacy_compliance.anonymize_text(
                query, method="pseudonymization"
            )
        
        # 3. Cria registro da query
        data_record = privacy_manager.create_data_record(
            content=query,
            agent_id=self.agent_id,
            purpose="User query processing",
            user_consent=user_consent,
            retention_policy=RetentionPolicy.SHORT_TERM  # Queries têm retenção curta
        )
        
        # 4. Executa query
        try:
            response = self.query(processed_query)
            
            # 5. Log de compliance
            privacy_manager.privacy_compliance.log_processing_activity(
                operation="QUERY_PROCESS",
                data_id=data_record.id,
                purpose="User query processing",
                user_consent=user_consent,
                details={
                    'detected_data_types': list(detected_data.keys()),
                    'anonymization_applied': bool(detected_data and self.auto_anonymize)
                }
            )
            
            return {
                'success': True,
                'response': response,
                'data_record_id': data_record.id,
                'privacy_info': {
                    'detected_data': detected_data,
                    'anonymization_applied': bool(detected_data and self.auto_anonymize)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao executar query com privacidade: {e}")
            privacy_manager.soft_delete_record(data_record.id, "Query processing error")
            
            return {
                'success': False,
                'error': str(e),
                'data_record_id': data_record.id
            }
    
    def get_privacy_report(self) -> Dict[str, Any]:
        """Gera relatório de privacidade do agente"""
        
        # Dados do privacy_manager para este agente
        agent_records = [
            record for record in privacy_manager.data_records.values()
            if record.agent_id == self.agent_id
        ]
        
        # Estatísticas detalhadas
        by_category = {}
        for category in DataCategory:
            by_category[category.value] = len([
                r for r in agent_records if r.category == category
            ])
        
        expired_count = len([r for r in agent_records if r.is_expired])
        deleted_count = len([r for r in agent_records if r.is_deleted])
        
        return {
            'agent_id': self.agent_id,
            'agent_name': self.name,
            'privacy_level': self.privacy_level,
            'retention_policy': self.data_retention_policy.name,
            'stats': self.privacy_stats,
            'data_records': {
                'total': len(agent_records),
                'active': len([r for r in agent_records if not r.is_deleted]),
                'deleted': deleted_count,
                'expired': expired_count,
                'by_category': by_category
            },
            'compliance_status': {
                'violations': self.privacy_stats['compliance_violations'],
                'consent_compliance': self.privacy_stats['consent_requests'] == 0 or not self.require_consent,
                'retention_compliance': expired_count == 0  # Todos expirados foram tratados
            }
        }

class PrivacyAwareAgentSystem(AgentSystem):
    """Sistema de agentes com privacidade integrada"""
    
    def __init__(self):
        super().__init__()
        self.privacy_enabled = True
        self.global_privacy_level = "standard"
        
        # Configurações globais de privacidade
        self.privacy_config = {
            'auto_cleanup_interval_hours': 24,
            'require_consent_for_sensitive': True,
            'log_all_operations': True,
            'anonymize_exports': True
        }
        
        # Última limpeza automática
        self.last_cleanup = datetime.now()
    
    def create_privacy_agent(self, name: str, description: str, system_prompt: str,
                           model_name: str = "gpt-3.5-turbo",
                           privacy_level: str = "standard") -> PrivacyAwareAgent:
        """Cria agente com privacidade"""
        
        agent_id = str(uuid.uuid4())
        
        agent = PrivacyAwareAgent(
            agent_id=agent_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            model_name=model_name,
            privacy_level=privacy_level
        )
        
        self.agents[agent_id] = agent
        
        # Log da criação
        privacy_manager.privacy_compliance.log_processing_activity(
            operation="AGENT_CREATE",
            data_id=agent_id,
            purpose="Agent creation",
            details={
                'agent_name': name,
                'privacy_level': privacy_level,
                'model_name': model_name
            }
        )
        
        return agent
    
    def run_privacy_cleanup(self) -> Dict[str, Any]:
        """Executa limpeza automática baseada em políticas de retenção"""
        
        logger.info("Iniciando limpeza automática de dados...")
        
        # 1. Cleanup geral do privacy_manager
        cleanup_stats = privacy_manager.cleanup_expired_data()
        
        # 2. Atualiza estatísticas dos agentes
        for agent in self.agents.values():
            if isinstance(agent, PrivacyAwareAgent):
                # Verifica se há dados expirados para este agente
                agent_records = [
                    record for record in privacy_manager.data_records.values()
                    if record.agent_id == agent.agent_id and record.is_expired
                ]
                
                if agent_records:
                    logger.info(f"Agente {agent.name}: {len(agent_records)} registros expirados")
        
        # 3. Atualiza timestamp
        self.last_cleanup = datetime.now()
        
        # 4. Log da operação
        privacy_manager.privacy_compliance.log_processing_activity(
            operation="SYSTEM_CLEANUP",
            data_id="system",
            purpose="Automated data retention compliance",
            details=cleanup_stats
        )
        
        return {
            'cleanup_timestamp': self.last_cleanup.isoformat(),
            'stats': cleanup_stats,
            'next_cleanup': (self.last_cleanup + timedelta(
                hours=self.privacy_config['auto_cleanup_interval_hours']
            )).isoformat()
        }
    
    def get_system_privacy_report(self) -> Dict[str, Any]:
        """Gera relatório completo de privacidade do sistema"""
        
        # Relatórios individuais dos agentes
        agent_reports = {}
        for agent_id, agent in self.agents.items():
            if isinstance(agent, PrivacyAwareAgent):
                agent_reports[agent_id] = agent.get_privacy_report()
        
        # Estatísticas globais
        global_stats = privacy_manager.get_data_summary()
        
        # Auditoria recente
        recent_audit = privacy_manager.privacy_compliance.get_audit_trail(
            start_date=datetime.now() - timedelta(days=7)
        )
        
        return {
            'system_info': {
                'privacy_enabled': self.privacy_enabled,
                'global_privacy_level': self.global_privacy_level,
                'config': self.privacy_config,
                'last_cleanup': self.last_cleanup.isoformat()
            },
            'global_stats': global_stats,
            'agents': agent_reports,
            'recent_audit_entries': len(recent_audit),
            'compliance_summary': {
                'total_agents': len([a for a in self.agents.values() if isinstance(a, PrivacyAwareAgent)]),
                'total_data_records': global_stats['total_records'],
                'active_records': global_stats['active_records'],
                'compliance_violations': sum([
                    agent.privacy_stats['compliance_violations'] 
                    for agent in self.agents.values() 
                    if isinstance(agent, PrivacyAwareAgent)
                ])
            }
        }
    
    def export_compliance_report(self, format: str = "json") -> str:
        """Exporta relatório de compliance para auditoria"""
        
        report = self.get_system_privacy_report()
        
        if self.privacy_config['anonymize_exports']:
            # Remove dados sensíveis do export
            for agent_id in report['agents']:
                if 'data_records' in report['agents'][agent_id]:
                    # Remove detalhes específicos, mantém apenas estatísticas
                    report['agents'][agent_id]['data_records'] = {
                        'total': report['agents'][agent_id]['data_records']['total'],
                        'by_category': report['agents'][agent_id]['data_records']['by_category']
                    }
        
        if format == "json":
            return json.dumps(report, indent=2, ensure_ascii=False, default=str)
        else:
            # Implementar outros formatos se necessário
            return json.dumps(report, indent=2, ensure_ascii=False, default=str)

# Instância global com privacidade
privacy_agent_system = PrivacyAwareAgentSystem() 