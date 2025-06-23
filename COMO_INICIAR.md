# 🚀 COMO INICIAR O RAG PYTHON v1.5.1

## ⚡ **INICIALIZAÇÃO RÁPIDA** (Recomendado)

### **Windows:**
```bash
# Duplo clique ou execute no terminal:
start_rag.bat
```

### **Linux/Mac:**
```bash
python iniciar_servidor_rag.py
```

---

## 🎯 **O QUE O INICIALIZADOR FAZ:**

### **✅ Verificações Automáticas:**
1. **🔍 Dependências** - Verifica e instala pacotes necessários
2. **📁 Arquivos** - Confirma que todos os arquivos críticos existem  
3. **🔧 Encoding** - Corrige problemas de null bytes automaticamente
4. **🔑 APIs** - Verifica chaves de API configuradas
5. **🛑 Conflitos** - Para servidores existentes na porta 8501

### **🚀 Inicialização Robusta:**
- ✅ Mata processos antigos automaticamente
- ✅ Corrige problemas de encoding
- ✅ Carrega variáveis de ambiente (.env)
- ✅ Inicia servidor com configurações otimizadas
- ✅ Fornece URLs corretas

---

## 🌐 **ACESSAR O SISTEMA:**

Após a inicialização bem-sucedida:

### **🖥️ Interface Principal:**
```
http://localhost:8501
```

### **📱 7 Abas Disponíveis:**
1. **🏠 Dashboard** - Status e métricas
2. **💬 Chat RAG** - Conversação com documentos
3. **🤖 Agentes** - Sistema de agentes especializados  
4. **🔄 Multi-LLM** - Comparação de 4 provedores
5. **🔒 Privacidade** - Compliance LGPD
6. **📁 Documentos** - Upload e gestão
7. **⚙️ Configurações** - Controles avançados

---

## ⚠️ **SOLUÇÃO DE PROBLEMAS:**

### **❌ Erro "Port 8501 is already in use":**
```bash
# O inicializador resolve automaticamente, mas se persistir:
netstat -ano | findstr 8501
taskkill /PID <numero_do_pid> /F
```

### **❌ Erro "SyntaxError: null bytes":**
```bash
# O inicializador corrige automaticamente, mas se precisar manual:
python iniciar_servidor_rag.py
# Vai detectar e corrigir o problema
```

### **❌ Dependências faltando:**
```bash
# OPÇÃO 1 - Instalar requisitos mínimos (recomendado):
pip install -r requirements_minimal.txt

# OPÇÃO 2 - Instalar requisitos completos:
pip install -r requirements.txt

# OPÇÃO 3 - Instalação manual essencial:
pip install python-dotenv streamlit openai psycopg2 chromadb langchain
```

---

## 🔧 **INICIALIZAÇÃO MANUAL** (Se necessário)

### **1. Verificar Dependências:**
```bash
# OPÇÃO 1 - Requisitos mínimos (mais rápido):
pip install -r requirements_minimal.txt

# OPÇÃO 2 - Requisitos completos (desenvolvimento):
pip install -r requirements.txt

# OPÇÃO 3 - Apenas essenciais:
pip install python-dotenv streamlit
```

### **2. Carregar Variáveis de Ambiente:**
```bash
# Certifique-se de ter arquivo .env com:
OPENAI_API_KEY=sua_key_aqui
GOOGLE_API_KEY=sua_key_aqui
OPENROUTER_API_KEY=sua_key_aqui
DEEPSEEK_API_KEY=sua_key_aqui
```

### **3. Iniciar Servidor:**
```bash
streamlit run app_completo_unificado.py --server.port=8501
```

---

## 📊 **STATUS DO SISTEMA:**

O inicializador verifica automaticamente:

### **✅ Provedores LLM:**
- 🤖 OpenAI (gpt-4-0613)
- 🧠 Google Gemini (gemini-1.0-pro-vision-latest)
- 🔄 OpenRouter (mistralai/mistral-small-3.2-24b-instruct:free)
- ⚡ DeepSeek (deepseek-chat)

### **✅ PostgreSQL/Supabase:**
- 📊 Conexão: db.fwzztbgmzxruqmtmafhe.supabase.co
- 🔧 12 índices HNSW otimizados
- 📋 5/5 tabelas funcionais

### **✅ Funcionalidades Avançadas:**
- ⚡ Cache inteligente (60-80% economia API)
- 📈 Sistema de métricas em tempo real
- 🔒 Conformidade LGPD com Microsoft Presidio
- 🌐 Compatibilidade com extensão Chrome v1.5.3

---

## 🎉 **RESULTADO FINAL:**

Após execução bem-sucedida do inicializador:

```
🌐 Servidor rodando em: http://localhost:8501
📊 Sistema: 4/4 provedores LLM configurados
🗄️ PostgreSQL: Conectado e otimizado  
🚀 Status: TOTALMENTE OPERACIONAL
```

**✨ Sistema RAG Python v1.5.1 pronto para uso!** ✨ 