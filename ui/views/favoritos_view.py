"""
Tela Exclusiva de Concursos Favoritos
"""
import streamlit as st
from datetime import date
from database.repository import ConcursoRepository
from services.matcher_service import MatcherService
from config import STATUS_USUARIO_LISTA
from ui.components import render_header, formatar_data_br, calcular_dias_restantes, render_status_badge

def render_favoritos_view():
    """Renderiza a lista de concursos marcados com estrela/favorito."""
    render_header(
        "Meus Concursos Favoritos ⭐",
        "Acesso rápido aos certames de maior prioridade para seu plano de estudos e carreira."
    )

    concursos = ConcursoRepository.buscar_concursos({"apenas_favoritos": True})
    concursos = MatcherService.enriquecer_concursos_com_match(concursos)

    if not concursos:
        st.info("⭐ Você ainda não favoritou nenhum concurso. Vá até a aba 'Concursos' e clique em '☆ Favoritar' nos editais de seu interesse para acompanhá-los de perto aqui.")
        return

    st.write(f"Você possui **{len(concursos)} concursos favoritos** sob acompanhamento especial.")

    for c in concursos:
        cid = c["id"]
        is_comp = bool(c.get("is_compativel"))
        match_areas = c.get("areas_match", [])

        st.markdown(f"""
        <div style="background: white; border: 2px solid #F59E0B; border-radius: 12px; padding: 1.25rem; margin-bottom: 0.5rem; box-shadow: 0 2px 4px rgba(245, 158, 11, 0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; color: #1E293B;">⭐ {c['nome']}</h3>
                    <div style="color: #64748B; font-size: 0.9rem; margin-top: 0.25rem;">
                        <strong>Órgão:</strong> {c['orgao']} • <strong>Banca:</strong> {c['instituicao'] or 'A Definir'} • <strong>UF:</strong> {c['estado']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_b1, col_b2 = st.columns([3, 1])
        with col_b1:
            tags_html = ""
            if is_comp:
                tags_html += f"""<span class="badge-tag badge-compatible">🎯 Compatível: {', '.join(match_areas)}</span>"""
            tags_html += f"""<span class="badge-tag badge-salario">💰 {c['salario_texto']}</span>"""
            tags_html += f"""<span class="badge-tag badge-vagas">👥 {c['vagas']} vagas</span>"""
            tags_html += f"""<span class="badge-tag badge-uf">🎓 {c['escolaridade']}</span>"""
            st.markdown(tags_html, unsafe_allow_html=True)

        with col_b2:
            if st.button("❌ Remover dos Favoritos", key=f"unfav_{cid}"):
                ConcursoRepository.alternar_favorito(cid)
                st.rerun()

        # Prazos e Status
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            dias_i = calcular_dias_restantes(c.get("data_inscricao_fim"))
            txt_i = f" ({dias_i} dias)" if dias_i is not None and dias_i >= 0 else " (Encerrada)" if dias_i is not None else ""
            st.markdown(f"**Inscrições até:** {formatar_data_br(c.get('data_inscricao_fim'))}{txt_i}")
        with col_p2:
            dias_p = calcular_dias_restantes(c.get("data_prova"))
            txt_p = f" (Em {dias_p} dias)" if dias_p is not None and dias_p >= 0 else ""
            st.markdown(f"**Data da Prova:** {formatar_data_br(c.get('data_prova'))}{txt_p}")
        with col_p3:
            st.markdown(f"**Meu Status:** {render_status_badge(c.get('status_usuario', 'Não analisado'))}", unsafe_allow_html=True)

        with st.expander("📝 Gerenciar Status e Próxima Ação Deste Favorito"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                idx_st = STATUS_USUARIO_LISTA.index(c.get("status_usuario", "Não analisado")) if c.get("status_usuario") in STATUS_USUARIO_LISTA else 0
                novo_st = st.selectbox("Atualizar Status:", STATUS_USUARIO_LISTA, index=idx_st, key=f"fav_st_{cid}")
                obs_muda = st.text_input("Observação:", key=f"fav_obs_muda_{cid}")
                if st.button("Salvar Status", key=f"fav_btn_st_{cid}"):
                    ConcursoRepository.atualizar_status_usuario(cid, novo_st, obs_muda)
                    st.success("Status atualizado!")
                    st.rerun()
            with col_s2:
                prox = st.text_input("Próxima Ação:", value=c.get("proxima_acao") or "", key=f"fav_pa_{cid}")
                if st.button("Salvar Próxima Ação", key=f"fav_btn_pa_{cid}"):
                    ConcursoRepository.definir_proxima_acao(cid, prox)
                    st.success("Ação definida com sucesso!")
                    st.rerun()

        st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
