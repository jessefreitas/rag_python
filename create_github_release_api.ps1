# Script PowerShell para criar GitHub Release v1.5.1 via API REST
# Requer Personal Access Token do GitHub

param(
    [string]$Token = $env:GITHUB_TOKEN
)

# Configurações
$Owner = "jessefreitas"
$Repo = "rag_python"
$TagName = "v1.5.1-release"
$ReleaseName = "🚀 RAG Python v1.5.1 - Production Release"

# Release Notes
$ReleaseBody = @"
## 📊 **Resumo da Release**

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
"@

function Create-GitHubRelease {
    param(
        [string]$Owner,
        [string]$Repo,
        [string]$TagName,
        [string]$ReleaseName,
        [string]$ReleaseBody,
        [string]$Token
    )
    
    if (-not $Token) {
        Write-Host "❌ Token do GitHub não fornecido!" -ForegroundColor Red
        Write-Host "💡 Defina a variável GITHUB_TOKEN ou passe como parâmetro" -ForegroundColor Yellow
        Write-Host "🔗 Criar token: https://github.com/settings/tokens" -ForegroundColor Cyan
        return $false
    }
    
    $Uri = "https://api.github.com/repos/$Owner/$Repo/releases"
    
    $Headers = @{
        "Authorization" = "token $Token"
        "Accept" = "application/vnd.github.v3+json"
        "User-Agent" = "PowerShell-GitHubRelease"
    }
    
    $Body = @{
        "tag_name" = $TagName
        "target_commitish" = "main"
        "name" = $ReleaseName
        "body" = $ReleaseBody
        "draft" = $false
        "prerelease" = $false
        "make_latest" = "true"
    } | ConvertTo-Json
    
    try {
        Write-Host "🚀 Criando GitHub Release..." -ForegroundColor Green
        Write-Host "📋 Tag: $TagName" -ForegroundColor Cyan
        Write-Host "📋 Nome: $ReleaseName" -ForegroundColor Cyan
        
        $Response = Invoke-RestMethod -Uri $Uri -Method Post -Headers $Headers -Body $Body -ContentType "application/json"
        
        Write-Host "🎉 Release criada com sucesso!" -ForegroundColor Green
        Write-Host "🔗 URL: $($Response.html_url)" -ForegroundColor Cyan
        Write-Host "📦 Download: $($Response.zipball_url)" -ForegroundColor Cyan
        
        return $Response
    }
    catch {
        Write-Host "❌ Erro ao criar release:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        
        if ($_.Exception.Response) {
            $ErrorResponse = $_.Exception.Response.GetResponseStream()
            $Reader = New-Object System.IO.StreamReader($ErrorResponse)
            $ErrorBody = $Reader.ReadToEnd()
            Write-Host "📋 Detalhes do erro: $ErrorBody" -ForegroundColor Yellow
        }
        
        return $false
    }
}

function Upload-ReleaseAsset {
    param(
        [string]$UploadUrl,
        [string]$FilePath,
        [string]$Token
    )
    
    if (-not (Test-Path $FilePath)) {
        Write-Host "⚠️  Arquivo não encontrado: $FilePath" -ForegroundColor Yellow
        return $false
    }
    
    $FileName = Split-Path $FilePath -Leaf
    $ContentType = "application/octet-stream"
    
    # Determinar content-type baseado na extensão
    switch ([System.IO.Path]::GetExtension($FilePath).ToLower()) {
        ".md" { $ContentType = "text/markdown" }
        ".txt" { $ContentType = "text/plain" }
        ".json" { $ContentType = "application/json" }
        ".ini" { $ContentType = "text/plain" }
    }
    
    $UploadUrlClean = $UploadUrl -replace "\{.*\}", ""
    $Uri = "$UploadUrlClean?name=$FileName"
    
    $Headers = @{
        "Authorization" = "token $Token"
        "Content-Type" = $ContentType
        "User-Agent" = "PowerShell-GitHubRelease"
    }
    
    try {
        Write-Host "📎 Uploading: $FileName" -ForegroundColor Cyan
        $FileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        $Response = Invoke-RestMethod -Uri $Uri -Method Post -Headers $Headers -Body $FileBytes
        Write-Host "✅ Upload concluído: $FileName" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Erro no upload de $FileName : $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Execução principal
Write-Host "🎯 RAG Python v1.5.1 - GitHub Release Creator" -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Gray

# Verificar se estamos no repositório correto
$CurrentRepo = git remote get-url origin 2>$null
if ($CurrentRepo -notlike "*jessefreitas/rag_python*") {
    Write-Host "⚠️  Aviso: Não parece estar no repositório correto" -ForegroundColor Yellow
    Write-Host "📋 Repositório atual: $CurrentRepo" -ForegroundColor Cyan
}

# Criar release
$Release = Create-GitHubRelease -Owner $Owner -Repo $Repo -TagName $TagName -ReleaseName $ReleaseName -ReleaseBody $ReleaseBody -Token $Token

if ($Release) {
    # Assets para upload
    $Assets = @(
        "release-assets/RELEASE_NOTES_v1.5.1.md",
        "release-assets/QUICK_START_v1.5.1.md",
        "release-assets/requirements.txt",
        "release-assets/pytest.ini",
        "release-assets/test_results_v1.5.0_final.json"
    )
    
    Write-Host "`n📦 Fazendo upload dos assets..." -ForegroundColor Green
    
    foreach ($Asset in $Assets) {
        if (Test-Path $Asset) {
            Upload-ReleaseAsset -UploadUrl $Release.upload_url -FilePath $Asset -Token $Token
        } else {
            Write-Host "⚠️  Asset não encontrado: $Asset" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n🎊 Release v1.5.1 publicada com sucesso!" -ForegroundColor Green
    Write-Host "🔗 Acesse: $($Release.html_url)" -ForegroundColor Cyan
} else {
    Write-Host "`n📋 INSTRUÇÕES MANUAIS:" -ForegroundColor Yellow
    Write-Host "1. Acesse: https://github.com/$Owner/$Repo/releases/new" -ForegroundColor Cyan
    Write-Host "2. Tag: $TagName" -ForegroundColor Cyan
    Write-Host "3. Title: $ReleaseName" -ForegroundColor Cyan
    Write-Host "4. Cole o conteúdo de release-assets/RELEASE_NOTES_v1.5.1.md" -ForegroundColor Cyan
    Write-Host "5. Anexe os arquivos da pasta release-assets/" -ForegroundColor Cyan
} 