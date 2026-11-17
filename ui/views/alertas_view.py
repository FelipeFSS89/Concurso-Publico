"""
Tela da Central de Alertas Inteligentes
Classificados por criticidade: Vermelho (Urgente), Amarelo (Atenção), Verde (Novidades) e Azul (Informativo).
"""
import streamlit as st
from database.repository import AlertaRepository
from services.alert_service import AlertService
from ui.components import render_header, render_alert_box, formatar_data_br

def render_alertas_view():
    """Renderiza a Central de Alertas categorizada."""
    render_header(
        "Central de Alertas e Notificações",
        "Monitoramento contínuo de prazos críticos de inscrição, provas iminentes e compatibilidade de perfis."
    )

    # Barra superior de controle
    col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
    with col_c1:
        tipo_filtro = st.selectbox(
            "Filtrar por Categoria de Alerta:",
            [
                ("todos", "Todos os Alertas"),
                ("urgente", "🔴 Vermelho - Urgentes (Prazos de Inscrição e Taxa)"),
                ("atencao", "🟡 Amarelo - Atenção (Provas se aproximando)"),
                ("novidade", "🟢 Verde - Novidades (Editais e Compatibilidade)"),
                ("info", "🔵 Azul - Informativos Gerais")
            ],
            format_func=lambda x: x[1]
        )[0]
    
    with col_c2:
        st.write("")
        st.write("")
        if st.button("🔄 Recalcular Alertas", use_container_width=True):
            qtd = AlertService.reavaliar_todos_alertas()
            st.success(f"Alertas recalculados com sucesso! ({qtd} processados)")
            st.rerun()

    with col_c3:
        st.write("")
        st.write("")
        if st.button("🧹 Marcar Todos como Lidos", use_container_width=True):
            AlertaRepository.marcar_todos_como_lidos()
            st.success("Todos os alertas marcados como lidos!")
            st.rerun()

    # Opção de exibir lidos
    col_l1, col_l2 = st.columns([3, 1])
    with col_l1:
        apenas_nao_lidos = st.checkbox("Exibir apenas alertas não lidos", value=True)
    with col_l2:
        if st.button("🗑️ Limpar Alertas Lidos"):
            AlertaRepository.limpar_alertas_lidos()
            st.info("Alertas lidos removidos.")
            st.rerun()

    # Busca alertas
    alertas = AlertaRepository.listar_alertas(apenas_nao_lidos=apenas_nao_lidos, tipo=tipo_filtro)

    st.markdown("---")

    if not alertas:
        st.info("Nenhum alerta encontrado para os critérios selecionados. Tudo em ordem com seus concursos!")
        return

    st.write(f"**{len(alertas)} alertas encontrados:**")

    for a in alertas:
        aid = a["id"]
        tipo = a["tipo"]
        is_lido = bool(a.get("lido", 0))

        col_box, col_act = st.columns([5, 1])
        with col_box:
            render_alert_box(
                tipo=tipo,
                titulo=a["titulo"],
                mensagem=a["mensagem"],
                data_referencia=a.get("data_referencia")
            )
        with col_act:
            st.write("")
            if not is_lido:
                if st.button("Marcar Lido", key=f"btn_lido_{aid}", use_container_width=True):
                    AlertaRepository.marcar_como_lido(aid)
                    st.rerun()
            else:
                st.caption("✅ Lido")
