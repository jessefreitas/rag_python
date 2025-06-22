"""
Modelos para o sistema de geração de documentos
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Literal, Optional
from datetime import datetime
import uuid

class DocRequest(BaseModel):
    """Requisição para geração de documento"""
    
    # Identificação
    agent_id: str = Field(..., description="ID do agente que solicita o documento")
    tipo_documento: str = Field(..., description="Tipo do documento a ser gerado")
    
    # Dados do documento
    variaveis: Dict[str, str] = Field(..., description="Variáveis para preenchimento do template")
    formato: Literal["docx", "pdf"] = "pdf"
    
    # Configurações opcionais
    use_ai_enhancement: bool = Field(True, description="Usar IA para melhorar o conteúdo")
    template_version: Optional[str] = Field(None, description="Versão específica do template")
    
    # Metadados
    solicitante: Optional[str] = Field(None, description="Nome do solicitante")
    observacoes: Optional[str] = Field(None, description="Observações especiais")
    
    @validator('agent_id')
    def validate_agent_id(cls, v):
        if not v or len(v) < 10:
            raise ValueError('Agent ID deve ter pelo menos 10 caracteres')
        return v
    
    @validator('tipo_documento')
    def validate_tipo_documento(cls, v):
        documentos_permitidos = [
            'contrato_prestacao_servicos',
            'peticao_inicial_civel', 
            'procuracao',
            'nda_confidencialidade',
            'parecer_juridico',
            'contestacao',
            'recurso_apelacao'
        ]
        if v not in documentos_permitidos:
            raise ValueError(f'Tipo de documento deve ser um de: {documentos_permitidos}')
        return v

class DocResponse(BaseModel):
    """Resposta da geração de documento"""
    
    # Status da operação
    status: Literal["sucesso", "erro", "processando"] 
    mensagem: str = Field(..., description="Mensagem descritiva do status")
    
    # Arquivo gerado
    documento_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url_arquivo: Optional[str] = Field(None, description="URL para download do arquivo")
    nome_arquivo: Optional[str] = Field(None, description="Nome do arquivo gerado")
    
    # Metadados
    tipo_documento: Optional[str] = None
    formato: Optional[str] = None
    tamanho_bytes: Optional[int] = None
    agent_id: Optional[str] = None
    
    # Timestamps
    criado_em: datetime = Field(default_factory=datetime.now)
    expira_em: Optional[datetime] = None
    
    # Informações de IA (se usada)
    ai_enhancement_used: bool = False
    ai_model_used: Optional[str] = None
    ai_tokens_consumed: Optional[int] = None

class DocumentTemplate(BaseModel):
    """Modelo para templates de documentos"""
    
    nome: str = Field(..., description="Nome do template")
    tipo: str = Field(..., description="Tipo de documento")
    versao: str = Field("1.0.0", description="Versão do template")
    
    # Metadados do template
    descricao: Optional[str] = None
    autor: Optional[str] = None
    area_juridica: Optional[str] = None
    
    # Configurações
    variaveis_obrigatorias: list[str] = Field(default_factory=list)
    variaveis_opcionais: list[str] = Field(default_factory=list)
    
    # Controle
    ativo: bool = True
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)

class DocumentAudit(BaseModel):
    """Modelo para auditoria de documentos gerados"""
    
    documento_id: str
    agent_id: str
    tipo_documento: str
    
    # Ação realizada
    acao: Literal["criado", "baixado", "excluido", "expirado"]
    usuario: Optional[str] = None
    ip_origem: Optional[str] = None
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Dados adicionais
    detalhes: Optional[Dict] = None 