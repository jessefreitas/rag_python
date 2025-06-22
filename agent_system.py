import os
import logging
from datetime import datetime
import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional

from vector_store import VectorStore
from rag_system import RAGSystem
from llm_providers import llm_manager
from database import Database

logging.basicConfig(level=logging.INFO)

class Agent:
    def __init__(self, data: Dict[str, Any]):
        self.id = str(data.get('id'))
        self.name = data.get('name')
        self.description = data.get('description')
        self.system_prompt = data.get('system_prompt')
        self.model = data.get('model', 'gpt-4o-mini')
        self.temperature = float(data.get('temperature', 0.7))
        self.created_at = data.get('created_at', datetime.now())
        
        self.rag_system = RAGSystem(agent_id=self.id)
        self.llm_provider_name = llm_manager.active_provider

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "model": self.model,
            "temperature": self.temperature,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
    def add_document(self, file_path: str):
        self.rag_system.add_document(file_path)

    def add_document_from_text(self, content: str, source: str):
        """Adiciona um documento ao sistema RAG a partir de um conteúdo de texto."""
        self.rag_system.add_document_from_text(content, source)

    def get_response(self, user_message: str, history: List[Dict[str, str]]) -> str:
        return self.rag_system.get_response(
            user_message, 
            history, 
            self.system_prompt, 
            self.temperature, 
            self.model
        )
        
    def get_multi_llm_response(self, user_message: str, history: List[Dict[str, str]], providers: List[str]):
        context = self.rag_system.get_relevant_context(user_message)
        return self.rag_system.get_multi_response(user_message, context, history, self.system_prompt, self.temperature, providers)

    @staticmethod
    def _execute_query(query: str, params: tuple = (), fetch: Optional[str] = None):
        conn = None
        try:
            conn = Database.get_connection()
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, params)
                if fetch == 'one':
                    result = cur.fetchone()
                elif fetch == 'all':
                    result = cur.fetchall()
                else:
                    result = None
                conn.commit()
                return result
        except Exception as e:
            logging.error(f"Database query failed: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if conn: Database.release_connection(conn)

    @classmethod
    def get_by_id(cls, agent_id: str) -> Optional['Agent']:
        row = cls._execute_query("SELECT * FROM agentes WHERE id = %s", (agent_id,), fetch='one')
        return cls(row) if row else None

    @classmethod
    def get_all(cls) -> List['Agent']:
        rows = cls._execute_query("SELECT * FROM agentes ORDER BY created_at DESC", fetch='all')
        return [cls(row) for row in rows] if rows else []

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Optional['Agent']:
        query = "INSERT INTO agentes (name, description, system_prompt, model, temperature) VALUES (%s, %s, %s, %s, %s) RETURNING *;"
        params = (data['name'], data.get('description'), data.get('system_prompt'), data.get('model'), data.get('temperature'))
        new_agent_data = cls._execute_query(query, params, fetch='one')
        return cls(new_agent_data) if new_agent_data else None

    @classmethod
    def update(cls, agent_id: str, data: Dict[str, Any]) -> Optional['Agent']:
        query = "UPDATE agentes SET name = %s, description = %s, system_prompt = %s, model = %s, temperature = %s WHERE id = %s RETURNING *;"
        params = (data['name'], data.get('description'), data.get('system_prompt'), data.get('model'), data.get('temperature'), agent_id)
        updated_agent_data = cls._execute_query(query, params, fetch='one')
        return cls(updated_agent_data) if updated_agent_data else None

    @classmethod
    def delete(cls, agent_id: str) -> bool:
        cls._execute_query("DELETE FROM agentes WHERE id = %s", (agent_id,))
        return True

    def save_conversation(self, user_message: str) -> Optional[str]:
        query = "INSERT INTO conversations (agent_id, user_message) VALUES (%s, %s) RETURNING id;"
        result = self._execute_query(query, (self.id, user_message), fetch='one')
        return str(result['id']) if result else None

    def save_llm_response(self, conversation_id: str, provider: str, model_used: str, response_text: str, tokens_used: int) -> Optional[str]:
        query = "INSERT INTO llm_responses (conversation_id, provider, model_used, response_text, tokens_used) VALUES (%s, %s, %s, %s, %s) RETURNING id;"
        params = (conversation_id, provider, model_used, response_text, tokens_used)
        result = self._execute_query(query, params, fetch='one')
        return str(result['id']) if result else None

    @staticmethod
    def set_feedback(response_id: str, feedback: int) -> bool:
        Agent._execute_query("UPDATE llm_responses SET feedback = %s WHERE id = %s", (feedback, response_id))
        return True

    def get_full_history(self) -> List[Dict[str, Any]]:
        query = """
            SELECT c.id as conv_id, c.user_message, c.created_at,
                   json_agg(json_build_object(
                       'id', r.id, 'provider', r.provider, 'model_used', r.model_used,
                       'response_text', r.response_text, 'feedback', r.feedback
                   ) ORDER BY r.created_at) FILTER (WHERE r.id IS NOT NULL) as responses
            FROM conversations c
            LEFT JOIN llm_responses r ON c.id = r.conversation_id
            WHERE c.agent_id = %s
            GROUP BY c.id ORDER BY c.created_at ASC;
        """
        rows = self._execute_query(query, (self.id,), fetch='all')
        if not rows: return []
        
        history = []
        for row in rows:
            history.append({"id": str(row['conv_id']), "role": "user", "content": row['user_message']})
            if row['responses']:
                history.append({"id": str(row['conv_id']), "role": "assistant", "responses": [{
                        'id': str(resp['id']), 'provider': resp['provider'], 'content': resp['response_text'], 'feedback': resp['feedback']
                    } for resp in row['responses']]
                })
        return history

    def get_stats(self) -> Dict[str, Any]:
        doc_query = "SELECT COUNT(*) FROM documents WHERE agent_id = %s;"
        doc_count_result = self._execute_query(doc_query, (self.id,), fetch='one')
        doc_count = doc_count_result[0] if doc_count_result else 0

        feedback_query = """
            SELECT provider, 
                   COALESCE(SUM(CASE WHEN feedback = 1 THEN 1 ELSE 0 END), 0) as positive,
                   COALESCE(SUM(CASE WHEN feedback = -1 THEN 1 ELSE 0 END), 0) as negative
            FROM llm_responses r JOIN conversations c ON r.conversation_id = c.id
            WHERE c.agent_id = %s GROUP BY r.provider;
        """
        feedback_rows = self._execute_query(feedback_query, (self.id,), fetch='all')
        
        total_positive = sum(row['positive'] for row in feedback_rows) if feedback_rows else 0
        total_negative = sum(row['negative'] for row in feedback_rows) if feedback_rows else 0
        
        return {
            "total_documents": doc_count,
            "total_positive_feedback": int(total_positive),
            "total_negative_feedback": int(total_negative),
            "feedback_by_llm": {row['provider']: {'positive': int(row['positive']), 'negative': int(row['negative'])} for row in feedback_rows} if feedback_rows else {}
        } 