#!/usr/bin/env python3
import os
import sys
import time
import psutil
import subprocess

def kill_processes_on_port(port):
    """Mata processos rodando em uma porta específica"""
    try:
        killed_count = 0
        for proc in psutil.process_iter(["pid", "name", "connections"]):
            try:
                connections = proc.info["connections"]
                if connections:
                    for conn in connections:
                        if hasattr(conn, "laddr") and conn.laddr and conn.laddr.port == port:
                            print(f"   Matando processo {proc.info[\"name\"]} (PID: {proc.info[\"pid\"]}) na porta {port}")
                            proc.kill()
                            killed_count += 1
                            break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if killed_count > 0:
            print(f"   {killed_count} processo(s) encerrado(s) na porta {port}")
        else:
            print(f"   Porta {port} livre")
        return True
    except Exception as e:
        print(f"   Erro ao verificar porta {port}: {e}")
        return False

def main():
    print("=" * 70)
    print(" RAG PYTHON v1.5.1 - INICIALIZADOR RÁPIDO")
    print("=" * 70)
    
    # Limpar portas
    print(" LIMPANDO PORTAS...")
    for port in [8501, 5000, 5001, 5002]:
        kill_processes_on_port(port)
    
    print("\n ESCOLHA O SERVIDOR:")
    print("1.  STREAMLIT - Interface principal (porta 8501)")
    print("2.  API FLASK - API para extensão (porta 5000)")
    print("3.  API SUPABASE - API com Supabase (porta 5002)")
    print("4.  INICIALIZADOR - Script robusto")
    
    choice = input("\nDigite sua escolha (1-4): ").strip()
    
    if choice == "1":
        print("\n Iniciando Streamlit...")
        subprocess.run(["python", "app_completo_unificado.py"])
    elif choice == "2":
        print("\n Iniciando API Flask...")
        subprocess.run(["python", "api_server_simple.py"])
    elif choice == "3":
        print("\n Iniciando API Supabase...")
        subprocess.run(["python", "api_server_supabase.py"])
    elif choice == "4":
        print("\n Iniciando com script robusto...")
        subprocess.run(["python", "iniciar_servidor_rag.py"])
    else:
        print(" Opção inválida")

if __name__ == "__main__":
    main()

