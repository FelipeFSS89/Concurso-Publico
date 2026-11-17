"""
Scraper Especializado para Degrau Cultural (degraucultural.com.br)
"""
import logging
import re
from typing import List, Dict, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from config import SITES_MONITORADOS

logger = logging.getLogger(__name__)

class DegrauScraper(BaseScraper):
    """Coleta e estrutura concursos listados na Degrau Cultural."""

    def __init__(self):
        super().__init__()
        self.config = SITES_MONITORADOS["degrau_cultural"]

    def coletar_concursos(self) -> List[Dict[str, Any]]:
        """Acessa a página de concursos da Degrau Cultural e extrai as oportunidades."""
        url = self.config["url"]
        base_url = self.config["base_url"]
        logger.info("Iniciando coleta em Degrau Cultural: %s", url)

        html = self.fetch_html(url)
        if not html:
            logger.warning("Não foi possível carregar a página da Degrau Cultural.")
            return []

        soup = BeautifulSoup(html, "html.parser")
        concursos = []

        # Procura os cards de concursos (cards a.pcard ou elementos com classe card/concurso)
        cards = soup.select("a.pcard, .pcard, [class*='pcard']")
        logger.info("Degrau Cultural: %d elementos de cards encontrados.", len(cards))

        for card in cards:
            try:
                # Link
                href = card.get("href", "")
                link_original = urljoin(base_url, href) if href else url

                # Título completo
                title_attr = card.get("title", "")
                card_text = card.get_text(" | ", strip=True)

                if not card_text and not title_attr:
                    continue

                partes_title = [p.strip() for p in title_attr.split("·") if p.strip()] if title_attr else []
                partes_text = [p.strip() for p in card_text.split("|") if p.strip()]

                # Órgão e Nome
                if partes_title:
                    sigla = partes_title[0]
                    orgao = partes_title[1] if len(partes_title) > 1 else sigla
                    cargo = partes_title[2] if len(partes_title) > 2 else "Diversos Cargos"
                    nome = f"{sigla} - {cargo}"
                else:
                    sigla = partes_text[1] if len(partes_text) > 1 else "Concurso Público"
                    orgao = partes_text[2] if len(partes_text) > 2 else sigla
                    cargo = partes_text[3] if len(partes_text) > 3 else "Diversos Cargos"
                    nome = f"{sigla} - {cargo}"

                # Situação / Status do edital
                situacao = "Inscrições Abertas"
                if partes_text:
                    primeiro = partes_text[0].lower()
                    if "solicitado" in primeiro:
                        situacao = "Solicitado"
                    elif "autorizado" in primeiro:
                        situacao = "Autorizado"
                    elif "confirmado" in primeiro:
                        situacao = "Confirmado / Edital Iminente"
                    elif "aberto" in primeiro or "inscrição" in primeiro:
                        situacao = "Inscrições Abertas"

                # Escolaridade
                escolaridade = "Médio"
                for p in partes_text:
                    if "nível" in p.lower() or "superior" in p.lower() or "médio" in p.lower() or "técnico" in p.lower():
                        escolaridade = self.normalizar_escolaridade(p)
                        break

                # Vagas
                vagas = 0
                for p in partes_text:
                    if "vaga" in p.lower():
                        vagas = self.extrair_vagas(p)
                        break

                # Salário
                salario = self.extrair_salario(card_text)
                salario_texto = f"R$ {salario:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if salario > 0 else "A consultar"

                # Estado
                estado = self.inferir_estado(f"{nome} {orgao} {card_text}")
                area = self.inferir_area(cargo, orgao)

                # Datas padrão estimadas ou extraídas
                data_publicacao = None
                data_inscricao_fim = None

                item = {
                    "nome": nome[:150],
                    "orgao": orgao[:150],
                    "instituicao": "Banca a Definir",
                    "cargo": cargo[:150],
                    "escolaridade": escolaridade,
                    "area_formacao": area,
                    "salario": salario,
                    "salario_texto": salario_texto,
                    "vagas": vagas,
                    "data_publicacao": data_publicacao,
                    "data_inscricao_inicio": None,
                    "data_inscricao_fim": data_inscricao_fim,
                    "data_prova": None,
                    "data_taxa_limite": None,
                    "cidade": "Rio de Janeiro e Nacional" if estado in ["RJ", "Nacional"] else "A Definir",
                    "estado": estado,
                    "link_edital": link_original,
                    "link_original": link_original,
                    "fonte": "Degrau Cultural",
                    "situacao_edital": situacao
                }
                concursos.append(item)
            except Exception as e:
                logger.error("Erro ao processar card na Degrau Cultural: %s", e)
                continue

        # Evita duplicatas internas da página
        vistos = set()
        unicos = []
        for c in concursos:
            chave = f"{c['nome']}_{c['orgao']}"
            if chave not in vistos:
                vistos.add(chave)
                unicos.append(c)

        logger.info("Degrau Cultural: %d concursos extraídos com sucesso.", len(unicos))
        return unicos
