import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class ResponseCache:
    """Sistema de cache para respostas LLM"""
    
    def __init__(self, cache_file: str = "response_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Carrega cache do arquivo"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_cache(self):
        """Salva cache no arquivo"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False, default=str)
    
    def get_cache_key(self, messages: list, provider: str, model: str) -> str:
        """Gera chave única para cache"""
        content = f"{provider}_{model}_{json.dumps(messages, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, messages: list, provider: str, model: str, max_age_hours: int = 24) -> Optional[str]:
        """Recupera resposta do cache se válida"""
        key = self.get_cache_key(messages, provider, model)
        
        if key in self.cache:
            entry = self.cache[key]
            cached_time = datetime.fromisoformat(entry['timestamp'])
            
            if datetime.now() - cached_time < timedelta(hours=max_age_hours):
                return entry['response']
        
        return None
    
    def set(self, messages: list, provider: str, model: str, response: str):
        """Armazena resposta no cache"""
        key = self.get_cache_key(messages, provider, model)
        
        self.cache[key] = {
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'model': model
        }
        
        self._save_cache()
