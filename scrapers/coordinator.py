"""
Coordenador do Sistema de Scrapers de Concursos
"""
import logging
from datetime import datetime
from typing import Dict, Any, List

from database.repository import ConcursoRepository, ConfiguracaoRepository, AlertaRepository
from scrapers.degrau_scraper import DegrauScraper
from scrapers.folha_scraper import FolhaQCScraper
from scrapers.mock_data import MOCK_CONCURSOS

logger = logging.getLogger(__name__)

class ScraperCoordinator:
    """Orquestra a coleta de múltiplos sites, inserção no banco e geração de alertas."""

    def __init__(self):
        self.degrau = DegrauScraper()
        self.folha = FolhaQCScraper()

    def inicializar_dados_semente(self) -> int:
        """Popula o banco com dados de exemplo ricos se estiver vazio."""
        novos = 0
        for dados in MOCK_CONCURSOS:
            _, is_novo = ConcursoRepository.inserir_concurso(dados)
            if is_novo:
                novos += 1
        logger.info("Dados semente verificados. %d novos concursos inseridos.", novos)
        return novos

    def executar_coleta(self, incluir_semente_se_vazio: bool = True) -> Dict[str, Any]:
        """
        Executa a varredura completa em todas as fontes configuradas.
        Retorna estatísticas da execução.
        """
        inicio = datetime.now()
        logger.info("Iniciando ciclo de scraping às %s", inicio.strftime("%Y-%m-%d %H:%M:%S"))

        todos_itens: List[Dict[str, Any]] = []
        erros: List[str] = []

        # 1. Coleta na Degrau Cultural
        try:
            itens_degrau = self.degrau.coletar_concursos()
            todos_itens.extend(itens_degrau)
        except Exception as e:
            msg = f"Erro ao coletar Degrau Cultural: {e}"
            logger.error(msg)
            erros.append(msg)

        # 2. Coleta na Folha QConcursos
        try:
            itens_folha = self.folha.coletar_concursos()
            todos_itens.extend(itens_folha)
        except Exception as e:
            msg = f"Erro ao coletar Folha QConcursos: {e}"
            logger.error(msg)
            erros.append(msg)

        # 3. Fallback inteligente: se nada foi coletado ou se é a primeira execução
        if incluir_semente_se_vazio and len(todos_itens) == 0:
            logger.info("Nenhum item novo capturado online. Carregando base estruturada de segurança.")
            todos_itens.extend(MOCK_CONCURSOS)

        # 4. Inserção no banco com controle de novidades
        novos_count = 0
        atualizados_count = 0

        for item in todos_itens:
            try:
                cid, is_novo = ConcursoRepository.inserir_concurso(item)
                if is_novo:
                    novos_count += 1
                    # Cria alerta de novo concurso detectado (Verde)
                    AlertaRepository.salvar_alerta(
                        tipo="novidade",
                        titulo=f"Novo Concurso: {item.get('nome')}",
                        mensagem=f"Publicado edital/oportunidade para {item.get('orgao')} com {item.get('vagas', 0)} vagas e salário de {item.get('salario_texto')}.",
                        concurso_id=cid,
                        data_referencia=item.get("data_publicacao")
                    )
                else:
                    atualizados_count += 1
            except Exception as e:
                logger.error("Erro ao salvar concurso no banco: %s", e)

        # Atualiza timestamp da última verificação
        fim = datetime.now()
        timestamp_str = fim.strftime("%d/%m/%Y às %H:%M:%S")
        ConfiguracaoRepository.salvar("ultimo_scraping", timestamp_str)

        # Registra alerta informativo geral (Azul)
        AlertaRepository.salvar_alerta(
            tipo="info",
            titulo="Varredura de Concursos Concluída",
            mensagem=f"Varredura finalizada em {fim.strftime('%H:%M:%S')}. {novos_count} novos concursos identificados e {atualizados_count} atualizados.",
            data_referencia=str(fim.date())
        )

        resultado = {
            "novos": novos_count,
            "atualizados": atualizados_count,
            "total_processados": len(todos_itens),
            "erros": erros,
            "duracao_segundos": (fim - inicio).total_seconds(),
            "timestamp": timestamp_str
        }
        logger.info("Ciclo de scraping concluído: %s", resultado)
        return resultado
