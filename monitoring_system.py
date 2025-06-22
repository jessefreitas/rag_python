#!/usr/bin/env python3
"""
Sistema de Monitoramento e Observabilidade - RAG Python v1.3.0
Coleta métricas, logs e monitora performance do sistema
"""

import os
import sys
import time
import psutil
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
from functools import wraps
import sqlite3

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_percent: float
    network_sent_mb: float
    network_recv_mb: float

@dataclass
class APIMetrics:
    """Métricas de APIs"""
    timestamp: datetime
    provider: str
    endpoint: str
    response_time: float
    status_code: int
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None

@dataclass
class PrivacyMetrics:
    """Métricas de privacidade"""
    timestamp: datetime
    operation: str
    data_category: str
    records_processed: int
    pii_detected: int
    anonymization_applied: bool
    compliance_status: str

class MetricsCollector:
    """Coletor de métricas do sistema"""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self.init_database()
        self.system_metrics = deque(maxlen=1000)
        self.api_metrics = deque(maxlen=5000)
        self.privacy_metrics = deque(maxlen=2000)
        self.monitoring_active = False
        self.monitor_thread = None
        
    def init_database(self):
        """Inicializa banco de dados para métricas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de métricas do sistema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                memory_used_mb REAL,
                disk_percent REAL,
                network_sent_mb REAL,
                network_recv_mb REAL
            )
        ''')
        
        # Tabela de métricas de API
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                provider TEXT,
                endpoint TEXT,
                response_time REAL,
                status_code INTEGER,
                tokens_used INTEGER,
                cost_estimate REAL
            )
        ''')
        
        # Tabela de métricas de privacidade
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS privacy_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT,
                data_category TEXT,
                records_processed INTEGER,
                pii_detected INTEGER,
                anonymization_applied BOOLEAN,
                compliance_status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Rede
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024 * 1024)
            network_recv_mb = network.bytes_recv / (1024 * 1024)
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                disk_percent=disk_percent,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb
            )
            
            self.system_metrics.append(metrics)
            self.save_system_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return None
    
    def record_api_call(self, provider: str, endpoint: str, response_time: float, 
                       status_code: int, tokens_used: Optional[int] = None,
                       cost_estimate: Optional[float] = None):
        """Registra chamada de API"""
        metrics = APIMetrics(
            timestamp=datetime.now(),
            provider=provider,
            endpoint=endpoint,
            response_time=response_time,
            status_code=status_code,
            tokens_used=tokens_used,
            cost_estimate=cost_estimate
        )
        
        self.api_metrics.append(metrics)
        self.save_api_metrics(metrics)
        
        # Log para monitoramento
        logger.info(f"API Call: {provider}/{endpoint} - {response_time:.2f}s - Status: {status_code}")
    
    def record_privacy_operation(self, operation: str, data_category: str,
                                records_processed: int, pii_detected: int,
                                anonymization_applied: bool, compliance_status: str):
        """Registra operação de privacidade"""
        metrics = PrivacyMetrics(
            timestamp=datetime.now(),
            operation=operation,
            data_category=data_category,
            records_processed=records_processed,
            pii_detected=pii_detected,
            anonymization_applied=anonymization_applied,
            compliance_status=compliance_status
        )
        
        self.privacy_metrics.append(metrics)
        self.save_privacy_metrics(metrics)
        
        # Log para compliance
        logger.info(f"Privacy Operation: {operation} - Category: {data_category} - PII: {pii_detected}")
    
    def save_system_metrics(self, metrics: SystemMetrics):
        """Salva métricas do sistema no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, memory_used_mb, disk_percent, network_sent_mb, network_recv_mb)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp.isoformat(),
                metrics.cpu_percent,
                metrics.memory_percent,
                metrics.memory_used_mb,
                metrics.disk_percent,
                metrics.network_sent_mb,
                metrics.network_recv_mb
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao salvar métricas do sistema: {e}")
    
    def save_api_metrics(self, metrics: APIMetrics):
        """Salva métricas de API no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_metrics 
                (timestamp, provider, endpoint, response_time, status_code, tokens_used, cost_estimate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp.isoformat(),
                metrics.provider,
                metrics.endpoint,
                metrics.response_time,
                metrics.status_code,
                metrics.tokens_used,
                metrics.cost_estimate
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao salvar métricas de API: {e}")
    
    def save_privacy_metrics(self, metrics: PrivacyMetrics):
        """Salva métricas de privacidade no banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO privacy_metrics 
                (timestamp, operation, data_category, records_processed, pii_detected, anonymization_applied, compliance_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp.isoformat(),
                metrics.operation,
                metrics.data_category,
                metrics.records_processed,
                metrics.pii_detected,
                metrics.anonymization_applied,
                metrics.compliance_status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao salvar métricas de privacidade: {e}")
    
    def start_monitoring(self, interval: int = 30):
        """Inicia monitoramento contínuo"""
        if self.monitoring_active:
            logger.warning("Monitoramento já está ativo")
            return
        
        self.monitoring_active = True
        
        def monitor_loop():
            while self.monitoring_active:
                self.collect_system_metrics()
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"Monitoramento iniciado com intervalo de {interval}s")
    
    def stop_monitoring(self):
        """Para monitoramento contínuo"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Monitoramento parado")
    
    def get_system_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Retorna resumo das métricas do sistema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT AVG(cpu_percent), MAX(cpu_percent), AVG(memory_percent), MAX(memory_percent),
                       AVG(memory_used_mb), MAX(memory_used_mb), COUNT(*)
                FROM system_metrics 
                WHERE timestamp > ?
            ''', (since.isoformat(),))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] is not None:
                return {
                    'period_hours': hours,
                    'cpu_avg': round(result[0], 2),
                    'cpu_max': round(result[1], 2),
                    'memory_avg': round(result[2], 2),
                    'memory_max': round(result[3], 2),
                    'memory_used_avg_mb': round(result[4], 2),
                    'memory_used_max_mb': round(result[5], 2),
                    'data_points': result[6]
                }
            else:
                return {'period_hours': hours, 'data_points': 0, 'message': 'Dados insuficientes'}
                
        except Exception as e:
            logger.error(f"Erro ao gerar resumo do sistema: {e}")
            return {'error': str(e)}

# Decorador para monitoramento automático de funções
def monitor_performance(operation_name: str = None):
    """Decorador para monitorar performance de funções"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                response_time = end_time - start_time
                
                logger.debug(f"Performance: {operation} executado em {response_time:.3f}s")
                return result
                
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                logger.error(f"Error in {operation}: {e}")
                raise
        
        return wrapper
    return decorator

# Instância global do coletor de métricas
metrics_collector = MetricsCollector()

def get_system_health() -> Dict[str, Any]:
    """Retorna status de saúde do sistema"""
    try:
        # Métricas atuais
        current_metrics = metrics_collector.collect_system_metrics()
        
        # Determina status de saúde
        health_status = "healthy"
        issues = []
        
        if current_metrics:
            if current_metrics.cpu_percent > 80:
                health_status = "warning"
                issues.append(f"CPU alta: {current_metrics.cpu_percent}%")
            
            if current_metrics.memory_percent > 85:
                health_status = "critical" if current_metrics.memory_percent > 95 else "warning"
                issues.append(f"Memória alta: {current_metrics.memory_percent}%")
            
            if current_metrics.disk_percent > 90:
                health_status = "critical"
                issues.append(f"Disco cheio: {current_metrics.disk_percent}%")
        
        # Resumo das últimas 24h
        system_summary = metrics_collector.get_system_summary(24)
        
        return {
            'status': health_status,
            'timestamp': datetime.now().isoformat(),
            'issues': issues,
            'current_metrics': asdict(current_metrics) if current_metrics else None,
            'system_summary': system_summary
        }
        
    except Exception as e:
        logger.error(f"Erro ao verificar saúde do sistema: {e}")
        return {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

if __name__ == "__main__":
    # Exemplo de uso
    print("🔍 Sistema de Monitoramento - RAG Python v1.3.0")
    print("=" * 50)
    
    # Inicia monitoramento
    metrics_collector.start_monitoring(interval=10)
    
    try:
        # Simula algumas operações
        time.sleep(5)
        
        # Registra algumas métricas de exemplo
        metrics_collector.record_api_call("openai", "chat/completions", 1.2, 200, 150, 0.003)
        metrics_collector.record_privacy_operation(
            operation="DETECT_ONLY",
            data_category="personal", 
            records_processed=1,
            pii_detected=3,
            anonymization_applied=False,
            compliance_status="compliant"
        )
        
        # Verifica saúde do sistema
        health = get_system_health()
        print(f"\n📊 Status do Sistema: {health['status'].upper()}")
        
        if health['current_metrics']:
            print(f"💾 CPU: {health['current_metrics']['cpu_percent']:.1f}%")
            print(f"🧠 Memória: {health['current_metrics']['memory_percent']:.1f}%")
        
    except KeyboardInterrupt:
        print("\n⏹️  Interrompido pelo usuário")
    finally:
        metrics_collector.stop_monitoring()
        print("✅ Monitoramento finalizado") 