"""
Orquestrador Principal CrewAI
Integração completa com o sistema RAG Python existente
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .pipelines import create_pipeline, BasePipeline
from .agents import create_agent_crew
from agent_system import Agent as RAGAgent
from privacy_system import PrivacyCompliance
from monitoring_system import MetricsCollector

logger = logging.getLogger(__name__)

class CrewOrchestrator:
    """Orquestrador principal para workflows CrewAI"""
    
    def __init__(self):
        self.active_pipelines: Dict[str, BasePipeline] = {}
        self.pipeline_history: List[Dict[str, Any]] = []
        self.privacy_manager = PrivacyCompliance()
        self.monitoring = MetricsCollector()
        
        # Estatísticas
        self.stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0
        }
    
    def create_workflow(self, 
                       agent_id: str, 
                       pipeline_type: str, 
                       workflow_id: Optional[str] = None) -> str:
        """Cria um novo workflow"""
        
        if workflow_id is None:
            workflow_id = f"{pipeline_type}_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Verificar se agente existe
            agent = RAGAgent.get_by_id(agent_id)
            if not agent:
                raise ValueError(f"Agente {agent_id} não encontrado")
            
            # Criar pipeline
            pipeline = create_pipeline(pipeline_type, agent_id)
            self.active_pipelines[workflow_id] = pipeline
            
            logger.info(f"Workflow {workflow_id} criado para agente {agent_id}")
            
            # Registrar no monitoramento
            self.monitoring.log_metric("workflow_created", 1, {
                'agent_id': agent_id,
                'pipeline_type': pipeline_type,
                'workflow_id': workflow_id
            })
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"Erro ao criar workflow: {e}")
            raise
    
    def execute_workflow(self, 
                        workflow_id: str, 
                        inputs: Dict[str, Any],
                        privacy_level: str = "standard") -> Dict[str, Any]:
        """Executa um workflow específico"""
        
        start_time = datetime.now()
        
        try:
            # Verificar se workflow existe
            if workflow_id not in self.active_pipelines:
                raise ValueError(f"Workflow {workflow_id} não encontrado")
            
            pipeline = self.active_pipelines[workflow_id]
            
            # Verificação de privacidade nos inputs
            privacy_check = self._check_privacy_compliance(inputs, privacy_level)
            if not privacy_check['approved']:
                return {
                    'success': False,
                    'error': 'Falha na verificação de privacidade',
                    'privacy_issues': privacy_check['issues'],
                    'workflow_id': workflow_id
                }
            
            # Executar pipeline
            logger.info(f"Iniciando execução do workflow {workflow_id}")
            result = pipeline.execute(inputs)
            
            # Calcular tempo de execução
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Atualizar estatísticas
            self._update_stats(True, execution_time)
            
            # Registrar histórico
            self._record_execution(workflow_id, inputs, result, execution_time)
            
            # Monitoramento
            self.monitoring.log_metric("workflow_executed", 1, {
                'workflow_id': workflow_id,
                'success': result['success'],
                'execution_time': execution_time
            })
            
            logger.info(f"Workflow {workflow_id} executado com sucesso em {execution_time:.2f}s")
            
            return {
                **result,
                'execution_time': execution_time,
                'privacy_approved': True
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, execution_time)
            
            logger.error(f"Erro na execução do workflow {workflow_id}: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'workflow_id': workflow_id,
                'execution_time': execution_time
            }
    
    async def execute_workflow_async(self, 
                                   workflow_id: str, 
                                   inputs: Dict[str, Any],
                                   privacy_level: str = "standard") -> Dict[str, Any]:
        """Execução assíncrona de workflow"""
        
        # Executar em thread separada para não bloquear
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.execute_workflow, 
            workflow_id, 
            inputs, 
            privacy_level
        )
    
    def execute_multi_workflow(self, 
                              workflow_configs: List[Dict[str, Any]],
                              parallel: bool = True) -> List[Dict[str, Any]]:
        """Executa múltiplos workflows"""
        
        if parallel:
            return self._execute_parallel_workflows(workflow_configs)
        else:
            return self._execute_sequential_workflows(workflow_configs)
    
    def _execute_parallel_workflows(self, workflow_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execução paralela de workflows"""
        
        async def run_parallel():
            tasks = []
            for config in workflow_configs:
                task = self.execute_workflow_async(
                    config['workflow_id'],
                    config['inputs'],
                    config.get('privacy_level', 'standard')
                )
                tasks.append(task)
            
            return await asyncio.gather(*tasks)
        
        return asyncio.run(run_parallel())
    
    def _execute_sequential_workflows(self, workflow_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execução sequencial de workflows"""
        
        results = []
        for config in workflow_configs:
            result = self.execute_workflow(
                config['workflow_id'],
                config['inputs'],
                config.get('privacy_level', 'standard')
            )
            results.append(result)
            
            # Se um workflow falhar, parar execução (opcional)
            if not result['success'] and config.get('stop_on_failure', False):
                break
        
        return results
    
    def _check_privacy_compliance(self, inputs: Dict[str, Any], privacy_level: str) -> Dict[str, Any]:
        """Verifica compliance de privacidade"""
        
        try:
            # Converter inputs para string para análise
            content = str(inputs)
            
            # Detectar dados pessoais
            detection_result = self.privacy_manager.detect_personal_data_only(content)
            
            # Avaliar se aprovado baseado no nível de privacidade
            if privacy_level == "detection_only":
                # Sempre aprovado, apenas detecta
                return {
                    'approved': True,
                    'detection_result': detection_result,
                    'issues': []
                }
            elif privacy_level == "standard" and detection_result['has_personal_data']:
                # Nível standard permite alguns dados pessoais
                sensitive_types = ['cpf', 'cnpj', 'rg']
                detected_sensitive = [t for t in detection_result['detected_types'] if t in sensitive_types]
                
                if detected_sensitive:
                    return {
                        'approved': False,
                        'detection_result': detection_result,
                        'issues': [f"Dados sensíveis detectados: {', '.join(detected_sensitive)}"]
                    }
            elif privacy_level in ["high", "maximum"] and detection_result['has_personal_data']:
                return {
                    'approved': False,
                    'detection_result': detection_result,
                    'issues': ["Dados pessoais não permitidos neste nível de privacidade"]
                }
            
            return {
                'approved': True,
                'detection_result': detection_result,
                'issues': []
            }
            
        except Exception as e:
            logger.error(f"Erro na verificação de privacidade: {e}")
            return {
                'approved': False,
                'detection_result': None,
                'issues': [f"Erro na verificação: {str(e)}"]
            }
    
    def _update_stats(self, success: bool, execution_time: float):
        """Atualiza estatísticas de execução"""
        
        self.stats['total_executions'] += 1
        
        if success:
            self.stats['successful_executions'] += 1
        else:
            self.stats['failed_executions'] += 1
        
        # Atualizar tempo médio
        total_time = self.stats['average_execution_time'] * (self.stats['total_executions'] - 1)
        self.stats['average_execution_time'] = (total_time + execution_time) / self.stats['total_executions']
    
    def _record_execution(self, workflow_id: str, inputs: Dict[str, Any], 
                         result: Dict[str, Any], execution_time: float):
        """Registra execução no histórico"""
        
        record = {
            'workflow_id': workflow_id,
            'timestamp': datetime.now().isoformat(),
            'execution_time': execution_time,
            'success': result['success'],
            'inputs_hash': hash(str(inputs)),  # Hash dos inputs para privacidade
            'result_summary': {
                'success': result['success'],
                'pipeline': result.get('pipeline'),
                'agent_id': result.get('agent_id')
            }
        }
        
        self.pipeline_history.append(record)
        
        # Manter apenas últimas 1000 execuções
        if len(self.pipeline_history) > 1000:
            self.pipeline_history = self.pipeline_history[-1000:]
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Obtém status de um workflow"""
        
        if workflow_id not in self.active_pipelines:
            return {'exists': False}
        
        pipeline = self.active_pipelines[workflow_id]
        
        # Buscar execuções no histórico
        executions = [r for r in self.pipeline_history if r['workflow_id'] == workflow_id]
        
        return {
            'exists': True,
            'workflow_id': workflow_id,
            'pipeline_type': pipeline.name,
            'agent_id': pipeline.agent_id,
            'total_executions': len(executions),
            'successful_executions': len([e for e in executions if e['success']]),
            'last_execution': executions[-1] if executions else None,
            'average_execution_time': sum(e['execution_time'] for e in executions) / len(executions) if executions else 0
        }
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """Lista todos os workflows ativos"""
        
        workflows = []
        for workflow_id, pipeline in self.active_pipelines.items():
            status = self.get_workflow_status(workflow_id)
            workflows.append(status)
        
        return workflows
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema"""
        
        return {
            'total_workflows': len(self.active_pipelines),
            'execution_stats': self.stats,
            'recent_executions': self.pipeline_history[-10:],  # Últimas 10 execuções
            'system_health': {
                'success_rate': (self.stats['successful_executions'] / self.stats['total_executions'] * 100) if self.stats['total_executions'] > 0 else 0,
                'average_execution_time': self.stats['average_execution_time']
            }
        }
    
    def cleanup_workflow(self, workflow_id: str) -> bool:
        """Remove um workflow da memória"""
        
        try:
            if workflow_id in self.active_pipelines:
                del self.active_pipelines[workflow_id]
                logger.info(f"Workflow {workflow_id} removido")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao remover workflow {workflow_id}: {e}")
            return False

# Instância global do orquestrador
crew_orchestrator = CrewOrchestrator() 