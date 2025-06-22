# 🚀 Guia da Extensão Chrome RAG-Control

## 📋 Pré-requisitos

1. ✅ Servidor rodando em `http://192.168.8.4:5000`
2. ✅ Pelo menos 1 agente criado no sistema
3. ✅ Chrome com modo desenvolvedor ativado

## 🔧 Instalação da Extensão

1. **Abra o Chrome** e vá para `chrome://extensions/`
2. **Ative o modo desenvolvedor** (toggle no canto superior direito)
3. **Clique em "Carregar sem compactação"**
4. **Selecione a pasta**: `C:\Users\Jessé Freitas\rag_python\rag_python\scraper_extension`
5. **A extensão será instalada** ✅

## ⚙️ Configuração OBRIGATÓRIA

### Passo 1: Configurar URL da API

1. **Clique no ícone da extensão** na barra de ferramentas
2. **Clique em "Configurações"** (ícone de engrenagem)
3. **Configure a URL da API**:
   ```
   http://192.168.8.4:5000
   ```
4. **Clique em "Salvar"**

### Passo 2: Testar Conectividade

1. **Clique no ícone da extensão** novamente
2. **Verifique se aparece**:
   - ✅ Lista de agentes carregada
   - ✅ Informações da página atual
   - ✅ Botão "Capturar Página" ativo

## 🎯 Como Usar

1. **Navegue** para qualquer página web
2. **Clique no ícone da extensão**
3. **Selecione o agente** no dropdown
4. **Clique em "Capturar Página"**
5. **Aguarde** a notificação de sucesso

## 🐛 Solução de Problemas

### ❌ "Falha na conectividade: Failed to fetch"

**Causa**: URL da API não configurada ou servidor não está rodando

**Solução**:
1. Verifique se o servidor está rodando: `http://192.168.8.4:5000`
2. Configure a URL nas opções da extensão
3. Recarregue a extensão

### ❌ "Nenhum agente ativo encontrado"

**Causa**: Não há agentes criados no sistema

**Solução**:
1. Acesse `http://192.168.8.4:5000/agents`
2. Crie pelo menos um agente
3. Recarregue a extensão

### ❌ Extensão não aparece

**Causa**: Erro na instalação

**Solução**:
1. Verifique se o modo desenvolvedor está ativo
2. Remova e reinstale a extensão
3. Verifique se não há erros no console

## 📊 Verificação de Status

### Teste Manual da API

Execute no terminal:
```bash
# Teste de conectividade
curl http://192.168.8.4:5000/api/v1/extension/health

# Teste de agentes
curl http://192.168.8.4:5000/api/v1/extension/agents
```

### Logs da Extensão

1. **Clique com o botão direito** no ícone da extensão
2. **Selecione "Inspecionar popup"**
3. **Vá para a aba "Console"**
4. **Veja os logs de debug**

## ✅ Status Atual

- ✅ Servidor funcionando em `http://192.168.8.4:5000`
- ✅ API da extensão operacional
- ✅ 1 agente disponível ("AGENTE CÍVEL")
- ✅ Endpoints testados e funcionando

## 🎉 Tudo Funcionando!

Se seguiu todos os passos, a extensão deve estar capturando páginas web e adicionando à base de conhecimento dos seus agentes RAG!

---

**💡 Dica**: Mantenha o servidor sempre rodando quando usar a extensão. 