import sqlite3
import json
from datetime import datetime
from typing import Dict, Any

class MetricsCollector:
    """Coleta e armazena métricas do sistema"""
    
    def __init__(self, db_file: str = "metrics.db"):
        self.db_file = db_file
        self._init_db()
    
    def _init_db(self):
        """Inicializa banco de métricas"""
        conn = sqlite3.connect(self.db_file)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                provider TEXT,
                model TEXT,
                response_time REAL,
                token_count INTEGER,
                success BOOLEAN,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def record_llm_request(self, provider: str, model: str, response_time: float, 
                          success: bool, token_count: int = None, metadata: Dict = None):
        """Registra requisição LLM"""
        conn = sqlite3.connect(self.db_file)
        conn.execute("""
            INSERT INTO metrics (event_type, provider, model, response_time, token_count, success, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'llm_request',
            provider,
            model,
            response_time,
            token_count,
            success,
            json.dumps(metadata) if metadata else None
        ))
        conn.commit()
        conn.close()
    
    def get_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Obtém estatísticas das últimas horas"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT provider, COUNT(*) as requests, AVG(response_time) as avg_time,
                   SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
            FROM metrics 
            WHERE timestamp > datetime('now', '-{} hours')
            GROUP BY provider
        """.format(hours))
        
        stats = {}
        for row in cursor.fetchall():
            provider, requests, avg_time, successful = row
            stats[provider] = {
                'requests': requests,
                'avg_response_time': round(avg_time, 2) if avg_time else 0,
                'success_rate': round((successful / requests) * 100, 2) if requests else 0
            }
        
        conn.close()
        return stats
