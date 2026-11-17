"""
Tela de Estatísticas e Análise Gráfica com Plotly
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database.repository import ConcursoRepository
from ui.components import render_header

def render_estatisticas_view():
    """Renderiza gráficos analíticos interativos."""
    render_header(
        "Métricas e Estatísticas Estratégicas",
        "Análise visual aprofundada dos concursos monitorados, remunerações, áreas de atuação e sua evolução."
    )

    dados = ConcursoRepository.obter_dados_graficos()
    concursos = ConcursoRepository.buscar_concursos()

    if not concursos:
        st.info("Nenhum concurso cadastrado no momento para gerar estatísticas.")
        return

    # Linha 1 de Gráficos: Status do Usuário e Distribuição por Estados
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("📌 Concursos por Status do Usuário")
        status_data = dados.get("status", [])
        if status_data:
            df_st = pd.DataFrame(status_data)
            fig_st = px.pie(
                df_st,
                names="status",
                values="qtd",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_st.update_traces(textposition='inside', textinfo='percent+label')
            fig_st.update_layout(height=350, margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_st, use_container_width=True)

    with col_g2:
        st.subheader("📍 Concursos por Estado (UF)")
        uf_data = dados.get("estados", [])
        if uf_data:
            df_uf = pd.DataFrame(uf_data)
            fig_uf = px.bar(
                df_uf,
                x="estado",
                y="qtd",
                labels={"estado": "UF", "qtd": "Total Concursos"},
                color="qtd",
                color_continuous_scale="Viridis",
                text="qtd"
            )
            fig_uf.update_traces(textposition='outside')
            fig_uf.update_layout(height=350, margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_uf, use_container_width=True)

    st.markdown("---")

    # Linha 2 de Gráficos: Escolaridade e Faixas Salariais
    col_g3, col_g4 = st.columns(2)

    with col_g3:
        st.subheader("🎓 Distribuição por Nível de Escolaridade")
        esc_data = dados.get("escolaridade", [])
        if esc_data:
            df_esc = pd.DataFrame(esc_data)
            fig_esc = px.bar(
                df_esc,
                x="escolaridade",
                y="qtd",
                color="escolaridade",
                labels={"escolaridade": "Escolaridade", "qtd": "Concursos"},
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_esc.update_layout(height=350, margin=dict(t=20, b=20, l=10, r=10), showlegend=False)
            st.plotly_chart(fig_esc, use_container_width=True)

    with col_g4:
        st.subheader("💰 Distribuição de Faixas Salariais")
        sal_data = dados.get("salarios", [])
        if sal_data:
            df_sal = pd.DataFrame(sal_data)
            fig_sal = px.pie(
                df_sal,
                names="faixa",
                values="qtd",
                color_discrete_sequence=px.colors.sequential.YlGnBu_r
            )
            fig_sal.update_layout(height=350, margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_sal, use_container_width=True)

    st.markdown("---")

    # Linha 3 de Gráficos: Concursos por Área de Formação e Evolução Temporal
    col_g5, col_g6 = st.columns(2)

    with col_g5:
        st.subheader("🏢 Oportunidades por Área de Atuação")
        df_all = pd.DataFrame(concursos)
        if "area_formacao" in df_all.columns:
            area_counts = df_all["area_formacao"].value_counts().reset_index()
            area_counts.columns = ["area", "qtd"]
            fig_area = px.bar(
                area_counts.head(8),
                y="area",
                x="qtd",
                orientation='h',
                color="qtd",
                color_continuous_scale="Teal",
                labels={"area": "Área de Atuação", "qtd": "Concursos"}
            )
            fig_area.update_layout(height=350, margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_area, use_container_width=True)

    with col_g6:
        st.subheader("📈 Evolução dos Concursos Cadastrados")
        evo_data = dados.get("evolucao", [])
        if evo_data:
            df_evo = pd.DataFrame(evo_data)
            fig_evo = px.area(
                df_evo,
                x="dia",
                y="cadastrados",
                markers=True,
                labels={"dia": "Data de Inclusão", "cadastrados": "Novos Concursos"},
                color_discrete_sequence=["#3B82F6"]
            )
            fig_evo.update_layout(height=350, margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_evo, use_container_width=True)
