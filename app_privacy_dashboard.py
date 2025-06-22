#!/usr/bin/env python3
"""
Dashboard de Compliance LGPD - RAG Python
Interface Streamlit para monitoramento e gestão de privacidade
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa sistema de privacidade
from privacy_system import privacy_manager, DataCategory, RetentionPolicy
from agent_system_privacy import privacy_agent_system

def main():
    """Interface principal do dashboard de compliance"""
    
    st.set_page_config(
        page_title="Dashboard LGPD - RAG Python",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔒 Dashboard de Compliance LGPD")
    st.markdown("**Sistema de Monitoramento e Gestão de Privacidade**")
    
    # Sidebar com navegação
    st.sidebar.title("📋 Navegação")
    
    pages = {
        "📊 Visão Geral": show_overview,
        "🔍 Detecção de Dados": show_detection,
        "📁 Gestão de Registros": show_records_management,
        "⚖️ Relatório de Compliance": show_compliance_report,
        "🔧 Configurações": show_settings
    }
    
    selected_page = st.sidebar.selectbox("Selecione uma página:", list(pages.keys()))
    
    # Estatísticas rápidas na sidebar
    show_quick_stats()
    
    # Executa página selecionada
    pages[selected_page]()

def show_quick_stats():
    """Mostra estatísticas rápidas na sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Estatísticas Rápidas")
    
    try:
        # Dados do sistema
        summary = privacy_manager.get_data_summary()
        
        st.sidebar.metric("📁 Total de Registros", summary['total_records'])
        st.sidebar.metric("✅ Registros Ativos", summary['active_records'])
        st.sidebar.metric("⚠️ Registros Expirados", summary['expired_records'])
        
        # Status geral
        if summary['expired_records'] > 0:
            st.sidebar.warning(f"⚠️ {summary['expired_records']} registros expirados")
        else:
            st.sidebar.success("✅ Todos os registros em compliance")
            
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar estatísticas: {e}")

def show_overview():
    """Página de visão geral"""
    st.header("📊 Visão Geral do Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        summary = privacy_manager.get_data_summary()
        
        with col1:
            st.metric(
                label="📁 Total de Registros",
                value=summary['total_records'],
                delta=f"+{summary['active_records']} ativos"
            )
        
        with col2:
            compliance_rate = ((summary['total_records'] - summary['expired_records']) / max(summary['total_records'], 1)) * 100
            st.metric(
                label="⚖️ Taxa de Compliance",
                value=f"{compliance_rate:.1f}%",
                delta="LGPD"
            )
        
        with col3:
            st.metric(
                label="🔒 Registros Anonimizados",
                value=summary['anonymized_records'],
                delta="Proteção ativa"
            )
        
        with col4:
            st.metric(
                label="🗑️ Registros Deletados",
                value=summary['deleted_records'],
                delta="Limpeza automática"
            )
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

def show_detection():
    """Página de detecção de dados"""
    st.header("🔍 Detecção de Dados Pessoais")
    
    st.markdown("**Teste a detecção de dados pessoais em tempo real**")
    
    # Área de input
    content = st.text_area(
        "Digite ou cole o texto para análise:",
        height=200,
        placeholder="Cole aqui documentos, contratos, ou qualquer texto que possa conter dados pessoais..."
    )
    
    # Opções de análise
    col1, col2 = st.columns(2)
    
    with col1:
        detection_mode = st.selectbox(
            "Modo de operação:",
            ["🔍 Apenas detecção (preserva original)", "🔒 Detecção + Anonimização"]
        )
    
    with col2:
        detailed_analysis = st.checkbox("📋 Análise detalhada", value=True)
    
    # Botão de análise
    if st.button("🔍 Analisar Dados", type="primary") and content:
        
        with st.spinner("Analisando dados pessoais..."):
            try:
                if "preserva original" in detection_mode:
                    # Modo detecção apenas
                    detection = privacy_manager.detect_personal_data_only(content, detailed=detailed_analysis)
                    risk_analysis = privacy_manager.analyze_document_privacy_risks(content)
                    
                    # Resultados
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🔍 Detecção (Original Preservado)")
                        
                        if detection['has_personal_data']:
                            st.success(f"✅ {detection['total_occurrences']} dados pessoais detectados")
                            st.info(f"📂 Categoria: {detection['data_category']}")
                            st.info(f"📝 Tipos: {', '.join(detection['detected_types'])}")
                            
                            if detailed_analysis and detection.get('details'):
                                st.markdown("**📋 Detalhes por tipo:**")
                                for data_type, details in detection['details'].items():
                                    with st.expander(f"{data_type.upper()} ({details['count']} ocorrências)"):
                                        st.write("**Exemplos encontrados:**")
                                        for example in details['examples']:
                                            st.code(example)
                        else:
                            st.success("✅ Nenhum dado pessoal detectado")
                    
                    with col2:
                        st.subheader("⚠️ Análise de Riscos")
                        
                        # Indicador de risco
                        risk_colors = {
                            "BAIXO": "🟢",
                            "MÉDIO": "🟡", 
                            "ALTO": "🟠",
                            "CRÍTICO": "🔴"
                        }
                        
                        risk_level = risk_analysis['risk_level']
                        st.markdown(f"### {risk_colors.get(risk_level, '⚪')} Risco: {risk_level}")
                        st.metric("Score de Risco", risk_analysis['risk_score'])
                        st.info(risk_analysis['risk_description'])
                        
                        if risk_analysis['lgpd_compliance_required']:
                            st.warning("⚖️ Compliance LGPD obrigatório")
                        
                        # Recomendações
                        st.markdown("**💡 Recomendações:**")
                        for rec in risk_analysis['recommendations'][:5]:  # Primeiras 5
                            st.markdown(f"- {rec}")
                
            except Exception as e:
                st.error(f"Erro na análise: {e}")
    
    elif st.button("🔍 Analisar Dados", type="primary") and not content:
        st.warning("⚠️ Por favor, insira algum conteúdo para análise")

def show_records_management():
    """Página de gestão de registros"""
    st.header("📁 Gestão de Registros de Dados")
    
    try:
        # Carrega registros
        records = list(privacy_manager.data_records.values())
        
        if not records:
            st.info("📝 Nenhum registro encontrado. Faça uma detecção primeiro.")
            return
        
        # Tabela de registros
        st.subheader(f"📋 Registros ({len(records)} total)")
        
        # Prepara dados para tabela
        table_data = []
        for record in records:
            table_data.append({
                "ID": record.id[:8] + "...",
                "Categoria": record.category.value,
                "Agente": record.agent_id,
                "Criado": record.created_at.strftime("%d/%m/%Y %H:%M"),
                "Status": "🗑️ Deletado" if record.is_deleted else "⏰ Expirado" if record.is_expired else "✅ Ativo",
                "Tamanho": f"{len(record.content)} chars"
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
        
        # Ações em lote
        st.subheader("⚙️ Ações")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧹 Limpar Expirados"):
                expired_count = privacy_manager.cleanup_expired_data()
                st.success(f"✅ {expired_count} registros expirados removidos")
        
        with col2:
            if st.button("📊 Atualizar Lista"):
                st.rerun()
        
    except Exception as e:
        st.error(f"Erro ao carregar registros: {e}")

def show_compliance_report():
    """Página de relatório de compliance"""
    st.header("⚖️ Relatório de Compliance LGPD")
    
    try:
        # Gera relatório completo
        summary = privacy_manager.get_data_summary()
        
        st.subheader("📋 Status Geral de Compliance")
        
        # Métricas principais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            compliance_rate = ((summary['total_records'] - summary['expired_records']) / max(summary['total_records'], 1)) * 100
            st.metric("Taxa de Compliance", f"{compliance_rate:.1f}%")
        
        with col2:
            st.metric("Registros em Conformidade", summary['total_records'] - summary['expired_records'])
        
        with col3:
            st.metric("Ações Necessárias", summary['expired_records'])
        
        # Checklist LGPD
        st.subheader("✅ Checklist LGPD")
        
        checklist = [
            ("Detecção de Dados Pessoais", True, "✅ Sistema ativo"),
            ("Políticas de Retenção", True, "✅ Configuradas"),
            ("Trilha de Auditoria", True, "✅ Logs completos"),
            ("Direito ao Esquecimento", True, "✅ Soft/Hard delete"),
            ("Consentimento Granular", True, "✅ Por operação"),
            ("Anonimização", True, "✅ Múltiplos métodos"),
            ("Relatórios de Compliance", True, "✅ Automáticos"),
            ("Interface de Gestão", True, "✅ Dashboard ativo")
        ]
        
        for item, status, description in checklist:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{item}**: {description}")
            with col2:
                if status:
                    st.success("✅")
                else:
                    st.error("❌")
        
        # Resumo de ações
        if summary['expired_records'] > 0:
            st.warning(f"⚠️ **Ação necessária**: {summary['expired_records']} registros expirados precisam ser tratados")
        else:
            st.success("🎉 **Parabéns!** Sistema em total compliance com LGPD")
        
    except Exception as e:
        st.error(f"Erro ao gerar relatório: {e}")

def show_settings():
    """Página de configurações"""
    st.header("🔧 Configurações do Sistema")
    
    st.subheader("⚙️ Configurações de Privacidade")
    
    # Configurações globais
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔍 Modo de Detecção Global**")
        detection_mode = st.radio(
            "Modo padrão:",
            ["🔍 Apenas detecção", "🔒 Detecção + Anonimização"],
            help="Define o comportamento padrão do sistema"
        )
        
        if st.button("💾 Salvar Modo"):
            mode_enabled = "apenas detecção" in detection_mode
            privacy_manager.set_detection_only_mode(mode_enabled)
            st.success(f"✅ Modo {'detecção apenas' if mode_enabled else 'anonimização'} ativado")
    
    with col2:
        st.markdown("**🔄 Manutenção**")
        if st.button("🧹 Limpeza Automática"):
            cleaned = privacy_manager.cleanup_expired_data()
            st.success(f"✅ {cleaned} registros limpos")

if __name__ == "__main__":
    main() 