"""
Tela do Dashboard Principal do Painel de Concursos
"""
import streamlit as st
import plotly.express as px
from datetime import date
from database.repository import ConcursoRepository, AlertaRepository, ConfiguracaoRepository
from services.alert_service import AlertService
from scrapers.coordinator import ScraperCoordinator
from ui.components import (
    render_header, 
    render_kpi_cards, 
    render_alert_box, 
    formatar_data_br, 
    calcular_dias_restantes,
    render_status_badge
)

def render_dashboard_view():
    """Renderiza a página principal do Dashboard."""
    
    # Header e barra de ações
    col_t, col_b = st.columns([3, 1])
    with col_t:
        ultimo = ConfiguracaoRepository.obter("ultimo_scraping", "Não realizado")
        render_header(
            "Painel de Concursos",
            f"Monitoramento inteligente em tempo real • Degrau Cultural & Folha QConcursos • Última varredura: {ultimo}"
        )
    with col_b:
        st.write("")
        st.write("")
        if st.button("🔄 Atualizar Concursos Agora", use_container_width=True, type="primary"):
            with st.spinner("Consultando Degrau Cultural e Folha QConcursos..."):
                coordinator = ScraperCoordinator()
                res = coordinator.executar_coleta(incluir_semente_se_vazio=True)
                AlertService.reavaliar_todos_alertas()
                st.success(f"Varredura concluída! {res['novos']} novos e {res['atualizados']} atualizados.")
                st.rerun()

    # 1. Carrega Estatísticas Consolidadas
    stats = ConcursoRepository.obter_estatisticas_gerais()

    # 2. Renderiza KPIs
    render_kpi_cards(stats)

    st.markdown("---")

    # 3. Painel de Alertas Importantes (Urgentes e Atenção)
    st.subheader("🚨 Central de Alertas Críticos")
    alertas_criticos = AlertaRepository.listar_alertas(apenas_nao_lidos=True)
    # Filtra os urgentes e de atenção primeiro
    alertas_destaque = [a for a in alertas_criticos if a["tipo"] in ["urgente", "atencao"]][:4]
    
    if alertas_destaque:
        for a in alertas_destaque:
            render_alert_box(a["tipo"], a["titulo"], a["mensagem"], a.get("data_referencia"))
    else:
        render_alert_box(
            "novidade", 
            "Tudo em dia!", 
            "Não há prazos vencendo nas próximas 48 horas nem provas iminentes sem aviso."
        )

    # 4. Próximos Vencimentos e Próximas Provas
    col_venc, col_prov = st.columns(2)

    with col_venc:
        st.subheader("⏰ Próximos Vencimentos de Inscrição")
        vencimentos = stats.get("proximos_vencimentos", [])
        if vencimentos:
            for v in vencimentos:
                dias = calcular_dias_restantes(v.get("data_inscricao_fim"))
                cor_dias = "#EF4444" if dias is not None and dias <= 3 else "#F59E0B"
                aviso_dias = "Hoje!" if dias == 0 else f"{dias} dias" if dias is not None and dias > 0 else "Encerrado"
                
                st.markdown(f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.85rem; margin-bottom: 0.6rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 700; color: #1E293B;">{v.get('nome')}</div>
                        <div style="font-size: 0.8rem; color: #64748B;">{v.get('orgao')} • {v.get('estado')}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: {cor_dias}15; color: {cor_dias}; font-weight: 800; font-size: 0.85rem; padding: 3px 8px; border-radius: 6px;">
                            {aviso_dias}
                        </span>
                        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">Até {formatar_data_br(v.get('data_inscricao_fim'))}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhuma inscrição com encerramento iminente.")

    with col_prov:
        st.subheader("📝 Próximas Provas Agendadas")
        provas = stats.get("proximas_provas", [])
        if provas:
            for p in provas:
                dias_p = calcular_dias_restantes(p.get("data_prova"))
                aviso_p = f"Em {dias_p} dias" if dias_p is not None and dias_p > 0 else "Hoje!" if dias_p == 0 else "Passou"
                st.markdown(f"""
                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.85rem; margin-bottom: 0.6rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 700; color: #1E293B;">{p.get('nome')}</div>
                        <div style="font-size: 0.8rem; color: #64748B;">Cargo: {p.get('cargo', 'Geral')} • {p.get('estado')}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: #3B82F615; color: #2563EB; font-weight: 800; font-size: 0.85rem; padding: 3px 8px; border-radius: 6px;">
                            {aviso_p}
                        </span>
                        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 2px;">{formatar_data_br(p.get('data_prova'))}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhuma data de prova agendada para os próximos dias.")

    st.markdown("---")

    # 5. Gráficos do Dashboard com Plotly
    st.subheader("📊 Panorama Visual dos Concursos")
    dados_graficos = ConcursoRepository.obter_dados_graficos()
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        status_list = dados_graficos.get("status", [])
        if status_list:
            fig_status = px.pie(
                status_list,
                names="status",
                values="qtd",
                title="Distribuição por Seu Status de Estudo / Inscrição",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_status.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=300)
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("Sem dados de status suficientes para o gráfico.")

    with col_g2:
        uf_list = dados_graficos.get("estados", [])
        if uf_list:
            fig_uf = px.bar(
                uf_list,
                x="estado",
                y="qtd",
                title="Oportunidades por Estado (UF)",
                labels={"estado": "Estado (UF)", "qtd": "Qtd Concursos"},
                color="qtd",
                color_continuous_scale="Blues"
            )
            fig_uf.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=300)
            st.plotly_chart(fig_uf, use_container_width=True)
        else:
            st.info("Sem dados de estados suficientes.")

    # 6. Painel de Próximas Ações Consolidadas
    st.subheader("🎯 Suas Próximas Ações de Estudo e Preparação")
    acoes = stats.get("proximas_acoes", [])
    if acoes:
        for ac in acoes:
            col_a1, col_a2 = st.columns([4, 1])
            with col_a1:
                dt_acao = f" (Prazo: {formatar_data_br(ac.get('data_proxima_acao'))})" if ac.get('data_proxima_acao') else ""
                st.markdown(f"**📌 {ac.get('proxima_acao')}**{dt_acao} — *{ac.get('nome')}* ({ac.get('orgao')})")
            with col_a2:
                if st.button("Marcar Concluída", key=f"btn_done_{ac['id']}"):
                    ConcursoRepository.definir_proxima_acao(ac["id"], ac["proxima_acao"], ac.get("data_proxima_acao"), concluida=True)
                    st.success("Ação concluída!")
                    st.rerun()
    else:
        st.info("Você ainda não definiu nenhuma próxima ação pendente. Vá na aba 'Concursos' para definir ações (ex: 'Ler edital', 'Pagar taxa', 'Estudar Português').")
