"""
Painel de Concursos - Aplicação Web Completa em Python, Streamlit e SQLite
Sistema inteligente de monitoramento, alertas e gerenciamento de concursos públicos.
"""
import streamlit as st
import logging
from datetime import datetime, date

# Configuração da página - DEVE ser o primeiro comando Streamlit
st.set_page_config(
    page_title="Painel de Concursos",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("PainelConcursos")

# Importações dos módulos internos
from database.connection import init_db
from database.repository import ConcursoRepository, AlertaRepository, ConfiguracaoRepository
from scrapers.coordinator import ScraperCoordinator
from services.alert_service import AlertService
from services.scheduler_service import SchedulerService
from ui.styles import CUSTOM_CSS
from ui.views import (
    render_dashboard_view,
    render_concursos_view,
    render_alertas_view,
    render_favoritos_view,
    render_estatisticas_view,
    render_calendario_view,
    render_config_view,
    render_about_view
)

def inicializar_sistema():
    """Garante a inicialização do banco, dados semente e robô agendado."""
    if "sistema_inicializado" not in st.session_state:
        # 1. Cria tabelas e índices no SQLite se não existirem
        init_db()

        # 2. Se banco estiver vazio, carrega base semente realista de concursos
        stats = ConcursoRepository.obter_estatisticas_gerais()
        if stats.get("total_concursos", 0) == 0:
            logger.info("Banco inicializado vazio. Carregando dados iniciais...")
            coord = ScraperCoordinator()
            coord.inicializar_dados_semente()
            AlertService.reavaliar_todos_alertas()

        # 3. Inicializa o agendador em background se configurado
        auto = ConfiguracaoRepository.obter("atualizacao_automatica", "true") == "true"
        if auto and not SchedulerService.esta_ativo():
            intervalo = int(ConfiguracaoRepository.obter("intervalo_horas", "6"))
            SchedulerService.iniciar(intervalo_horas=intervalo)

        st.session_state["sistema_inicializado"] = True

def formatar_data_atualizacao(texto_scraping: str) -> str:
    """Retorna data de última atualização amigável e dinâmica."""
    if texto_scraping and texto_scraping.strip():
        return texto_scraping
    return datetime.now().strftime("%d/%m/%Y às %H:%M")

def main():
    """Função principal de orquestração da interface."""
    # Injeta estilos CSS profissionais inspirados em SaaS modernos
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Inicialização do banco e serviços
    inicializar_sistema()

    # Contagem de alertas não lidos para o badge no menu
    alertas_nao_lidos = len(AlertaRepository.listar_alertas(apenas_nao_lidos=True))
    badge_alertas = f"  ({alertas_nao_lidos})" if alertas_nao_lidos > 0 else ""

    # Recupera última atualização para o rodapé da sidebar
    ultimo_scraping = ConfiguracaoRepository.obter("ultimo_scraping", "")
    data_atualizacao_str = formatar_data_atualizacao(ultimo_scraping)

    # -------------------------------------------------------------
    # SIDEBAR MODERNA (ESTILO SAAS / LINEAR / NOTION)
    # -------------------------------------------------------------
    with st.sidebar:
        # 1. CABEÇALHO DA SIDEBAR
        st.markdown("""
        <div class="sidebar-brand-container">
            <div class="sidebar-brand-header">
                <div class="sidebar-brand-icon">
                    🏛️
                </div>
                <div>
                    <div class="sidebar-brand-title">Painel de Concursos</div>
                    <div class="sidebar-brand-subtitle">Sistema Inteligente de Monitoramento de Concursos Públicos</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="nav-section-label">MENU PRINCIPAL</div>', unsafe_allow_html=True)

        # 2. MENU PRINCIPAL COM ÍCONES E DESTAQUE ATIVO
        opcoes_menu = [
            "🏠 Dashboard",
            "📋 Concursos",
            "⭐ Favoritos",
            f"🔔 Alertas{badge_alertas}",
            "📅 Calendário",
            "📈 Estatísticas",
            "⚙️ Configurações",
            "ℹ️ Recursos Extras"
        ]

        pagina_selecionada = st.radio(
            label="Navegação Principal",
            options=opcoes_menu,
            index=0,
            label_visibility="collapsed"
        )

        # 3. RODAPÉ DA SIDEBAR COM STATUS ONLINE DINÂMICO
        st.markdown(f"""
        <div class="sidebar-footer-card">
            <div class="footer-status-row">
                <span class="status-badge-online">
                    <span class="pulsing-dot"></span>
                    Online
                </span>
                <span class="footer-version">v1.0.0</span>
            </div>
            <div class="footer-divider"></div>
            <div class="footer-update-text">
                <div><strong>Status do Sistema:</strong> Online</div>
                <div style="margin-top: 3px;"><strong>Última atualização:</strong> {data_atualizacao_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # ROTEAMENTO MODULAR DE TELAS
    # -------------------------------------------------------------
    if pagina_selecionada.startswith("🏠 Dashboard"):
        render_dashboard_view()
    elif pagina_selecionada.startswith("📋 Concursos"):
        render_concursos_view()
    elif pagina_selecionada.startswith("⭐ Favoritos"):
        render_favoritos_view()
    elif pagina_selecionada.startswith("🔔 Alertas"):
        render_alertas_view()
    elif pagina_selecionada.startswith("📅 Calendário"):
        render_calendario_view()
    elif pagina_selecionada.startswith("📈 Estatísticas"):
        render_estatisticas_view()
    elif pagina_selecionada.startswith("⚙️ Configurações"):
        render_config_view()
    elif pagina_selecionada.startswith("ℹ️ Recursos Extras") or pagina_selecionada.startswith("ℹ️ About"):
        render_about_view()

if __name__ == "__main__":
    main()
