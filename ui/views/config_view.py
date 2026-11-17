"""
Tela de Configurações, Formações de Interesse e Parâmetros do Sistema
"""
import streamlit as st
from database.repository import ConfiguracaoRepository, ConcursoRepository
from services.scheduler_service import SchedulerService
from services.notification_service import NotificationService
from scrapers.coordinator import ScraperCoordinator
from services.alert_service import AlertService
from config import ESTADOS_BRASIL, AREAS_FORMACAO_SUGESTOES
from ui.components import render_header

def render_config_view():
    """Renderiza painel de preferências e áreas de interesse."""
    render_header(
        "Configurações e Áreas de Interesse",
        "Personalize seus cursos de graduação/nível médio, agendamento de varredura e canais de notificação."
    )

    tab_formacoes, tab_agendamento, tab_notif, tab_manutencao = st.tabs([
        "🎓 Minhas Formações de Interesse",
        "⏰ Atualização Automática & Filtros",
        "📲 Canais de Notificação (E-mail/Telegram/WhatsApp)",
        "🛠️ Manutenção & Banco de Dados"
    ])

    # -------------------------------------------------------------
    # TAB 1: FORMAÇÕES DE INTERESSE
    # -------------------------------------------------------------
    with tab_formacoes:
        st.subheader("Cadastro de Cursos e Áreas Compatíveis")
        st.markdown("""
        Concursos públicos correspondentes a estas áreas receberão o selo verde **🎯 Compatível** 
        e emitirão alertas de **Novidade** assim que forem detectados nos portais monitorados.
        """)

        col_add1, col_add2, col_add3 = st.columns([2, 3, 1])
        with col_add1:
            nome_formacao = st.text_input("Nome da Área / Curso:", placeholder="Ex: Tecnologia da Informação")
        with col_add2:
            kw_formacao = st.text_input("Palavras-chave (separadas por vírgula):", placeholder="Ex: ti, computação, sistemas, desenvolvimento, dados")
        with col_add3:
            st.write("")
            st.write("")
            if st.button("➕ Adicionar", use_container_width=True):
                if nome_formacao.strip():
                    ConfiguracaoRepository.adicionar_formacao(nome_formacao, kw_formacao)
                    st.success(f"Área '{nome_formacao}' adicionada com sucesso!")
                    st.rerun()

        # Sugestões rápidas
        st.caption("💡 Sugestões comuns para adicionar rapidamente:")
        cols_sug = st.columns(6)
        for i, sug in enumerate(AREAS_FORMACAO_SUGESTOES[:6]):
            with cols_sug[i]:
                if st.button(sug, key=f"sug_{i}"):
                    ConfiguracaoRepository.adicionar_formacao(sug, sug.lower())
                    st.rerun()

        st.markdown("---")
        st.markdown("#### Áreas Atualmente Cadastradas no Seu Perfil:")
        formacoes = ConfiguracaoRepository.listar_formacoes()

        if formacoes:
            for f in formacoes:
                col_f1, col_f2 = st.columns([5, 1])
                with col_f1:
                    kw_txt = f" *(Palavras-chave: {f.get('palavras_chave')})*" if f.get("palavras_chave") else ""
                    st.markdown(f"• **{f['nome']}**{kw_txt}")
                with col_f2:
                    if st.button("Excluir", key=f"del_f_{f['id']}"):
                        ConfiguracaoRepository.remover_formacao(f["id"])
                        st.rerun()
        else:
            st.info("Nenhuma formação cadastrada ainda. Adicione acima para ativar o destaque de compatibilidade.")

    # -------------------------------------------------------------
    # TAB 2: ATUALIZAÇÃO AUTOMÁTICA E FILTROS PADRÃO
    # -------------------------------------------------------------
    with tab_agendamento:
        st.subheader("Parâmetros do Robô de Monitoramento")
        
        cfg = ConfiguracaoRepository.obter_todas()
        
        auto_ativo = st.toggle("Ativar Atualização Automática em Segundo Plano", value=(cfg.get("atualizacao_automatica") == "true"))
        
        col_sch1, col_sch2 = st.columns(2)
        with col_sch1:
            intervalo = st.selectbox(
                "Frequência de Verificação nos Sites:",
                [2, 4, 6, 8, 12, 24],
                index=[2, 4, 6, 8, 12, 24].index(int(cfg.get("intervalo_horas", 6))) if int(cfg.get("intervalo_horas", 6)) in [2, 4, 6, 8, 12, 24] else 2,
                format_func=lambda x: f"A cada {x} horas"
            )
        with col_sch2:
            horario = st.text_input("Horário fixo de verificação diária:", value=cfg.get("horario_verificacao", "08:00"))

        st.markdown("#### Critérios Mínimos de Interesse")
        col_crit1, col_crit2 = st.columns(2)
        with col_crit1:
            salario_min = st.number_input("Piso Salarial Desejado (R$):", min_value=0, value=int(cfg.get("salario_minimo", 3000)), step=500)
        with col_crit2:
            vagas_min = st.number_input("Quantidade Mínima de Vagas:", min_value=1, value=int(cfg.get("vagas_minimas", 1)), step=1)

        if st.button("💾 Salvar Parâmetros de Monitoramento", type="primary"):
            ConfiguracaoRepository.salvar("atualizacao_automatica", "true" if auto_ativo else "false")
            ConfiguracaoRepository.salvar("intervalo_horas", str(intervalo))
            ConfiguracaoRepository.salvar("horario_verificacao", horario)
            ConfiguracaoRepository.salvar("salario_minimo", str(salario_min))
            ConfiguracaoRepository.salvar("vagas_minimas", str(vagas_min))
            
            # Atualiza o serviço em background
            if auto_ativo:
                SchedulerService.iniciar(intervalo)
            else:
                SchedulerService.parar()

            st.success("Configurações salvas e aplicadas com sucesso!")
            st.rerun()

    # -------------------------------------------------------------
    # TAB 3: NOTIFICAÇÕES (EMAIL, TELEGRAM, WHATSAPP)
    # -------------------------------------------------------------
    with tab_notif:
        st.subheader("Canais de Notificação Ativos")
        st.markdown("Integração modular pronta para disparo automático de alertas em mensageiros e correio eletrônico.")

        cfg = ConfiguracaoRepository.obter_todas()

        # E-mail
        with st.expander("✉️ Notificações por E-mail (SMTP)", expanded=False):
            email_ativo = st.checkbox("Ativar Alertas por E-mail", value=(cfg.get("notificacoes_email") == "true"))
            c_e1, c_e2 = st.columns(2)
            with c_e1:
                smtp_user = st.text_input("Usuário / E-mail Remetente:", value=cfg.get("smtp_user", ""))
                smtp_host = st.text_input("Servidor SMTP:", value=cfg.get("smtp_host", "smtp.gmail.com"))
            with c_e2:
                smtp_pass = st.text_input("Senha / Senha de App:", value=cfg.get("smtp_password", ""), type="password")
                email_dest = st.text_input("E-mail do Destinatário:", value=cfg.get("email_destinatario", ""))

            if st.button("Salvar E-mail"):
                ConfiguracaoRepository.salvar("notificacoes_email", "true" if email_ativo else "false")
                ConfiguracaoRepository.salvar("smtp_user", smtp_user)
                ConfiguracaoRepository.salvar("smtp_password", smtp_pass)
                ConfiguracaoRepository.salvar("smtp_host", smtp_host)
                ConfiguracaoRepository.salvar("email_destinatario", email_dest)
                st.success("Configurações de E-mail atualizadas!")

        # Telegram
        with st.expander("✈️ Notificações via Telegram Bot", expanded=False):
            tg_ativo = st.checkbox("Ativar Alertas via Telegram", value=(cfg.get("notificacoes_telegram") == "true"))
            c_t1, c_t2 = st.columns(2)
            with c_t1:
                tg_token = st.text_input("Bot Token (do @BotFather):", value=cfg.get("telegram_token", ""))
            with c_t2:
                tg_chat = st.text_input("Chat ID:", value=cfg.get("telegram_chat_id", ""))

            if st.button("Salvar Telegram"):
                ConfiguracaoRepository.salvar("notificacoes_telegram", "true" if tg_ativo else "false")
                ConfiguracaoRepository.salvar("telegram_token", tg_token)
                ConfiguracaoRepository.salvar("telegram_chat_id", tg_chat)
                st.success("Configurações de Telegram salvas!")

        # WhatsApp
        with st.expander("💬 Notificações via WhatsApp (Webhook API)", expanded=False):
            wpp_ativo = st.checkbox("Ativar Alertas via WhatsApp", value=(cfg.get("notificacoes_whatsapp") == "true"))
            c_w1, c_w2 = st.columns(2)
            with c_w1:
                wpp_url = st.text_input("URL do Webhook / Instância:", value=cfg.get("whatsapp_webhook_url", ""))
            with c_w2:
                wpp_num = st.text_input("Número com DDI e DDD:", value=cfg.get("whatsapp_numero", ""), placeholder="Ex: 5521999998888")

            if st.button("Salvar WhatsApp"):
                ConfiguracaoRepository.salvar("notificacoes_whatsapp", "true" if wpp_ativo else "false")
                ConfiguracaoRepository.salvar("whatsapp_webhook_url", wpp_url)
                ConfiguracaoRepository.salvar("whatsapp_numero", wpp_num)
                st.success("Configurações de WhatsApp salvas!")

        st.markdown("---")
        if st.button("🚀 Enviar Notificação de Teste em Todos os Canais Ativos"):
            res = NotificationService.enviar_alerta("Teste de Conexão", "Sua central de alertas do Painel de Concursos está operando normalmente!")
            st.info(f"Disparos executados: {res}")

    # -------------------------------------------------------------
    # TAB 4: MANUTENÇÃO & BANCO
    # -------------------------------------------------------------
    with tab_manutencao:
        st.subheader("Gerenciamento do Banco de Dados SQLite")
        st.markdown("""
        O banco de dados é persistente e está gravado localmente em:
        `data/concursos.db`
        """)

        st.markdown(f"**Status do Agendador em Segundo Plano:** {'🟢 Em Execução' if SchedulerService.esta_ativo() else '⚪ Parado'}")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.button("📥 Restaurar Concursos Semente / Base Padrão", use_container_width=True):
                coord = ScraperCoordinator()
                inseridos = coord.inicializar_dados_semente()
                AlertService.reavaliar_todos_alertas()
                st.success(f"{inseridos} concursos semente restaurados/reforçados no banco!")
                st.rerun()

        with col_m2:
            if st.button("🔄 Executar Varredura Completa Forçada Agora", use_container_width=True):
                with st.spinner("Varrendo Degrau Cultural e Folha QConcursos..."):
                    coord = ScraperCoordinator()
                    res = coord.executar_coleta(incluir_semente_se_vazio=True)
                    AlertService.reavaliar_todos_alertas()
                    st.success(f"Finalizado: {res['novos']} novos, {res['atualizados']} atualizados!")
                    st.rerun()
