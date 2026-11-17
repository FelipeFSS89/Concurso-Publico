"""
Tela de Calendário e Linha do Tempo dos Concursos
Exibe datas de inscrições, pagamento de taxa e provas em ordem cronológica.
"""
import streamlit as st
from datetime import datetime, date
from database.repository import ConcursoRepository
from ui.components import render_header, formatar_data_br, calcular_dias_restantes

def render_calendario_view():
    """Renderiza a visão de calendário e cronograma de eventos dos concursos."""
    render_header(
        "Calendário e Cronograma Oficial",
        "Acompanhe todas as datas de abertura, encerramento de inscrições, vencimento de taxas e provas agendadas."
    )

    concursos = ConcursoRepository.buscar_concursos()

    # Coleta todos os eventos datados
    eventos = []
    for c in concursos:
        # Início de inscrição
        if c.get("data_inscricao_inicio"):
            eventos.append({
                "concurso_id": c["id"],
                "nome": c["nome"],
                "orgao": c["orgao"],
                "tipo": "Abertura de Inscrição",
                "data": c["data_inscricao_inicio"],
                "cor": "#10B981", # Verde
                "icone": "🟢"
            })
        # Fim de inscrição
        if c.get("data_inscricao_fim"):
            eventos.append({
                "concurso_id": c["id"],
                "nome": c["nome"],
                "orgao": c["orgao"],
                "tipo": "Encerramento de Inscrição",
                "data": c["data_inscricao_fim"],
                "cor": "#EF4444", # Vermelho
                "icone": "🔴"
            })
        # Pagamento da taxa
        if c.get("data_taxa_limite"):
            eventos.append({
                "concurso_id": c["id"],
                "nome": c["nome"],
                "orgao": c["orgao"],
                "tipo": "Vencimento da Taxa",
                "data": c["data_taxa_limite"],
                "cor": "#F59E0B", # Amarelo/Laranja
                "icone": "💳"
            })
        # Data da prova
        if c.get("data_prova"):
            eventos.append({
                "concurso_id": c["id"],
                "nome": c["nome"],
                "orgao": c["orgao"],
                "tipo": "Data da Prova",
                "data": c["data_prova"],
                "cor": "#3B82F6", # Azul
                "icone": "📝"
            })

    # Ordena eventos por data
    eventos.sort(key=lambda x: x["data"])

    # Filtros do Calendário
    col_m, col_t = st.columns(2)
    with col_m:
        # Extrai meses disponíveis
        meses_disponiveis = ["Todos os Meses"]
        for ev in eventos:
            try:
                m_str = datetime.strptime(ev["data"][:7], "%Y-%m").strftime("%m/%Y")
                if m_str not in meses_disponiveis:
                    meses_disponiveis.append(m_str)
            except ValueError:
                pass
        mes_filtro = st.selectbox("Filtrar por Mês/Ano:", meses_disponiveis)

    with col_t:
        tipos_disponiveis = ["Todos os Tipos", "Abertura de Inscrição", "Encerramento de Inscrição", "Vencimento da Taxa", "Data da Prova"]
        tipo_filtro = st.selectbox("Filtrar por Tipo de Evento:", tipos_disponiveis)

    # Aplica filtros
    eventos_filtrados = eventos
    if mes_filtro != "Todos os Meses":
        eventos_filtrados = [
            e for e in eventos_filtrados 
            if datetime.strptime(e["data"][:7], "%Y-%m").strftime("%m/%Y") == mes_filtro
        ]
    if tipo_filtro != "Todos os Tipos":
        eventos_filtrados = [e for e in eventos_filtrados if e["tipo"] == tipo_filtro]

    st.markdown("---")

    if not eventos_filtrados:
        st.info("Nenhum evento registrado para o mês e tipo selecionados.")
        return

    st.write(f"**{len(eventos_filtrados)} eventos programados** encontrados:")

    # Renderiza Linha do Tempo
    for ev in eventos_filtrados:
        dias = calcular_dias_restantes(ev["data"])
        dias_txt = "Hoje!" if dias == 0 else f"Em {dias} dias" if dias is not None and dias > 0 else f"Ocorreu há {abs(dias)} dias" if dias is not None else ""
        cor_badge = "#EF4444" if (dias is not None and dias <= 3 and dias >= 0) else ev["cor"]

        st.markdown(f"""
        <div style="background: white; border-left: 6px solid {ev['cor']}; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 0.85rem; font-weight: 700; color: {ev['cor']}; text-transform: uppercase;">
                    {ev['icone']} {ev['tipo']}
                </div>
                <div style="font-size: 1.05rem; font-weight: 800; color: #1E293B; margin-top: 0.2rem;">
                    {ev['nome']}
                </div>
                <div style="font-size: 0.85rem; color: #64748B;">
                    {ev['orgao']}
                </div>
            </div>
            <div style="text-align: right; min-width: 140px;">
                <div style="font-size: 1.1rem; font-weight: 800; color: #0F172A;">
                    {formatar_data_br(ev['data'])}
                </div>
                <span style="display: inline-block; background-color: {cor_badge}15; color: {cor_badge}; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; margin-top: 0.25rem;">
                    {dias_txt}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
