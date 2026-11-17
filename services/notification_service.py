"""
Serviço de Notificações Multicanal (E-mail, Telegram e WhatsApp)
Estrutura pronta e modular para despachar alertas pelos canais configurados.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import requests
from database.repository import ConfiguracaoRepository

logger = logging.getLogger(__name__)

class NotificationService:
    """Central de envio de notificações para mensageiros e correio eletrônico."""

    @classmethod
    def enviar_alerta(cls, titulo: str, mensagem: str, canal: str = "todos") -> Dict[str, bool]:
        """
        Despacha alerta para os canais ativados.
        Retorna dicionário com o status de cada canal acionado.
        """
        resultados = {}
        config = ConfiguracaoRepository.obter_todas()

        # E-mail
        if canal in ["email", "todos"] and config.get("notificacoes_email") == "true":
            resultados["email"] = cls.enviar_email(titulo, mensagem, config)

        # Telegram
        if canal in ["telegram", "todos"] and config.get("notificacoes_telegram") == "true":
            resultados["telegram"] = cls.enviar_telegram(f"*{titulo}*\n\n{mensagem}", config)

        # WhatsApp
        if canal in ["whatsapp", "todos"] and config.get("notificacoes_whatsapp") == "true":
            resultados["whatsapp"] = cls.enviar_whatsapp(f"*{titulo}*\n\n{mensagem}", config)

        return resultados

    @classmethod
    def enviar_email(cls, assunto: str, corpo_html: str, config: Optional[Dict[str, str]] = None) -> bool:
        """Envia e-mail formatado via SMTP."""
        config = config or ConfiguracaoRepository.obter_todas()
        host = config.get("smtp_host", "smtp.gmail.com")
        porta = int(config.get("smtp_port", "587"))
        usuario = config.get("smtp_user", "")
        senha = config.get("smtp_password", "")
        destinatario = config.get("email_destinatario", usuario)

        if not usuario or not senha or not destinatario:
            logger.info("[Mock E-mail] Credenciais de SMTP não configuradas. Simulação de envio com sucesso.")
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[Painel de Concursos] {assunto}"
            msg["From"] = usuario
            msg["To"] = destinatario

            msg.attach(MIMEText(corpo_html, "html"))

            with smtplib.SMTP(host, porta) as server:
                server.starttls()
                server.login(usuario, senha)
                server.sendmail(usuario, destinatario, msg.as_string())
            logger.info("E-mail enviado com sucesso para %s", destinatario)
            return True
        except Exception as e:
            logger.error("Falha ao enviar e-mail: %s", e)
            return False

    @classmethod
    def enviar_telegram(cls, texto: str, config: Optional[Dict[str, str]] = None) -> bool:
        """Envia mensagem para Telegram Bot."""
        config = config or ConfiguracaoRepository.obter_todas()
        bot_token = config.get("telegram_token", "")
        chat_id = config.get("telegram_chat_id", "")

        if not bot_token or not chat_id:
            logger.info("[Mock Telegram] Token ou Chat ID do Telegram não configurados. Simulação de envio com sucesso.")
            return True

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        try:
            resp = requests.post(url, json={"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            logger.error("Falha ao enviar mensagem no Telegram: %s", e)
            return False

    @classmethod
    def enviar_whatsapp(cls, texto: str, config: Optional[Dict[str, str]] = None) -> bool:
        """Envia mensagem para WhatsApp via webhook / Evolution API / Twilio."""
        config = config or ConfiguracaoRepository.obter_todas()
        webhook_url = config.get("whatsapp_webhook_url", "")
        numero = config.get("whatsapp_numero", "")

        if not webhook_url or not numero:
            logger.info("[Mock WhatsApp] Webhook do WhatsApp não configurado. Simulação de envio com sucesso.")
            return True

        try:
            resp = requests.post(webhook_url, json={"number": numero, "message": texto}, timeout=10)
            return resp.status_code in [200, 201]
        except Exception as e:
            logger.error("Falha ao disparar webhook do WhatsApp: %s", e)
            return False
