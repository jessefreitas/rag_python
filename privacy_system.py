#!/usr/bin/env python3
"""
Sistema de Privacidade e Anonimização - RAG Python
Compliance LGPD e proteção de dados pessoais
"""

import hashlib
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Importações para anonimização
try:
    from faker import Faker
except ImportError:
    Faker = None

try:
    import scrubadub
except ImportError:
    scrubadub = None

# Configuração de logging
logger = logging.getLogger(__name__)

class DataCategory(Enum):
    """Categorias de dados para classificação LGPD"""
    PERSONAL = "personal"           # Dados pessoais
    SENSITIVE = "sensitive"         # Dados pessoais sensíveis
    ANONYMOUS = "anonymous"         # Dados anônimos
    PSEUDONYMOUS = "pseudonymous"   # Dados pseudonimizados
    PUBLIC = "public"              # Dados públicos

class RetentionPolicy(Enum):
    """Políticas de retenção de dados"""
    SHORT_TERM = 30      # 30 dias
    MEDIUM_TERM = 180    # 6 meses
    LONG_TERM = 365      # 1 ano
    LEGAL_MINIMUM = 1825 # 5 anos (mínimo legal)
    PERMANENT = -1       # Permanente (apenas para dados anônimos)

@dataclass
class DataRecord:
    """Registro de dados com metadados de privacidade"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    category: DataCategory = DataCategory.PERSONAL
    retention_policy: RetentionPolicy = RetentionPolicy.MEDIUM_TERM
    created_at: datetime = field(default_factory=datetime.now)
    anonymized_at: Optional[datetime] = None
    agent_id: Optional[str] = None
    user_consent: bool = False
    processing_purpose: str = ""
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    
    @property
    def expires_at(self) -> Optional[datetime]:
        """Calcula quando o dado expira baseado na política de retenção"""
        if self.retention_policy == RetentionPolicy.PERMANENT:
            return None
        return self.created_at + timedelta(days=self.retention_policy.value)
    
    @property
    def is_expired(self) -> bool:
        """Verifica se o dado expirou"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

class PrivacyCompliance:
    """Sistema de compliance com LGPD"""
    
    def __init__(self):
        self.faker = Faker('pt_BR') if Faker else None
        self.audit_log: List[Dict[str, Any]] = []
    
    def detect_personal_data(self, text: str) -> Dict[str, List[str]]:
        """Detecta dados pessoais no texto"""
        patterns = {
            'cpf': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
            'cnpj': r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\(\d{2}\)\s?)?\d{4,5}-?\d{4}\b',
            'rg': r'\b\d{1,2}\.?\d{3}\.?\d{3}-?\d{1}\b',
            'cep': r'\b\d{5}-?\d{3}\b',
            'nome_proprio': r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b'
        }
        
        detected = {}
        for data_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected[data_type] = matches
        
        # Usar scrubadub se disponível
        if scrubadub:
            scrubber = scrubadub.Scrubber()
            scrubber.add_detector(scrubadub.detectors.EmailDetector)
            scrubber.add_detector(scrubadub.detectors.PhoneDetector)
            
            filth = scrubber.filth.find_filth(text)
            for item in filth:
                data_type = item.type.lower()
                if data_type not in detected:
                    detected[data_type] = []
                detected[data_type].append(item.text)
        
        return detected
    
    def anonymize_text(self, text: str, method: str = "pseudonymization") -> Tuple[str, Dict[str, str]]:
        """Anonimiza texto substituindo dados pessoais"""
        if not self.faker and method == "fake_data":
            method = "pseudonymization"
        
        mapping = {}
        anonymized_text = text
        detected_data = self.detect_personal_data(text)
        
        for data_type, values in detected_data.items():
            for value in values:
                if value not in mapping:
                    if method == "pseudonymization":
                        # Pseudonimização com hash
                        hash_object = hashlib.sha256(value.encode())
                        mapping[value] = f"<{data_type.upper()}_{hash_object.hexdigest()[:8]}>"
                    elif method == "fake_data" and self.faker:
                        # Substituição por dados falsos
                        mapping[value] = self._generate_fake_data(data_type)
                    elif method == "masking":
                        # Mascaramento parcial
                        mapping[value] = self._mask_data(value, data_type)
                    else:
                        # Remoção completa
                        mapping[value] = f"<{data_type.upper()}_REMOVIDO>"
                
                anonymized_text = anonymized_text.replace(value, mapping[value])
        
        return anonymized_text, mapping
    
    def _generate_fake_data(self, data_type: str) -> str:
        """Gera dados falsos baseado no tipo"""
        if not self.faker:
            return f"<{data_type.upper()}_FAKE>"
        
        fake_generators = {
            'cpf': lambda: self.faker.cpf(),
            'cnpj': lambda: self.faker.cnpj(),
            'email': lambda: self.faker.email(),
            'phone': lambda: self.faker.phone_number(),
            'nome_proprio': lambda: self.faker.name(),
            'cep': lambda: self.faker.postcode()
        }
        
        generator = fake_generators.get(data_type)
        return generator() if generator else f"<{data_type.upper()}_FAKE>"
    
    def _mask_data(self, value: str, data_type: str) -> str:
        """Mascara dados mantendo formato mas ocultando informações"""
        if data_type == 'cpf':
            return f"***.***.{value[-6:]}" if len(value) >= 6 else "***.***.***-**"
        elif data_type == 'email':
            parts = value.split('@')
            if len(parts) == 2:
                name = parts[0]
                domain = parts[1]
                masked_name = name[0] + '*' * (len(name) - 2) + name[-1] if len(name) > 2 else '***'
                return f"{masked_name}@{domain}"
        elif data_type == 'phone':
            return f"({value[:2]}) ****-{value[-4:]}" if len(value) >= 6 else "(**) ****-****"
        
        # Mascaramento genérico
        if len(value) > 4:
            return value[:2] + '*' * (len(value) - 4) + value[-2:]
        else:
            return '*' * len(value)
    
    def classify_data_sensitivity(self, text: str) -> DataCategory:
        """Classifica sensibilidade dos dados"""
        detected = self.detect_personal_data(text)
        
        # Dados sensíveis conforme LGPD
        sensitive_patterns = [
            r'\b(?:saúde|doença|tratamento|medicamento|hospital)\b',
            r'\b(?:religião|religioso|igreja|templo)\b',
            r'\b(?:político|partido|eleição|voto)\b',
            r'\b(?:sexual|orientação|identidade|gênero)\b',
            r'\b(?:étnico|racial|cor|raça)\b'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, text.lower()):
                return DataCategory.SENSITIVE
        
        # Tem dados pessoais mas não sensíveis
        if detected:
            return DataCategory.PERSONAL
        
        return DataCategory.ANONYMOUS
    
    def log_processing_activity(self, operation: str, data_id: str, purpose: str, 
                               user_consent: bool = False, details: Optional[Dict] = None):
        """Registra atividade de processamento para auditoria"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'data_id': data_id,
            'purpose': purpose,
            'user_consent': user_consent,
            'details': details or {}
        }
        
        self.audit_log.append(log_entry)
        logger.info(f"Processamento registrado: {operation} para {data_id}")
    
    def get_audit_trail(self, data_id: Optional[str] = None, 
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retorna trilha de auditoria filtrada"""
        filtered_logs = self.audit_log
        
        if data_id:
            filtered_logs = [log for log in filtered_logs if log['data_id'] == data_id]
        
        if start_date:
            filtered_logs = [log for log in filtered_logs 
                           if datetime.fromisoformat(log['timestamp']) >= start_date]
        
        if end_date:
            filtered_logs = [log for log in filtered_logs 
                           if datetime.fromisoformat(log['timestamp']) <= end_date]
        
        return filtered_logs

class DataLifecycleManager:
    """Gerenciador do ciclo de vida dos dados"""
    
    def __init__(self):
        self.privacy_compliance = PrivacyCompliance()
        self.data_records: Dict[str, DataRecord] = {}
        self.detection_only_mode = False  # Novo modo apenas detecção
    
    def create_data_record(self, content: str, agent_id: str, 
                          purpose: str, user_consent: bool = False,
                          retention_policy: RetentionPolicy = RetentionPolicy.MEDIUM_TERM) -> DataRecord:
        """Cria um novo registro de dados"""
        
        # Classifica sensibilidade
        category = self.privacy_compliance.classify_data_sensitivity(content)
        
        # Cria registro
        record = DataRecord(
            content=content,
            category=category,
            retention_policy=retention_policy,
            agent_id=agent_id,
            user_consent=user_consent,
            processing_purpose=purpose
        )
        
        self.data_records[record.id] = record
        
        # Log da atividade
        self.privacy_compliance.log_processing_activity(
            operation="CREATE",
            data_id=record.id,
            purpose=purpose,
            user_consent=user_consent,
            details={
                'category': category.value,
                'retention_days': retention_policy.value,
                'agent_id': agent_id
            }
        )
        
        return record
    
    def anonymize_record(self, record_id: str, method: str = "pseudonymization") -> bool:
        """Anonimiza um registro específico"""
        if record_id not in self.data_records:
            return False
        
        record = self.data_records[record_id]
        
        # Anonimiza conteúdo
        anonymized_content, mapping = self.privacy_compliance.anonymize_text(
            record.content, method
        )
        
        # Atualiza registro
        record.content = anonymized_content
        record.category = DataCategory.ANONYMOUS
        record.anonymized_at = datetime.now()
        
        # Log da atividade
        self.privacy_compliance.log_processing_activity(
            operation="ANONYMIZE",
            data_id=record_id,
            purpose="Data protection compliance",
            details={
                'method': method,
                'mapping_count': len(mapping)
            }
        )
        
        return True
    
    def soft_delete_record(self, record_id: str, reason: str = "User request") -> bool:
        """Soft delete - marca como deletado mas mantém dados"""
        if record_id not in self.data_records:
            return False
        
        record = self.data_records[record_id]
        record.is_deleted = True
        record.deleted_at = datetime.now()
        
        self.privacy_compliance.log_processing_activity(
            operation="SOFT_DELETE",
            data_id=record_id,
            purpose=reason
        )
        
        return True
    
    def hard_delete_record(self, record_id: str, reason: str = "Retention policy") -> bool:
        """Hard delete - remove permanentemente"""
        if record_id not in self.data_records:
            return False
        
        # Log antes de deletar
        self.privacy_compliance.log_processing_activity(
            operation="HARD_DELETE",
            data_id=record_id,
            purpose=reason
        )
        
        # Remove registro
        del self.data_records[record_id]
        
        return True
    
    def cleanup_expired_data(self) -> Dict[str, int]:
        """Remove dados expirados baseado nas políticas de retenção"""
        stats = {
            'anonymized': 0,
            'hard_deleted': 0,
            'skipped': 0
        }
        
        expired_records = [
            record for record in self.data_records.values()
            if record.is_expired and not record.is_deleted
        ]
        
        for record in expired_records:
            if record.category in [DataCategory.PERSONAL, DataCategory.SENSITIVE]:
                # Anonimiza dados pessoais/sensíveis
                if self.anonymize_record(record.id, method="masking"):
                    stats['anonymized'] += 1
                else:
                    stats['skipped'] += 1
            elif record.category == DataCategory.ANONYMOUS:
                # Pode manter dados anônimos
                stats['skipped'] += 1
            else:
                # Hard delete para outros casos
                if self.hard_delete_record(record.id, "Retention policy expired"):
                    stats['hard_deleted'] += 1
                else:
                    stats['skipped'] += 1
        
        logger.info(f"Limpeza concluída: {stats}")
        return stats
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos dados gerenciados"""
        records = list(self.data_records.values())
        
        return {
            'total_records': len(records),
            'active_records': len([r for r in records if not r.is_deleted]),
            'deleted_records': len([r for r in records if r.is_deleted]),
            'by_category': {
                category.value: len([r for r in records if r.category == category])
                for category in DataCategory
            },
            'expired_records': len([r for r in records if r.is_expired]),
            'anonymized_records': len([r for r in records if r.anonymized_at is not None])
        }
    
    def detect_personal_data_only(self, content: str, detailed: bool = True) -> Dict[str, Any]:
        """Detecta dados pessoais SEM anonimizar - apenas identificação"""
        
        detected_data = self.privacy_compliance.detect_personal_data(content)
        data_category = self.privacy_compliance.classify_data_sensitivity(content)
        
        result = {
            'has_personal_data': bool(detected_data),
            'data_category': data_category.value,
            'detected_types': list(detected_data.keys()),
            'total_occurrences': sum(len(values) for values in detected_data.values())
        }
        
        if detailed:
            # Adiciona detalhes específicos por tipo
            result['details'] = {}
            for data_type, values in detected_data.items():
                result['details'][data_type] = {
                    'count': len(values),
                    'examples': values[:3] if len(values) > 3 else values,  # Máximo 3 exemplos
                    'positions': []
                }
                
                # Encontra posições no texto (opcional)
                for value in values:
                    positions = []
                    start = 0
                    while True:
                        pos = content.find(value, start)
                        if pos == -1:
                            break
                        positions.append({'start': pos, 'end': pos + len(value)})
                        start = pos + 1
                    result['details'][data_type]['positions'].extend(positions)
        
        return result
    
    def create_detection_only_record(self, content: str, agent_id: str, 
                                   purpose: str = "Data detection analysis") -> Dict[str, Any]:
        """Cria registro apenas para detecção, sem anonimização"""
        
        # Detecta dados
        detection_result = self.detect_personal_data_only(content, detailed=True)
        
        # Cria registro marcado como detection-only
        record = DataRecord(
            content=content,  # Mantém conteúdo original
            category=DataCategory[detection_result['data_category'].upper()],
            retention_policy=RetentionPolicy.SHORT_TERM,  # Retenção curta para análises
            agent_id=agent_id,
            user_consent=True,  # Implícito para detecção apenas
            processing_purpose=f"{purpose} (detection only)"
        )
        
        self.data_records[record.id] = record
        
        # Log da atividade
        self.privacy_compliance.log_processing_activity(
            operation="DETECT_ONLY",
            data_id=record.id,
            purpose=purpose,
            user_consent=True,
            details={
                'detection_mode': True,
                'anonymization_applied': False,
                'detected_types': detection_result['detected_types'],
                'total_occurrences': detection_result['total_occurrences'],
                'agent_id': agent_id
            }
        )
        
        return {
            'record_id': record.id,
            'detection_result': detection_result,
            'original_content_preserved': True,
            'created_at': record.created_at.isoformat()
        }
    
    def set_detection_only_mode(self, enabled: bool = True):
        """Ativa/desativa modo global de detecção apenas"""
        self.detection_only_mode = enabled
        logger.info(f"Modo detecção apenas: {'ATIVADO' if enabled else 'DESATIVADO'}")
    
    def analyze_document_privacy_risks(self, content: str) -> Dict[str, Any]:
        """Analisa riscos de privacidade de um documento sem modificá-lo"""
        
        detection = self.detect_personal_data_only(content, detailed=True)
        
        # Calcula score de risco
        risk_scores = {
            'cpf': 10,
            'cnpj': 8,
            'email': 6,
            'phone': 7,
            'rg': 9,
            'cep': 4,
            'nome_proprio': 5
        }
        
        total_risk = 0
        for data_type, details in detection.get('details', {}).items():
            type_risk = risk_scores.get(data_type, 3)
            total_risk += type_risk * details['count']
        
        # Classifica risco
        if total_risk == 0:
            risk_level = "BAIXO"
            risk_description = "Nenhum dado pessoal detectado"
        elif total_risk <= 10:
            risk_level = "BAIXO"
            risk_description = "Poucos dados pessoais de baixo risco"
        elif total_risk <= 30:
            risk_level = "MÉDIO"
            risk_description = "Dados pessoais presentes, requer atenção"
        elif total_risk <= 60:
            risk_level = "ALTO"
            risk_description = "Muitos dados pessoais, alto risco LGPD"
        else:
            risk_level = "CRÍTICO"
            risk_description = "Dados altamente sensíveis, compliance obrigatório"
        
        return {
            'risk_level': risk_level,
            'risk_score': total_risk,
            'risk_description': risk_description,
            'detection_summary': detection,
            'recommendations': self._get_privacy_recommendations(detection, risk_level),
            'lgpd_compliance_required': risk_level in ["ALTO", "CRÍTICO"]
        }
    
    def _get_privacy_recommendations(self, detection: Dict[str, Any], risk_level: str) -> List[str]:
        """Gera recomendações baseadas na detecção"""
        recommendations = []
        
        if not detection['has_personal_data']:
            recommendations.append("✅ Documento seguro - nenhum dado pessoal detectado")
            return recommendations
        
        detected_types = detection['detected_types']
        
        if 'cpf' in detected_types:
            recommendations.append("🔒 CPF detectado - considere anonimização ou mascaramento")
        
        if 'cnpj' in detected_types:
            recommendations.append("🏢 CNPJ detectado - verifique se é necessário para o processamento")
        
        if 'email' in detected_types:
            recommendations.append("📧 E-mail detectado - implemente controles de acesso")
        
        if 'phone' in detected_types:
            recommendations.append("📱 Telefone detectado - considere mascaramento parcial")
        
        if 'rg' in detected_types:
            recommendations.append("🆔 RG detectado - dados sensíveis, anonimização recomendada")
        
        if risk_level in ["ALTO", "CRÍTICO"]:
            recommendations.extend([
                "⚠️ Implementar controles de acesso rigorosos",
                "📋 Documentar finalidade do processamento",
                "🔄 Estabelecer política de retenção",
                "👤 Obter consentimento explícito quando necessário"
            ])
        
        return recommendations

# Instância global
privacy_manager = DataLifecycleManager() 