"""
Tela Sobre o Projeto (About) - Painel de Concursos
Apresenta informações do projeto, desenvolvedor, tecnologias e roadmap futuro.
"""
import streamlit as st
from ui.components import render_header

def render_about_view():
    """Renderiza a página profissional 'Sobre o Projeto'."""
    render_header(
        "Sobre o Projeto",
        "Conheça a visão, arquitetura, desenvolvedor e objetivos futuros do Painel de Concursos."
    )

    # -------------------------------------------------------------
    # 1. CARD PRINCIPAL: VISÃO GERAL DA PLATAFORMA
    # -------------------------------------------------------------
    st.markdown("""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 2rem; margin-bottom: 1.75rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);">
                🏛️
            </div>
            <div>
                <h2 style="margin: 0; font-size: 1.4rem; font-weight: 800; color: #0F172A;">Painel de Concursos</h2>
                <span style="font-size: 0.85rem; color: #64748B; font-weight: 600;">Plataforma Inteligente de Gestão de Concursos Públicos</span>
            </div>
        </div>
        <p style="font-size: 1.05rem; line-height: 1.7; color: #334155; margin: 0;">
            O <strong>Painel de Concursos</strong> é uma plataforma desenvolvida para auxiliar candidatos a concursos públicos no acompanhamento de oportunidades, organização de inscrições, gerenciamento de estudos e monitoramento de prazos importantes.
        </p>
        <p style="font-size: 1.05rem; line-height: 1.7; color: #334155; margin-top: 0.75rem; margin-bottom: 0;">
            O sistema centraliza informações de concursos, alertas, favoritos, observações e histórico de acompanhamento em um único ambiente.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 2. SEÇÃO CRIADOR DO PROJETO & DESENVOLVEDOR
    # -------------------------------------------------------------
    col_dev, col_tech = st.columns([1, 1])

    with col_dev:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border-radius: 16px; padding: 2rem; color: white; height: 100%; box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.2); border-left: 6px solid #6366F1;">
            <div style="text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.1em; color: #818CF8; font-weight: 700; margin-bottom: 0.5rem;">
                Criador do Projeto
            </div>
            <div style="font-size: 1.75rem; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 0.5rem;">
                <span>Felipe Sousa</span>
                <span style="font-size: 1.1rem; color: #38BDF8;" title="Desenvolvedor Verificado">✓</span>
            </div>
            <p style="color: #94A3B8; font-size: 0.95rem; margin-top: 0.5rem; line-height: 1.5;">
                Idealizador e arquiteto de software do Painel de Concursos.
            </p>
            <div style="margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 600;">PROJETO</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.75rem;">Painel de Concursos</div>
                
                <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 600;">DESENVOLVEDOR</div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC;">Felipe Sousa</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_tech:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 2rem; height: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.08em; color: #64748B; font-weight: 700; margin-bottom: 0.5rem;">
                Stack de Engenharia
            </div>
            <h3 style="margin: 0 0 1rem 0; font-size: 1.3rem; font-weight: 800; color: #0F172A;">
                Tecnologias Utilizadas
            </h3>
            <p style="color: #64748B; font-size: 0.92rem; margin-bottom: 1.25rem;">
                Construído com tecnologias modernas, eficientes e escaláveis para garantir velocidade e estabilidade.
            </p>
            <div style="display: flex; flex-wrap: wrap; gap: 0.6rem;">
                <span style="background: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.88rem;">🐍 Python 3.12+</span>
                <span style="background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.88rem;">👑 Streamlit</span>
                <span style="background: #F0FDF4; color: #16A34A; border: 1px solid #BBF7D0; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.88rem;">🗄️ SQLite</span>
                <span style="background: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.88rem;">🐼 Pandas</span>
                <span style="background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.88rem;">🍲 BeautifulSoup</span>
                <span style="background: #FAF5FF; color: #9333EA; border: 1px solid #E9D5FF; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.88rem;">📊 Plotly</span>
            </div>
            <div style="margin-top: 1.5rem; font-size: 0.85rem; color: #64748B; line-height: 1.5;">
                • Persistência em modo <strong>WAL (Write-Ahead Logging)</strong> com índices otimizados.<br>
                • Scrapers resilientes com normalização regex e tratamento de falhas.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 3. SEÇÃO OBJETIVOS FUTUROS (ROADMAP)
    # -------------------------------------------------------------
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <span style="text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.08em; color: #3B82F6; font-weight: 700;">Evolução Contínua</span>
        <h3 style="margin: 0.25rem 0 0.5rem 0; font-size: 1.35rem; font-weight: 800; color: #0F172A;">Objetivos Futuros</h3>
        <p style="color: #64748B; font-size: 0.95rem; margin: 0;">Próximas funcionalidades e integrações planejadas para as próximas versões da plataforma.</p>
    </div>
    """, unsafe_allow_html=True)

    col_r1, col_r2, col_r3 = st.columns(3)

    with col_r1:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">✈️</div>
            <div style="font-weight: 700; color: #1E293B; font-size: 1rem; margin-bottom: 0.35rem;">Integração com Telegram</div>
            <p style="color: #64748B; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                Envio automático de alertas de editais e lembretes de provas diretamente no canal ou bot privado do usuário.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_r2:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💬</div>
            <div style="font-weight: 700; color: #1E293B; font-size: 1rem; margin-bottom: 0.35rem;">Integração com WhatsApp</div>
            <p style="color: #64748B; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                Notificações instantâneas de prazos de inscrição, pagamento de taxa e novas retificações de editais via WhatsApp.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_r3:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">✉️</div>
            <div style="font-weight: 700; color: #1E293B; font-size: 1rem; margin-bottom: 0.35rem;">Integração com E-mail</div>
            <p style="color: #64748B; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                Boletim semanal consolidado com oportunidades compatíveis com a formação cadastrada e resumo dos certames favoritados.
            </p>
        </div>
        """, unsafe_allow_html=True)

    col_r4, col_r5, col_r6 = st.columns(3)

    with col_r4:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📱</div>
            <div style="font-weight: 700; color: #1E293B; font-size: 1rem; margin-bottom: 0.35rem;">Aplicativo Mobile</div>
            <p style="color: #64748B; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                Versão mobile progressiva (PWA) e aplicativo nativo com notificações push em tempo real na palma da mão.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_r5:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📈</div>
            <div style="font-weight: 700; color: #1E293B; font-size: 1rem; margin-bottom: 0.35rem;">Dashboard Avançado</div>
            <p style="color: #64748B; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                Análise preditiva de concorrência por vaga, histórico de bancas e estimativa de pontuação de corte.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_r6:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">☁️</div>
            <div style="font-weight: 700; color: #1E293B; font-size: 1rem; margin-bottom: 0.35rem;">Sincronização em Nuvem</div>
            <p style="color: #64748B; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                Backup automatizado e sincronização de anotações, favoritos e histórico de status entre múltiplos dispositivos.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 2.5rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 4. RODAPÉ DA PÁGINA ABOUT
    # -------------------------------------------------------------
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem; border-top: 1px solid #E2E8F0; color: #64748B; font-size: 0.9rem;">
        <div style="font-weight: 600; color: #334155;">
            © 2026 - Desenvolvido por <strong>Felipe Sousa</strong>
        </div>
        <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.25rem;">
            Todos os direitos reservados.
        </div>
    </div>
    """, unsafe_allow_html=True)
