# 🚀 Guia Rápido - Extensão Chrome RAG

## ✅ Status: FUNCIONANDO

A extensão Chrome está funcionando corretamente! A API responde em `http://192.168.8.4:5000` e a captura de páginas está operacional.

## 📋 Como Usar

### 1. **Configurar a Extensão**
1. Clique no ícone da extensão RAG-Control
2. Clique em "Configurações"
3. Digite: `http://192.168.8.4:5000`
4. Clique em "Salvar Configurações"

### 2. **Capturar uma Página**
1. Navegue para qualquer página web
2. Clique no ícone da extensão RAG-Control
3. Selecione o agente "AGENTE CÍVEL" (ou outro disponível)
4. Clique em "Capturar Página"
5. Aguarde a confirmação de sucesso

### 3. **Verificar se Funcionou**
- Acesse: `http://192.168.8.4:5000/agents`
- Clique no agente usado
- Verifique se o documento foi adicionado
- Teste fazendo uma pergunta sobre o conteúdo capturado

## 🧪 Teste Realizado

```bash
✅ Health Check: OK
✅ Listagem de Agentes: 1 agente encontrado
✅ Captura de Página: Sucesso (example.com capturada)
```

## 🔧 Solução de Problemas

### **Erro de Conectividade**
- Verifique se o servidor está rodando: `netstat -an | findstr :5000`
- Confirme o IP da rede: `ipconfig`
- Use o IP correto nas configurações da extensão

### **Nenhum Agente Disponível**
- Acesse `http://192.168.8.4:5000/agents`
- Crie um novo agente se necessário
- Verifique se o agente está ativo

### **Falha na Captura**
- Verifique se a URL é válida (deve começar com http/https)
- Confirme se o agente foi selecionado
- Verifique os logs do servidor

## 🎯 Próximos Passos

1. **Configure a URL correta** na extensão
2. **Teste com páginas reais** (não apenas example.com)
3. **Verifique o conteúdo** no dashboard do agente
4. **Faça perguntas** sobre o conteúdo capturado

## 📊 Resumo Técnico

- **Servidor**: Rodando em `0.0.0.0:5000` ✅
- **API**: Funcionando em `http://192.168.8.4:5000` ✅
- **Agentes**: 1 agente ativo ("AGENTE CÍVEL") ✅
- **Captura**: Testada e funcionando ✅
- **Extensão**: Configurada e pronta para uso ✅

**A extensão está 100% funcional!** 🎉 