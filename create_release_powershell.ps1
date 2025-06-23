# Script PowerShell para criar GitHub Release v1.5.1 com assets
param(
    [string]$GitHubToken = $env:GITHUB_TOKEN
)

$Owner = "jessefreitas"
$Repo = "rag_python"
$TagName = "v1.5.1-release"
$ReleaseName = "🚀 RAG Python v1.5.1 - Production Release"

Write-Host "🎯 RAG Python v1.5.1 - GitHub Release Creator" -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Gray

# Ler release notes
try {
    $ReleaseBody = Get-Content -Path "release-assets/RELEASE_NOTES_v1.5.1.md" -Raw -Encoding UTF8
    Write-Host "✅ Release notes carregadas" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao ler release notes: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Função para criar release
function Create-GitHubRelease {
    $Uri = "https://api.github.com/repos/$Owner/$Repo/releases"
    
    $Headers = @{
        "Accept" = "application/vnd.github.v3+json"
        "User-Agent" = "PowerShell-RAG-Release"
        "Content-Type" = "application/json"
    }
    
    $Body = @{
        "tag_name" = $TagName
        "target_commitish" = "main"
        "name" = $ReleaseName
        "body" = $ReleaseBody
        "draft" = $false
        "prerelease" = $false
    } | ConvertTo-Json -Depth 10
    
    try {
        Write-Host "🚀 Criando release..." -ForegroundColor Green
        Write-Host "📋 Tag: $TagName" -ForegroundColor Cyan
        Write-Host "📋 Nome: $ReleaseName" -ForegroundColor Cyan
        
        # Tentar criar release (repositório público não precisa de token)
        $Response = Invoke-RestMethod -Uri $Uri -Method Post -Headers $Headers -Body $Body
        
        Write-Host "🎉 Release criada com sucesso!" -ForegroundColor Green
        Write-Host "🔗 URL: $($Response.html_url)" -ForegroundColor Cyan
        Write-Host "📦 ID: $($Response.id)" -ForegroundColor Yellow
        
        return $Response
    }
    catch {
        Write-Host "❌ Erro ao criar release: $($_.Exception.Message)" -ForegroundColor Red
        
        # Tentar método alternativo sem autenticação
        try {
            Write-Host "🔄 Tentando método alternativo..." -ForegroundColor Yellow
            
            # Remover headers de autenticação
            $HeadersAlt = @{
                "Accept" = "application/vnd.github.v3+json"
                "User-Agent" = "PowerShell-RAG-Release"
                "Content-Type" = "application/json"
            }
            
            $ResponseAlt = Invoke-RestMethod -Uri $Uri -Method Post -Headers $HeadersAlt -Body $Body
            
            Write-Host "🎉 Release criada (método alternativo)!" -ForegroundColor Green
            Write-Host "🔗 URL: $($ResponseAlt.html_url)" -ForegroundColor Cyan
            
            return $ResponseAlt
        }
        catch {
            Write-Host "❌ Método alternativo também falhou: $($_.Exception.Message)" -ForegroundColor Red
            return $null
        }
    }
}

# Função para fazer upload de asset
function Upload-Asset {
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
    $UploadUrlClean = $UploadUrl -replace '\{.*\}', "?name=$FileName"
    
    $Headers = @{
        "Accept" = "application/vnd.github.v3+json"
        "User-Agent" = "PowerShell-RAG-Release"
        "Content-Type" = "application/octet-stream"
    }
    
    if ($Token) {
        $Headers["Authorization"] = "token $Token"
    }
    
    try {
        Write-Host "📎 Uploading: $FileName" -ForegroundColor Cyan
        
        $FileBytes = [System.IO.File]::ReadAllBytes($FilePath)
        $Response = Invoke-RestMethod -Uri $UploadUrlClean -Method Post -Headers $Headers -Body $FileBytes
        
        Write-Host "✅ Upload concluído: $FileName" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Erro no upload de $FileName : $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Verificar se release já existe
try {
    $CheckUri = "https://api.github.com/repos/$Owner/$Repo/releases"
    $ExistingReleases = Invoke-RestMethod -Uri $CheckUri
    
    $ExistingRelease = $ExistingReleases | Where-Object { $_.tag_name -eq $TagName }
    
    if ($ExistingRelease) {
        Write-Host "✅ Release já existe!" -ForegroundColor Green
        Write-Host "🔗 URL: $($ExistingRelease.html_url)" -ForegroundColor Cyan
        exit 0
    }
}
catch {
    Write-Host "⚠️  Não foi possível verificar releases existentes" -ForegroundColor Yellow
}

# Criar release
$Release = Create-GitHubRelease

if ($Release) {
    Write-Host "`n📦 Fazendo upload dos assets..." -ForegroundColor Green
    
    # Lista de assets para upload
    $Assets = @(
        "release-assets/QUICK_START_v1.5.1.md",
        "release-assets/requirements.txt",
        "release-assets/pytest.ini",
        "release-assets/test_results_v1.5.0_final.json"
    )
    
    $UploadCount = 0
    foreach ($Asset in $Assets) {
        if (Test-Path $Asset) {
            if (Upload-Asset -UploadUrl $Release.upload_url -FilePath $Asset -Token $GitHubToken) {
                $UploadCount++
            }
        } else {
            Write-Host "⚠️  Asset não encontrado: $Asset" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n🎊 SUCESSO COMPLETO!" -ForegroundColor Green
    Write-Host "📦 Release criada: $($Release.html_url)" -ForegroundColor Cyan
    Write-Host "📎 Assets uploaded: $UploadCount/4" -ForegroundColor Yellow
    Write-Host "`n🚀 RAG Python v1.5.1 está oficialmente publicado!" -ForegroundColor Magenta
    
} else {
    Write-Host "`n📋 INSTRUÇÕES MANUAIS:" -ForegroundColor Yellow
    Write-Host "1. Acesse: https://github.com/$Owner/$Repo/releases/new" -ForegroundColor Cyan
    Write-Host "2. Tag: $TagName" -ForegroundColor Cyan
    Write-Host "3. Title: $ReleaseName" -ForegroundColor Cyan
    Write-Host "4. Cole o conteúdo de release-assets/RELEASE_NOTES_v1.5.1.md" -ForegroundColor Cyan
    Write-Host "5. Anexe os arquivos da pasta release-assets/" -ForegroundColor Cyan
}

# Verificar resultado final
Write-Host "`n🔍 Verificação final..." -ForegroundColor Blue
try {
    $FinalCheck = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo/releases"
    if ($FinalCheck.Count -gt 0) {
        Write-Host "✅ $($FinalCheck.Count) release(s) encontrada(s)" -ForegroundColor Green
        foreach ($rel in $FinalCheck) {
            Write-Host "   📦 $($rel.name) ($($rel.tag_name))" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ Nenhuma release encontrada" -ForegroundColor Red
    }
} catch {
    Write-Host "⚠️  Erro na verificação final" -ForegroundColor Yellow
} 