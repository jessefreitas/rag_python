#!/usr/bin/env python3
import requests
import time

print("🔍 Testando servidor Flask...")

try:
    # Testar endpoint /api
    r = requests.get('http://localhost:5000/api', timeout=5)
    print(f"Status /api: {r.status_code}")
    if r.status_code == 200:
        print(f"Response /api: {r.json()}")
    
    # Testar endpoint /api/health
    r = requests.get('http://localhost:5000/api/health', timeout=5)
    print(f"Status /api/health: {r.status_code}")
    if r.status_code == 200:
        print(f"Response /api/health: {r.json()}")
    
    # Testar endpoint /api/agents
    r = requests.get('http://localhost:5000/api/agents', timeout=5)
    print(f"Status /api/agents: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Agentes encontrados: {len(data.get('agents', []))}")
        for agent in data.get('agents', []):
            print(f"  - {agent.get('name', 'N/A')}")
    
except Exception as e:
    print(f"Erro: {e}") 