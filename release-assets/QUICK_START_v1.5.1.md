# ⚡ RAG Python v1.5.1 - Guia de Instalação Rápida

## 🚀 **Setup em 5 Minutos**

### **1. 📥 Download e Clone**
```bash
# Opção 1: Clone direto
git clone https://github.com/jessefreitas/rag_python.git
cd rag_python
git checkout v1.5.1-stable

# Opção 2: Download da release
# Baixe o ZIP da release e extraia
```

### **2. 🐍 Ambiente Python**
```bash
# Python 3.10+ obrigatório
python --version

# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### **3. 📦 Instalação de Dependências**
```bash
# Instalar dependências principais
pip install -r requirements.txt

# Dependências de teste (opcional)
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

### **4. 🔑 Configuração de API Keys**
```bash
# Copiar arquivo de exemplo
copy env_example.txt .env

# Editar .env com suas keys:
# OPENAI_API_KEY=sk-your-openai-key
# GOOGLE_API_KEY=your-google-key
# OPENROUTER_API_KEY=your-openrouter-key
# DEEPSEEK_API_KEY=your-deepseek-key
```

### **5. ✅ Validação**
```bash
# Executar testes para validar instalação
pytest test_integration_complete.py -v

# Deve mostrar: 1 passed ✅
```

## 🚀 **Execução Rápida**

### **🌐 API REST**
```bash
# Iniciar servidor API
python api_server.py

# Acesse: http://localhost:5000/docs
```

### **📊 Interface Streamlit**
```bash
# Interface principal
streamlit run app.py

# Interface multi-LLM
streamlit run app_multi_llm.py

# Dashboard LGPD
streamlit run app_privacy_dashboard.py
```

### **🤖 Demo CrewAI**
```bash
# Demonstração dos workflows
python demo_crewai_workflows.py
```

## 🎯 **Casos de Uso Rápidos**

### **1. 📄 Geração de Documento**
```python
from document_generation.services.doc_generator import document_generator

# Gerar contrato
doc_request = {
    "tipo_documento": "contrato_prestacao_servicos",
    "dados": {
        "cliente_nome": "João Silva",
        "prestador_nome": "Tech Solutions Ltda",
        "servico": "Desenvolvimento de Software",
        "valor": "R$ 10.000,00"
    }
}

resultado = document_generator.generate_document(doc_request)
print(f"Documento gerado: {resultado['file_path']}")
```

### **2. 🔒 Verificação LGPD**
```python
from privacy_system import privacy_manager

# Detectar dados pessoais
texto = "João Silva, CPF: 123.456.789-10, email: joao@email.com"
deteccao = privacy_manager.detect_personal_data_only(texto)

print(f"Dados pessoais detectados: {deteccao['detected_types']}")
```

### **3. 🤖 Workflow CrewAI**
```python
from crew.orchestrator import crew_orchestrator
from crew.pipelines import LegalDocumentPipeline

# Executar pipeline jurídico
pipeline = LegalDocumentPipeline()
resultado = crew_orchestrator.execute_pipeline(
    pipeline, 
    {"consulta": "Como elaborar um contrato de prestação de serviços?"}
)

print(f"Resultado: {resultado}")
```

## 🛠️ **Solução de Problemas**

### **❌ Erro de Importação**
```bash
# Reinstalar dependências
pip install --force-reinstall -r requirements.txt
```

### **❌ Erro de API Key**
```bash
# Verificar se .env está configurado
cat .env  # Linux/Mac
type .env  # Windows
```

### **❌ Erro de PostgreSQL**
```bash
# PostgreSQL é opcional, pode usar SQLite
# Comentar DATABASE_URL no .env se não tiver PostgreSQL
```

### **❌ Erro de Testes**
```bash
# Executar apenas testes básicos
pytest test_pytest_suite.py::TestPrivacySystem -v
```

## 📞 **Suporte Rápido**

### **🆘 Problemas Comuns**
1. **Python < 3.10:** Atualize para Python 3.10+
2. **Dependências:** Execute `pip install --upgrade pip`
3. **API Keys:** Verifique se estão corretas no .env
4. **Permissões:** Execute como administrador se necessário

### **📋 Verificação do Sistema**
```bash
# Script de verificação rápida
python -c "
import sys
print(f'Python: {sys.version}')
try:
    from privacy_system import privacy_manager
    print('✅ Privacy system OK')
except:
    print('❌ Privacy system ERROR')
    
try:
    from crew.orchestrator import crew_orchestrator
    print('✅ CrewAI OK')
except:
    print('❌ CrewAI ERROR')
"
```

## 🎉 **Pronto!**

Se chegou até aqui, seu sistema RAG Python v1.5.1 está funcionando!

### **🔗 Links Úteis**
- **Documentação:** [GitHub Wiki](https://github.com/jessefreitas/rag_python/wiki)
- **Issues:** [GitHub Issues](https://github.com/jessefreitas/rag_python/issues)
- **API Docs:** http://localhost:5000/docs (após iniciar)

### **🚀 Próximos Passos**
1. Explore os demos em `demo_*.py`
2. Configure seus agentes em `agents_config.json`
3. Teste os workflows CrewAI
4. Implemente seus casos de uso

**Bem-vindo ao futuro dos sistemas RAG! 🎊** 