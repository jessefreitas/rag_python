#!/usr/bin/env python3
"""
Script para iniciar o servidor Flask com configuração de rede explícita
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Inicia o servidor Flask com configuração de rede"""
    
    print("🚀 Iniciando servidor RAG Python...")
    print("📡 Configuração de rede: 0.0.0.0:5000")
    print("🌐 Acessível em: http://192.168.8.4:5000")
    print("🏠 Local: http://localhost:5000")
    print("-" * 50)
    
    try:
        # Importar e configurar o app Flask
        from web_agent_manager import app
        
        # Configurações explícitas
        app.config['DEBUG'] = True
        app.config['THREADED'] = True
        
        # Iniciar servidor com configuração explícita
        app.run(
            host='0.0.0.0',  # Aceitar conexões de qualquer IP
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=False  # Evitar problemas de reinicialização
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        logging.error(f"Erro ao iniciar servidor: {e}", exc_info=True)

if __name__ == "__main__":
    main() 