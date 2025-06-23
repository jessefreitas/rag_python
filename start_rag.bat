@echo off
REM ===================================================================
REM 🚀 RAG PYTHON v1.5.1 - INICIALIZADOR WINDOWS
REM ===================================================================

title RAG Python v1.5.1 - Sistema Unificado

echo.
echo ======================================================================
echo 🚀 RAG PYTHON v1.5.1 - SISTEMA UNIFICADO
echo ======================================================================
echo 🎯 Multi-LLM + Agentes + Privacidade + PostgreSQL
echo 🔧 Inicializacao automatica para Windows
echo ======================================================================
echo.

REM Mudar para o diretório do script
cd /d "%~dp0"

REM Verificar se Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado. Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Verificar se pip está disponível
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip nao encontrado. Verifique a instalacao do Python.
    pause
    exit /b 1
)

echo ✅ pip encontrado
echo.

REM Instalar dependências mínimas se necessário
echo 📦 Verificando dependencias minimas...
if exist requirements_minimal.txt (
    echo 📋 Instalando requirements_minimal.txt...
    python -m pip install -r requirements_minimal.txt --quiet
    if errorlevel 1 (
        echo ⚠️ Falha ao instalar algumas dependencias, continuando...
    ) else (
        echo ✅ Dependencias minimas instaladas
    )
) else (
    echo 📦 Instalando python-dotenv essencial...
    python -m pip install python-dotenv --quiet
)

echo.

REM Executar o inicializador Python
echo 🚀 Executando inicializador robusto...
echo.
python iniciar_servidor_rag.py

REM Se chegou aqui, o servidor foi encerrado
echo.
echo ======================================================================
echo 👋 Servidor RAG encerrado
echo ======================================================================
echo 💡 Para reiniciar, execute novamente: start_rag.bat
echo ======================================================================
pause 