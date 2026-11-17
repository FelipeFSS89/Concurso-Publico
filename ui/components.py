"""
Componentes Reutilizáveis de Interface para Streamlit
"""
import streamlit as st
from datetime import datetime, date
from typing import Dict, Any, Optional
from config import STATUS_CONFIG

def formatar_data_br(data_iso: Optional[str]) -> str:
    """Converte 'YYYY-MM-DD' para 'DD/MM/AAAA'."""
    if not data_iso:
        return "Não informada"
    try:
        dt = datetime.strptime(str(data_iso)[:10], "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return str(data_iso)

def calcular_dias_restantes(data_iso: Optional[str]) -> Optional[int]:
    """Calcula a diferença em dias entre a data e hoje."""
    if not data_iso:
        return None
    try:
        dt = datetime.strptime(str(data_iso)[:10], "%Y-%m-%d").date()
        return (dt - date.today()).days
    except ValueError:
        return None

def render_header(titulo: str, subtitulo: str):
    """Renderiza cabeçalho estilizado no topo da página."""
    html = f"""
    <div class="app-header">
        <h1>🏛️ {titulo}</h1>
        <p>{subtitulo}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_kpi_cards(stats: Dict[str, Any]):
    """Renderiza a grade de KPIs principais do Dashboard."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div>
                <div class="kpi-title">Total Encontrados</div>
                <div class="kpi-value">{stats.get('total_concursos', 0)}</div>
            </div>
            <div class="kpi-sub">📡 Portais monitorados</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #3B82F6;">
            <div>
                <div class="kpi-title">Monitorados</div>
                <div class="kpi-value" style="color: #2563EB;">{stats.get('total_monitorados', 0)}</div>
            </div>
            <div class="kpi-sub">👁️ No seu radar</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #F59E0B;">
            <div>
                <div class="kpi-title">Favoritos</div>
                <div class="kpi-value" style="color: #D97706;">{stats.get('total_favoritos', 0)}</div>
            </div>
            <div class="kpi-sub">⭐ Prioridade alta</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #10B981;">
            <div>
                <div class="kpi-title">Inscrições Feitas</div>
                <div class="kpi-value" style="color: #059669;">{stats.get('total_inscricoes', 0)}</div>
            </div>
            <div class="kpi-sub">📝 Inscrito / Taxa paga</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #8B5CF6;">
            <div>
                <div class="kpi-title">Em Estudo Ativo</div>
                <div class="kpi-value" style="color: #7C3AED;">{stats.get('total_estudo', 0)}</div>
            </div>
            <div class="kpi-sub">📚 Foco no edital</div>
        </div>
        """, unsafe_allow_html=True)

def render_alert_box(tipo: str, titulo: str, mensagem: str, data_referencia: Optional[str] = None):
    """Renderiza card de alerta com bordas e cores semânticas."""
    tipo_css = tipo.lower() if tipo in ["urgente", "atencao", "novidade", "info"] else "info"
    
    icones = {
        "urgente": "🚨",
        "atencao": "⚠️",
        "novidade": "✨",
        "info": "ℹ️"
    }
    icone = icones.get(tipo_css, "ℹ️")
    data_html = f"<span style='float: right; font-size: 0.75rem; opacity: 0.8;'>{formatar_data_br(data_referencia)}</span>" if data_referencia else ""

    html = f"""
    <div class="alert-box {tipo_css}">
        <span style="font-size: 1.25rem; line-height: 1;">{icone}</span>
        <div style="flex-grow: 1;">
            {data_html}
            <div><strong>{titulo}</strong></div>
            <div style="margin-top: 0.25rem;">{mensagem}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_status_badge(status: str) -> str:
    """Retorna tag HTML de badge colorida correspondente ao status do usuário."""
    cfg = STATUS_CONFIG.get(status, {"color": "#64748B"})
    cor = cfg["color"]
    return f"""<span style="background-color: {cor}20; color: {cor}; border: 1px solid {cor}50; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 0.75rem;">{status}</span>"""
