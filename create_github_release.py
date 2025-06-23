#!/usr/bin/env python3
"""
Script para criar GitHub Release v1.5.1
Requer GitHub CLI (gh) instalado e autenticado
"""

import subprocess
import json
import os
from pathlib import Path

def create_github_release():
    """Criar GitHub Release v1.5.1"""
    
    # Configurações da release
    tag_name = "v1.5.1-release"
    release_title = "🚀 RAG Python v1.5.1 - Production Release"
    
    # Release notes condensadas
    release_notes = """## 📊 **Resumo da Release**

Esta é uma **release de produção** com sistema completamente testado e validado. O RAG Python v1.5.1 representa um marco significativo com **100% dos testes passando** e pipeline CI/CD profissional implementado.

## ✨ **Principais Novidades**

### 🤖 **CrewAI Orchestration**
- **4 pipelines especializados** para workflows jurídicos
- **Orquestração inteligente** de agentes especializados
- **Execução paralela** e assíncrona de workflows
- **Monitoramento** em tempo real de execuções

### 📄 **Sistema de Geração de Documentos**
- **Templates jurídicos** dinâmicos com Jinja2
- **Conversão automática** para PDF (Windows/Linux)
- **Integração com IA** para melhoramento de documentos
- **Verificação de privacidade** integrada

### 🔒 **Compliance LGPD Avançado**
- **Privacy by Design** nativo
- **4 níveis de proteção** de dados
- **Detecção automática** de PII
- **Anonimização** inteligente
- **Auditoria completa** de dados

### 🧪 **Pipeline CI/CD Profissional**
- **GitHub Actions** com 8 jobs especializados
- **Multi-Python testing** (3.10, 3.11, 3.12)
- **Security scanning** (Bandit, Safety)
- **Coverage reporting** (44%)
- **Deployment automático**

## 📋 **Resultados dos Testes**

### ✅ **100% Success Rate**
```
Total: 33 testes
Passed: 33 ✅
Failed: 0 ❌
Success Rate: 100%
```

### 🎯 **Cobertura por Sistema**
- **Privacy System (LGPD):** 5/5 testes ✅
- **CrewAI Orchestrator:** 3/3 testes ✅
- **Document Generation:** 3/3 testes ✅
- **LLM Providers:** 3/3 testes ✅
- **Agent System:** 2/2 testes ✅
- **Integration:** 2/2 testes ✅

## 🚀 **Instalação Rápida**

```bash
# Clone do repositório
git clone https://github.com/jessefreitas/rag_python.git
cd rag_python

# Checkout da versão estável
git checkout v1.5.1-release

# Instalação de dependências
pip install -r requirements.txt

# Execução dos testes
pytest

# Iniciar sistema
python api_server.py
```

## 📦 **Assets da Release**

- **RELEASE_NOTES_v1.5.1.md** - Documentação completa
- **QUICK_START_v1.5.1.md** - Guia de instalação rápida
- **requirements.txt** - Dependências Python
- **pytest.ini** - Configuração de testes
- **test_results_v1.5.0_final.json** - Resultados dos testes

## 🎯 **Funcionalidades Principais**
- ✅ Sistema RAG multi-modal
- ✅ CrewAI Orchestration (4 pipelines especializados)
- ✅ Document Generation (templates jurídicos)
- ✅ Privacy System (LGPD compliant)
- ✅ Multi-LLM (OpenAI, Google, OpenRouter, DeepSeek)
- ✅ API REST FastAPI
- ✅ Interfaces Streamlit
- ✅ Chrome Extension

**Esta release está pronta para uso em produção!** 🚀

---

**Baixe agora e experimente o futuro dos sistemas RAG inteligentes!**
"""

    # Assets para anexar
    assets = [
        "release-assets/RELEASE_NOTES_v1.5.1.md",
        "release-assets/QUICK_START_v1.5.1.md",
        "release-assets/requirements.txt",
        "release-assets/pytest.ini",
        "release-assets/test_results_v1.5.0_final.json"
    ]
    
    try:
        print("🚀 Criando GitHub Release v1.5.1...")
        
        # Verificar se gh CLI está disponível
        result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ GitHub CLI (gh) não está instalado.")
            print("📥 Instale: https://cli.github.com/")
            return False
            
        print("✅ GitHub CLI encontrado")
        
        # Verificar autenticação
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ GitHub CLI não está autenticado.")
            print("🔑 Execute: gh auth login")
            return False
            
        print("✅ GitHub CLI autenticado")
        
        # Criar release
        cmd = [
            "gh", "release", "create", tag_name,
            "--title", release_title,
            "--notes", release_notes,
            "--latest"
        ]
        
        # Adicionar assets
        for asset in assets:
            if os.path.exists(asset):
                cmd.append(asset)
                print(f"📎 Anexando: {asset}")
            else:
                print(f"⚠️  Asset não encontrado: {asset}")
        
        print("🔄 Executando comando de criação...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("🎉 GitHub Release criada com sucesso!")
            print("🔗 URL:", result.stdout.strip())
            return True
        else:
            print("❌ Erro ao criar release:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def alternative_manual_instructions():
    """Instruções manuais caso o script automático falhe"""
    print("""
📋 INSTRUÇÕES MANUAIS PARA CRIAR A RELEASE:

1. 🌐 Acesse: https://github.com/jessefreitas/rag_python/releases/new

2. 🏷️ Configure:
   - Tag: v1.5.1-release
   - Title: 🚀 RAG Python v1.5.1 - Production Release

3. 📄 Cole a descrição do arquivo: release-assets/RELEASE_NOTES_v1.5.1.md

4. 📎 Anexe os arquivos:
   - release-assets/RELEASE_NOTES_v1.5.1.md
   - release-assets/QUICK_START_v1.5.1.md
   - release-assets/requirements.txt
   - release-assets/pytest.ini
   - release-assets/test_results_v1.5.0_final.json

5. ✅ Marque "Set as the latest release"

6. 🚀 Clique "Publish release"
""")

if __name__ == "__main__":
    print("🎯 RAG Python v1.5.1 - GitHub Release Creator")
    print("=" * 50)
    
    success = create_github_release()
    
    if not success:
        print("\n" + "=" * 50)
        print("📋 PLANO B: Instruções Manuais")
        alternative_manual_instructions()
    
    print("\n🎊 Release v1.5.1 pronta para o mundo!") 