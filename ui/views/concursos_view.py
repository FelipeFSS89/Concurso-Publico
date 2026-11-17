"""
Tela de Concursos: Listagem, Filtros Combináveis, Detalhamento e Gestão Completa
"""
import streamlit as st
import pandas as pd
from datetime import date
from typing import Dict, Any

from database.repository import ConcursoRepository, ConfiguracaoRepository
from services.matcher_service import MatcherService
from services.export_service import ExportService
from config import STATUS_USUARIO_LISTA, ESCOLARIDADE_LISTA, ESTADOS_BRASIL, STATUS_CONFIG
from ui.components import render_header, formatar_data_br, calcular_dias_restantes, render_status_badge

def render_concursos_view():
    """Renderiza a tela de listagem e gerenciamento de concursos."""
    render_header(
        "Explorador de Concursos Públicos",
        "Busca avançada, filtros combinados, destaques de compatibilidade e gestão individual de cada certame."
    )

    # -------------------------------------------------------------
    # 1. BARRA LATERAL DE FILTROS OU EXPANDER
    # -------------------------------------------------------------
    with st.expander("🔍 Painel de Filtros Avançados", expanded=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        with col_f1:
            busca = st.text_input("Palavra-chave (Nome, Órgão ou Cargo)", placeholder="Ex: INSS, Analista, Fiscal...")
            escolaridade = st.selectbox("Escolaridade", ["Todas"] + ESCOLARIDADE_LISTA)
            
        with col_f2:
            formacoes_cadastradas = ConfiguracaoRepository.listar_formacoes()
            nomes_formacoes = ["Todas"] + [f["nome"] for f in formacoes_cadastradas]
            formacao_sel = st.selectbox("Área de Formação / Interesse", nomes_formacoes)
            estado_sel = st.selectbox("Estado (UF)", ["Todos"] + ESTADOS_BRASIL)

        with col_f3:
            status_sel = st.selectbox("Meu Status", ["Todos"] + STATUS_USUARIO_LISTA)
            salario_min = st.number_input("Salário Mínimo (R$)", min_value=0, value=0, step=1000)

        with col_f4:
            ordenacao = st.selectbox(
                "Ordenar por",
                [
                    ("recente", "Mais Recentes"),
                    ("prazo_inscricao", "Prazo de Inscrição Mais Próximo"),
                    ("data_prova", "Data da Prova Mais Próxima"),
                    ("maior_salario", "Maior Salário"),
                    ("mais_vagas", "Mais Vagas")
                ],
                format_func=lambda x: x[1]
            )[0]

            col_chk1, col_chk2 = st.columns(2)
            with col_chk1:
                apenas_abertos = st.checkbox("Apenas Abertos", value=False)
            with col_chk2:
                apenas_favoritos = st.checkbox("Apenas Favoritos ⭐", value=False)

    # -------------------------------------------------------------
    # 2. CONSULTA AO BANCO DE DADOS
    # -------------------------------------------------------------
    filtros = {
        "busca": busca,
        "escolaridade": escolaridade,
        "area_formacao": formacao_sel,
        "estado": estado_sel,
        "status_usuario": status_sel,
        "salario_min": salario_min,
        "ordenacao": ordenacao,
        "apenas_abertos": apenas_abertos,
        "apenas_favoritos": apenas_favoritos
    }

    concursos = ConcursoRepository.buscar_concursos(filtros)
    # Enriquecimento com sistema de matching de formação
    concursos = MatcherService.enriquecer_concursos_com_match(concursos)

    # -------------------------------------------------------------
    # 3. BARRA DE STATUS DOS RESULTADOS E EXPORTAÇÃO
    # -------------------------------------------------------------
    col_res, col_exp = st.columns([2, 1])
    with col_res:
        st.write(f"**{len(concursos)} concursos encontrados** com os critérios aplicados.")
    with col_exp:
        col_csv, col_xlsx = st.columns(2)
        with col_csv:
            csv_bytes = ExportService.exportar_csv(concursos)
            st.download_button(
                "📥 Exportar CSV",
                data=csv_bytes,
                file_name="concursos_filtrados.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_xlsx:
            xlsx_bytes = ExportService.exportar_excel(concursos)
            st.download_button(
                "📥 Exportar Excel",
                data=xlsx_bytes,
                file_name="concursos_filtrados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    st.markdown("---")

    if not concursos:
        st.warning("Nenhum concurso encontrado para os filtros selecionados. Experimente limpar ou flexibilizar os filtros.")
        return

    # -------------------------------------------------------------
    # 4. MODO DE VISUALIZAÇÃO (CARDS OU TABELA)
    # -------------------------------------------------------------
    modo_vis = st.radio("Modo de exibição:", ["Cartões Detalhados", "Tabela Resumida"], horizontal=True)

    if modo_vis == "Tabela Resumida":
        # Formata dados para tabela interativa
        tabela_dados = []
        for c in concursos:
            tabela_dados.append({
                "ID": c["id"],
                "⭐": "⭐" if c.get("is_favorito") else "",
                "Nome": c["nome"],
                "Órgão": c["orgao"],
                "Banca": c["instituicao"] or "A definir",
                "Cargo": c["cargo"],
                "Escolaridade": c["escolaridade"],
                "UF": c["estado"],
                "Vagas": c["vagas"],
                "Salário": c["salario_texto"],
                "Fim Inscrição": formatar_data_br(c.get("data_inscricao_fim")),
                "Data Prova": formatar_data_br(c.get("data_prova")),
                "Meu Status": c.get("status_usuario", "Não analisado"),
                "Fonte": c.get("fonte", "Web")
            })
        st.dataframe(pd.DataFrame(tabela_dados), use_container_width=True, hide_index=True)
        st.caption("Alterne para o modo 'Cartões Detalhados' para editar status, adicionar anotações e gerenciar próximas ações.")

    else:
        # Modo Cartões Detalhados
        for c in concursos:
            cid = c["id"]
            is_fav = bool(c.get("is_favorito"))
            is_comp = bool(c.get("is_compativel"))
            match_areas = c.get("areas_match", [])

            with st.container():
                st.markdown(f"""
                <div style="background: white; border: 1px solid {'#10B981' if is_comp else '#E2E8F0'}; border-radius: 12px; padding: 1.25rem; margin-bottom: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="font-size: 1.2rem; font-weight: 800; color: #0F172A;">{c['nome']}</span>
                            <div style="font-size: 0.9rem; color: #475569; margin-top: 0.2rem;">
                                <strong>Órgão:</strong> {c['orgao']} • <strong>Banca:</strong> {c['instituicao'] or 'A Definir'} • <strong>Fonte:</strong> {c['fonte']}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Badges e Metadados
                badges_col1, badges_col2 = st.columns([3, 1])
                with badges_col1:
                    tags_html = ""
                    if is_comp:
                        tags_html += f"""<span class="badge-tag badge-compatible">🎯 Compatível: {', '.join(match_areas)}</span>"""
                    tags_html += f"""<span class="badge-tag badge-uf">📍 {c['estado']} - {c.get('cidade', 'Geral')}</span>"""
                    tags_html += f"""<span class="badge-tag badge-salario">💰 {c['salario_texto']}</span>"""
                    tags_html += f"""<span class="badge-tag badge-vagas">👥 {c['vagas']} vagas</span>"""
                    tags_html += f"""<span class="badge-tag badge-vagas">🎓 {c['escolaridade']}</span>"""
                    st.markdown(tags_html, unsafe_allow_html=True)
                
                with badges_col2:
                    # Botão de favoritar
                    fav_label = "⭐ Favorito" if is_fav else "☆ Favoritar"
                    if st.button(fav_label, key=f"fav_btn_{cid}"):
                        novo_fav = ConcursoRepository.alternar_favorito(cid)
                        st.rerun()

                # Datas em colunas
                col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                with col_d1:
                    dias_insc = calcular_dias_restantes(c.get("data_inscricao_fim"))
                    dias_insc_txt = f" ({dias_insc}d restantes)" if dias_insc is not None and dias_insc >= 0 else " (Encerrada)" if dias_insc is not None else ""
                    st.markdown(f"**Término Inscrições:**<br>{formatar_data_br(c.get('data_inscricao_fim'))}{dias_insc_txt}", unsafe_allow_html=True)
                with col_d2:
                    dias_prov = calcular_dias_restantes(c.get("data_prova"))
                    dias_prov_txt = f" (Em {dias_prov}d)" if dias_prov is not None and dias_prov >= 0 else ""
                    st.markdown(f"**Data da Prova:**<br>{formatar_data_br(c.get('data_prova'))}{dias_prov_txt}", unsafe_allow_html=True)
                with col_d3:
                    st.markdown(f"**Vencimento Taxa:**<br>{formatar_data_br(c.get('data_taxa_limite'))}", unsafe_allow_html=True)
                with col_d4:
                    st.markdown(f"**Status Atual:**<br>{render_status_badge(c.get('status_usuario', 'Não analisado'))}", unsafe_allow_html=True)

                # Gaveta de Gestão / Ações do Concurso
                with st.expander(f"⚙️ Gerenciar Meu Status, Observações e Links ({c['nome']})"):
                    col_m1, col_m2 = st.columns([1, 1])

                    # Lado Esquerdo: Alterar Status e Próxima Ação
                    with col_m1:
                        st.markdown("##### 📌 Atualizar Meu Status")
                        idx_status = STATUS_USUARIO_LISTA.index(c.get("status_usuario", "Não analisado")) if c.get("status_usuario") in STATUS_USUARIO_LISTA else 0
                        novo_st = st.selectbox(
                            "Novo Status:",
                            STATUS_USUARIO_LISTA,
                            index=idx_status,
                            key=f"st_sel_{cid}"
                        )
                        motivo_st = st.text_input("Observação da mudança (opcional):", placeholder="Ex: Fiz o pagamento da taxa hoje", key=f"motivo_{cid}")

                        if st.button("Salvar Status", key=f"btn_salvar_st_{cid}"):
                            ConcursoRepository.atualizar_status_usuario(cid, novo_st, motivo_st)
                            st.success(f"Status atualizado para '{novo_st}'!")
                            st.rerun()

                        st.markdown("##### 🎯 Próxima Ação")
                        col_ac1, col_ac2 = st.columns([2, 1])
                        with col_ac1:
                            prox_acao = st.text_input("Ação:", value=c.get("proxima_acao") or "", placeholder="Ex: Ler edital, Pagar boleto", key=f"pa_{cid}")
                        with col_ac2:
                            dt_lim = st.date_input("Data Limite:", value=date.today(), key=f"dt_pa_{cid}")
                        
                        chk_concluido = st.checkbox("Ação Concluída", value=bool(c.get("acao_concluida")), key=f"chk_done_{cid}")
                        if st.button("Salvar Próxima Ação", key=f"btn_pa_{cid}"):
                            ConcursoRepository.definir_proxima_acao(cid, prox_acao, dt_lim.isoformat(), chk_concluido)
                            st.success("Próxima ação salva!")
                            st.rerun()

                    # Lado Direito: Observações e Links
                    with col_m2:
                        st.markdown("##### 📝 Anotações do Concurso")
                        nova_obs = st.text_area("Adicionar nova anotação:", placeholder="Ex: Prova será no turno da tarde em Niterói...", key=f"obs_input_{cid}", height=80)
                        if st.button("Adicionar Anotação", key=f"btn_obs_{cid}"):
                            if nova_obs.strip():
                                ConcursoRepository.adicionar_observacao(cid, nova_obs)
                                st.success("Anotação adicionada!")
                                st.rerun()

                        # Exibe detalhes e anotações anteriores
                        detalhes = ConcursoRepository.buscar_por_id(cid)
                        if detalhes and detalhes.get("observacoes"):
                            st.markdown("**Histórico de Anotações:**")
                            for ob in detalhes["observacoes"][:4]:
                                st.markdown(f"""
                                <div class="timeline-item">
                                    <div class="timeline-date">{formatar_data_br(ob['criado_em'][:10])} às {ob['criado_em'][11:16]}</div>
                                    <div class="timeline-text">{ob['texto']}</div>
                                </div>
                                """, unsafe_allow_html=True)

                        st.markdown("##### 🔗 Links Úteis")
                        col_l1, col_l2 = st.columns(2)
                        with col_l1:
                            if c.get("link_edital"):
                                st.link_button("📄 Acessar Edital", c["link_edital"], use_container_width=True)
                        with col_l2:
                            if c.get("link_original"):
                                st.link_button("🌐 Página Oficial", c["link_original"], use_container_width=True)

                st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
