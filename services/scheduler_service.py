"""
Serviço de Agendamento em Segundo Plano
Executa verificações periódicas nos portais Degrau Cultural e Folha QConcursos.
"""
import time
import threading
import logging
import schedule
from datetime import datetime

from scrapers.coordinator import ScraperCoordinator
from services.alert_service import AlertService
from database.repository import ConfiguracaoRepository

logger = logging.getLogger(__name__)

class SchedulerService:
    """Gerenciador do loop de agendamento automático em background thread."""

    _thread = None
    _stop_event = threading.Event()
    _is_running = False

    @classmethod
    def _job_execucao(cls):
        """Tarefa executada pelo agendador."""
        auto_ativo = ConfiguracaoRepository.obter("atualizacao_automatica", "true") == "true"
        if not auto_ativo:
            logger.info("Agendador disparou, mas atualização automática está desativada nas configurações.")
            return

        logger.info("Agendador disparou ciclo de verificação automática.")
        try:
            coordinator = ScraperCoordinator()
            resultado = coordinator.executar_coleta(incluir_semente_se_vazio=False)
            AlertService.reavaliar_todos_alertas()
            logger.info("Ciclo automático finalizado: %s", resultado)
        except Exception as e:
            logger.error("Erro durante execução do job agendado: %s", e)

    @classmethod
    def _run_loop(cls):
        """Loop de polling do schedule rodando na thread dedicada."""
        logger.info("Thread do agendador iniciada com sucesso.")
        while not cls._stop_event.is_set():
            schedule.run_pending()
            time.sleep(10)
        logger.info("Thread do agendador finalizada.")

    @classmethod
    def iniciar(cls, intervalo_horas: int = 6):
        """Inicia a thread de segundo plano com a frequência configurada."""
        if cls._is_running:
            logger.info("Agendador já está em execução.")
            return

        schedule.clear()
        # Agenda execução a cada N horas
        schedule.every(intervalo_horas).hours.do(cls._job_execucao)
        
        # Também agenda verificação diária pela manhã às 08:00
        horario = ConfiguracaoRepository.obter("horario_verificacao", "08:00")
        try:
            schedule.every().day.at(horario).do(cls._job_execucao)
        except Exception:
            schedule.every().day.at("08:00").do(cls._job_execucao)

        cls._stop_event.clear()
        cls._thread = threading.Thread(target=cls._run_loop, daemon=True, name="ConcursosSchedulerThread")
        cls._thread.start()
        cls._is_running = True
        logger.info("Serviço de agendamento ativado. Intervalo: %d horas. Horário fixo: %s", intervalo_horas, horario)

    @classmethod
    def parar(cls):
        """Para a thread de segundo plano de forma graciosa."""
        if not cls._is_running:
            return
        cls._stop_event.set()
        cls._is_running = False
        schedule.clear()
        logger.info("Serviço de agendamento parado.")

    @classmethod
    def esta_ativo(cls) -> bool:
        """Indica se o agendador está rodando."""
        return cls._is_running and cls._thread is not None and cls._thread.is_alive()
