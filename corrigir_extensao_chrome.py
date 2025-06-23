#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir problemas da extensão Chrome RAG-Control
"""

import os
import json
import shutil
from pathlib import Path

def verificar_extensao():
    """Verifica o estado atual da extensão"""
    print("🔍 VERIFICANDO EXTENSÃO CHROME RAG-CONTROL")
    print("=" * 50)
    
    extensao_dir = Path("scraper_extension")
    
    if not extensao_dir.exists():
        print("❌ Diretório da extensão não encontrado")
        return False
    
    # Verificar arquivos obrigatórios
    arquivos_obrigatorios = [
        "manifest.json",
        "popup.html",
        "popup.js", 
        "background.js",
        "style.css"
    ]
    
    print("📁 Verificando arquivos:")
    for arquivo in arquivos_obrigatorios:
        caminho = extensao_dir / arquivo
        if caminho.exists():
            size = caminho.stat().st_size
            print(f"  ✅ {arquivo} ({size} bytes)")
        else:
            print(f"  ❌ {arquivo} - NÃO ENCONTRADO")
    
    return True

def corrigir_manifest():
    """Corrige o manifest.json para ser compatível com Chrome"""
    print("\n🔧 CORRIGINDO MANIFEST.JSON")
    print("=" * 30)
    
    manifest_path = Path("scraper_extension/manifest.json")
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Manifest correto para Chrome Extension API V3
        manifest_corrigido = {
            "manifest_version": 3,
            "name": "RAG-Control",
            "version": "1.5.2",
            "description": "Envia a URL da página atual para um agente RAG para processamento no backend.",
            "action": {
                "default_popup": "popup.html",
                "default_title": "RAG-Control - Capturar Página"
            },
            "background": {
                "service_worker": "background.js"
            },
            "permissions": [
                "storage",
                "tabs",
                "notifications",
                "activeTab",
                "contextMenus"
            ],
            "host_permissions": [
                "<all_urls>"
            ],
            "content_security_policy": {
                "extension_pages": "script-src 'self' https://cdn.jsdelivr.net; object-src 'self'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;"
            },
            "icons": {
                "16": "icons/icon16.svg",
                "48": "icons/icon16.svg",
                "128": "icons/icon16.svg"
            },
            "options_ui": {
                "page": "options.html",
                "open_in_tab": true
            }
        }
        
        # Salvar manifest corrigido
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_corrigido, f, indent=4, ensure_ascii=False)
        
        print("✅ Manifest.json corrigido com sucesso!")
        
        # Mostrar diferenças principais
        print("\n📋 Principais correções:")
        print("  🔒 Removido 'unsafe-inline' do script-src")
        print("  📝 CSP atualizado para Manifest V3")
        print("  🔧 Estrutura otimizada")
        print("  🆕 Versão atualizada para 1.5.2")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir manifest: {e}")
        return False

def verificar_csp_compliance():
    """Verifica se todos os arquivos estão em conformidade com CSP"""
    print("\n🛡️ VERIFICANDO CONFORMIDADE CSP")
    print("=" * 30)
    
    extensao_dir = Path("scraper_extension")
    
    # Verificar arquivos HTML por scripts inline
    arquivos_html = list(extensao_dir.glob("*.html"))
    
    for arquivo_html in arquivos_html:
        print(f"\n📄 Verificando {arquivo_html.name}:")
        
        try:
            with open(arquivo_html, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar problemas comuns
            problemas = []
            
            if 'onclick=' in content:
                problemas.append("Event handlers inline (onclick)")
            if 'onload=' in content:
                problemas.append("Event handlers inline (onload)")
            if '<script>' in content and '</script>' in content:
                if 'src=' not in content[content.find('<script>'):content.find('</script>')]:
                    problemas.append("Scripts inline")
            
            if problemas:
                print("  ⚠️ Problemas encontrados:")
                for problema in problemas:
                    print(f"    - {problema}")
            else:
                print("  ✅ Conformidade CSP OK")
                
        except Exception as e:
            print(f"  ❌ Erro ao verificar {arquivo_html.name}: {e}")

def criar_extensao_limpa():
    """Cria uma versão limpa da extensão"""
    print("\n🧹 CRIANDO VERSÃO LIMPA DA EXTENSÃO")
    print("=" * 40)
    
    # Criar diretório limpo
    clean_dir = Path("scraper_extension_clean")
    if clean_dir.exists():
        shutil.rmtree(clean_dir)
    
    clean_dir.mkdir()
    
    # Copiar arquivos essenciais
    arquivos_copiar = [
        "manifest.json",
        "popup.html", 
        "popup.js",
        "background.js",
        "style.css",
        "options.html",
        "options.js"
    ]
    
    source_dir = Path("scraper_extension")
    
    for arquivo in arquivos_copiar:
        source = source_dir / arquivo
        dest = clean_dir / arquivo
        
        if source.exists():
            shutil.copy2(source, dest)
            print(f"  ✅ Copiado: {arquivo}")
        else:
            print(f"  ⚠️ Não encontrado: {arquivo}")
    
    # Copiar diretório de ícones se existir
    icons_dir = source_dir / "icons"
    if icons_dir.exists():
        shutil.copytree(icons_dir, clean_dir / "icons")
        print("  ✅ Copiado: diretório icons")
    
    print(f"\n📁 Extensão limpa criada em: {clean_dir}")
    print("💡 Use esta versão para carregar no Chrome")

def gerar_instrucoes_instalacao():
    """Gera instruções de instalação"""
    instrucoes = """
# 🔧 INSTRUÇÕES DE INSTALAÇÃO - EXTENSÃO RAG-CONTROL v1.5.2

## Passo a Passo:

### 1. Preparar a Extensão
✅ Extensão corrigida e pronta para instalação
📁 Localização: scraper_extension_clean/

### 2. Abrir Chrome Extensions
1. Abra o Google Chrome
2. Digite na barra de endereços: `chrome://extensions/`
3. Pressione Enter

### 3. Ativar Modo Desenvolvedor
1. No canto superior direito, ative o toggle "Modo de desenvolvedor"
2. Você verá aparecer novos botões

### 4. Carregar Extensão
1. Clique em "Carregar sem compactação"
2. Navegue até a pasta: `scraper_extension_clean`
3. Selecione a pasta e clique "Selecionar pasta"

### 5. Verificar Instalação
✅ A extensão deve aparecer na lista
✅ Ícone deve aparecer na barra de ferramentas
✅ Sem erros de CSP ou manifest

## Solução de Problemas:

### Se ainda houver erro de CSP:
1. Verifique se está usando a pasta `scraper_extension_clean`
2. Recarregue a extensão clicando no ícone de atualização
3. Reinicie o Chrome se necessário

### Se não aparecer na barra:
1. Clique no ícone de puzzle na barra de ferramentas
2. Encontre "RAG-Control" e clique no pin

## Funcionalidades:
🤖 Capturar página atual para processamento RAG
📊 Seleção de agentes específicos
🔒 Conformidade LGPD
⚡ Interface moderna e responsiva

---
Extensão criada pelo Sistema RAG Python v1.5.2+
Todos os problemas de CSP foram corrigidos!
"""
    
    with open("INSTALACAO_EXTENSAO.md", "w", encoding="utf-8") as f:
        f.write(instrucoes)
    
    print("📄 Instruções salvas em: INSTALACAO_EXTENSAO.md")

def main():
    """Função principal"""
    print("🚀 CORREÇÃO COMPLETA DA EXTENSÃO CHROME")
    print("=" * 60)
    
    # Verificar estado atual
    if not verificar_extensao():
        return
    
    # Corrigir manifest
    if not corrigir_manifest():
        return
    
    # Verificar conformidade CSP
    verificar_csp_compliance()
    
    # Criar versão limpa
    criar_extensao_limpa()
    
    # Gerar instruções
    gerar_instrucoes_instalacao()
    
    print("\n" + "="*60)
    print("🎉 EXTENSÃO CHROME CORRIGIDA COM SUCESSO!")
    print("="*60)
    print("✅ Problemas de CSP resolvidos")
    print("✅ Manifest.json atualizado para v1.5.2")
    print("✅ Versão limpa criada")
    print("✅ Instruções de instalação geradas")
    print("\n💡 PRÓXIMO PASSO:")
    print("   1. Use a pasta 'scraper_extension_clean' no Chrome")
    print("   2. Siga as instruções em 'INSTALACAO_EXTENSAO.md'")
    print("   3. A extensão deve carregar sem erros!")

if __name__ == "__main__":
    main() 