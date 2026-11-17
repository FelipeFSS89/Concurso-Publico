"""
Serviço Centralizador de Alertas Inteligentes
Gera e classifica alertas em Vermelho (Urgente), Amarelo (Atenção), Verde (Novidades) e Azul (Informativo).
"""
import logging
from datetime import date, datetime
from typing import List, Dict, Any
from database.repository import ConcursoRepository, AlertaRepository, ConfiguracaoRepository
from services.matcher_service import MatcherService

logger = logging.getLogger(__name__)

class AlertService:
    """Calcula e despacha alertas com base nos prazos de inscrição, prova e interesses."""

    @classmethod
    def reavaliar_todos_alertas(cls) -> int:
        """
        Varre todos os concursos do banco e calcula alertas de prazos e provas relativos a hoje.
        Retorna o número de alertas novos ou reforçados.
        """
        hoje = date.today()
        concursos = ConcursoRepository.buscar_concursos()
        concursos = MatcherService.enriquecer_concursos_com_match(concursos)
        alertas_gerados = 0

        for c in concursos:
            cid = c["id"]
            nome = c["nome"]
            orgao = c["orgao"]
            fim_insc = c.get("data_inscricao_fim")
            data_taxa = c.get("data_taxa_limite")
            data_prova = c.get("data_prova")

            # -------------------------------------------------------------
            # ALERTAS VERMELHOS (URGENTE) - Prazos de inscrição e pagamento
            # -------------------------------------------------------------
            if fim_insc:
                try:
                    dt_fim = datetime.strptime(fim_insc, "%Y-%m-%d").date()
                    dias_restantes = (dt_fim - hoje).days

                    if dias_restantes == 0:
                        AlertaRepository.salvar_alerta(
                            tipo="urgente",
                            titulo="🚨 ÚLTIMO DIA DE INSCRIÇÃO!",
                            mensagem=f"As inscrições para o concurso {nome} ({orgao}) se encerram HOJE!",
                            concurso_id=cid,
                            data_referencia=fim_insc
                        )
                        alertas_gerados += 1
                    elif dias_restantes == 3:
                        AlertaRepository.salvar_alerta(
                            tipo="urgente",
                            titulo="⚠️ Falta 3 dias para encerrar inscrição!",
                            mensagem=f"O prazo de inscrição para {nome} expira em 3 dias ({dt_fim.strftime('%d/%m/%Y')}).",
                            concurso_id=cid,
                            data_referencia=fim_insc
                        )
                        alertas_gerados += 1
                    elif dias_restantes == 7:
                        AlertaRepository.salvar_alerta(
                            tipo="urgente",
                            titulo="⏰ Falta 7 dias para encerrar inscrição",
                            mensagem=f"Atenção: restam exatamente 7 dias para o encerramento das inscrições de {nome}.",
                            concurso_id=cid,
                            data_referencia=fim_insc
                        )
                        alertas_gerados += 1
                except ValueError:
                    pass

            if data_taxa:
                try:
                    dt_taxa = datetime.strptime(data_taxa, "%Y-%m-%d").date()
                    dias_taxa = (dt_taxa - hoje).days
                    if dias_taxa in [0, 1]:
                        AlertaRepository.salvar_alerta(
                            tipo="urgente",
                            titulo="💳 Último dia de pagamento da taxa de inscrição!",
                            mensagem=f"Atenção ao pagamento da taxa do concurso {nome}. Prazo limite: {dt_taxa.strftime('%d/%m/%Y')}.",
                            concurso_id=cid,
                            data_referencia=data_taxa
                        )
                        alertas_gerados += 1
                except ValueError:
                    pass

            # -------------------------------------------------------------
            # ALERTAS AMARELOS (ATENÇÃO) - Provas chegando
            # -------------------------------------------------------------
            if data_prova:
                try:
                    dt_prova = datetime.strptime(data_prova, "%Y-%m-%d").date()
                    dias_prova = (dt_prova - hoje).days

                    if dias_prova == 3:
                        AlertaRepository.salvar_alerta(
                            tipo="atencao",
                            titulo="📝 Prova em 3 dias!",
                            mensagem=f"A prova de {nome} ocorrerá em 3 dias! Prepare documentos, canetas e local de prova.",
                            concurso_id=cid,
                            data_referencia=data_prova
                        )
                        alertas_gerados += 1
                    elif dias_prova == 7:
                        AlertaRepository.salvar_alerta(
                            tipo="atencao",
                            titulo="📅 Prova em 7 dias!",
                            mensagem=f"Falta 1 semana para a prova de {nome} ({dt_prova.strftime('%d/%m/%Y')}). Revise pontos-chave!",
                            concurso_id=cid,
                            data_referencia=data_prova
                        )
                        alertas_gerados += 1
                    elif dias_prova == 15:
                        AlertaRepository.salvar_alerta(
                            tipo="atencao",
                            titulo="⏳ Prova em 15 dias!",
                            mensagem=f"Faltam 15 dias para a realização da prova de {nome}.",
                            concurso_id=cid,
                            data_referencia=data_prova
                        )
                        alertas_gerados += 1
                    elif dias_prova == 30:
                        AlertaRepository.salvar_alerta(
                            tipo="atencao",
                            titulo="📌 Prova em 30 dias!",
                            mensagem=f"Reta final! Falta 1 mês para a prova de {nome} ({dt_prova.strftime('%d/%m/%Y')}).",
                            concurso_id=cid,
                            data_referencia=data_prova
                        )
                        alertas_gerados += 1
                except ValueError:
                    pass

            # -------------------------------------------------------------
            # ALERTAS VERDES (NOVIDADE) - Concurso compatível com perfil
            # -------------------------------------------------------------
            if c.get("is_compativel") and c.get("areas_match"):
                # Verifica se é novo (publicado nos últimos 7 dias)
                dt_pub = c.get("data_publicacao")
                if dt_pub:
                    try:
                        pub = datetime.strptime(dt_pub, "%Y-%m-%d").date()
                        if (hoje - pub).days <= 7:
                            areas_str = ", ".join(c["areas_match"])
                            AlertaRepository.salvar_alerta(
                                tipo="novidade",
                                titulo=f"🎯 Concurso compatível com seu perfil: {nome}",
                                mensagem=f"Novo concurso compatível com suas áreas cadastradas ({areas_str}) no órgão {orgao}. Salário: {c.get('salario_texto')}.",
                                concurso_id=cid,
                                data_referencia=dt_pub
                            )
                            alertas_gerados += 1
                    except ValueError:
                        pass

        logger.info("Reavaliação de alertas finalizada. %d novos alertas verificados.", alertas_gerados)
        return alertas_gerados
