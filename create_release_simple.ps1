# Script simples para criar GitHub Release v1.5.1
param([string]$Token = $env:GITHUB_TOKEN)

$Owner = "jessefreitas"
$Repo = "rag_python"
$TagName = "v1.5.1-release"
$ReleaseName = "🚀 RAG Python v1.5.1 - Production Release"

$ReleaseBody = "## 📊 **Resumo da Release**

Esta é uma **release de produção** com sistema completamente testado e validado. O RAG Python v1.5.1 representa um marco significativo com **100% dos testes passando** e pipeline CI/CD profissional implementado.

## ✨ **Principais Novidades**

### 🤖 **CrewAI Orchestration**
- **4 pipelines especializados** para workflows jurídicos
- **Orquestração inteligente** de agentes especializados
- **Execução paralela** e assíncrona de workflows

### 📄 **Sistema de Geração de Documentos**
- **Templates jurídicos** dinâmicos com Jinja2
- **Conversão automática** para PDF (Windows/Linux)
- **Integração com IA** para melhoramento de documentos

### 🔒 **Compliance LGPD Avançado**
- **Privacy by Design** nativo
- **4 níveis de proteção** de dados
- **Detecção automática** de PII

### 🧪 **Pipeline CI/CD Profissional**
- **GitHub Actions** com 8 jobs especializados
- **Multi-Python testing** (3.10, 3.11, 3.12)
- **Security scanning** (Bandit, Safety)

## 📋 **Resultados dos Testes**
- **Total:** 33 testes
- **Passed:** 33 ✅
- **Failed:** 0 ❌
- **Success Rate:** 100%

## 🚀 **Instalação Rápida**
git clone https://github.com/jessefreitas/rag_python.git
cd rag_python
git checkout v1.5.1-release
pip install -r requirements.txt
pytest

**Esta release está pronta para uso em produção!** 🚀"

if (-not $Token) {
    Write-Host "❌ Token não fornecido!" -ForegroundColor Red
    Write-Host "🔗 Criar token: https://github.com/settings/tokens" -ForegroundColor Cyan
    exit 1
}

Write-Host "🎯 RAG Python v1.5.1 - GitHub Release Creator" -ForegroundColor Magenta
Write-Host "🚀 Criando release..." -ForegroundColor Green

$Uri = "https://api.github.com/repos/$Owner/$Repo/releases"
$Headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
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
    $Response = Invoke-RestMethod -Uri $Uri -Method Post -Headers $Headers -Body $Body -ContentType "application/json"
    Write-Host "🎉 Release criada com sucesso!" -ForegroundColor Green
    Write-Host "🔗 URL: $($Response.html_url)" -ForegroundColor Cyan
    Write-Host "📦 Download: $($Response.zipball_url)" -ForegroundColor Cyan
}
catch {
    Write-Host "❌ Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "📋 Criação manual:" -ForegroundColor Yellow
    Write-Host "https://github.com/$Owner/$Repo/releases/new" -ForegroundColor Cyan
} 