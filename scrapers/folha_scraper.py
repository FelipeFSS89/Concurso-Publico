"""
Scraper Especializado para Folha QConcursos (folha.qconcursos.com)
"""
import logging
import re
from typing import List, Dict, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime, date
from scrapers.base_scraper import BaseScraper
from config import SITES_MONITORADOS

logger = logging.getLogger(__name__)

class FolhaQCScraper(BaseScraper):
    """Coleta e estrutura concursos abertos e notícias da Folha QConcursos."""

    MESES = {
        "janeiro": "01", "fevereiro": "02", "março": "03", "marco": "03",
        "abril": "04", "maio": "05", "junho": "06", "julho": "07",
        "agosto": "08", "setembro": "09", "outubro": "10",
        "novembro": "11", "dezembro": "12"
    }

    def __init__(self):
        super().__init__()
        self.config = SITES_MONITORADOS["folha_qconcursos"]

    def converter_data_por_extenso(self, texto: str) -> str:
        """Converte referências como '18 de novembro' ou '15/12/2026' para YYYY-MM-DD."""
        if not texto:
            return ""
        
        # Padrão DD/MM/AAAA ou DD/MM
        m_barra = re.search(r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?', texto)
        if m_barra:
            d, m = int(m_barra.group(1)), int(m_barra.group(2))
            ano = int(m_barra.group(3)) if m_barra.group(3) else date.today().year
            if ano < 100:
                ano += 2000
            try:
                return f"{ano:04d}-{m:02d}-{d:02d}"
            except ValueError:
                pass

        # Padrão "dia DD de MÊS"
        m_ext = re.search(r'(\d{1,2})\s+de\s+([a-zç]+)', texto.lower())
        if m_ext:
            d = int(m_ext.group(1))
            mes_nome = m_ext.group(2)
            if mes_nome in self.MESES:
                mes_num = self.MESES[mes_nome]
                ano = date.today().year
                return f"{ano:04d}-{mes_num}-{d:02d}"

        return ""

    def coletar_concursos(self) -> List[Dict[str, Any]]:
        """Acessa a matéria central de concursos abertos da Folha QConcursos e extrai os itens."""
        url = self.config["url"]
        base_url = self.config["base_url"]
        logger.info("Iniciando coleta em Folha QConcursos: %s", url)

        html = self.fetch_html(url)
        if not html:
            logger.warning("Falha ao carregar página de concursos da Folha QConcursos.")
            return []

        soup = BeautifulSoup(html, "html.parser")
        concursos = []

        # Localiza subtítulos que indicam concursos (h2 ou h3 contendo 'Concurso' ou 'PSS' ou 'Seleção')
        headings = soup.find_all(["h2", "h3"])
        logger.info("Folha QConcursos: %d títulos/cabeçalhos encontrados.", len(headings))

        for h in headings:
            h_text = h.get_text(strip=True)
            if not any(k in h_text.lower() for k in ["concurso", "pss", "seleção", "edital", "prefeitura"]):
                continue
            if any(k in h_text.lower() for k in ["menu", "sumário", "notícias", "comentários", "veja mais"]):
                continue

            # Agrupa os parágrafos subsequentes até o próximo h2/h3
            paragrafos = []
            links_item = []
            curr = h.find_next_sibling()
            while curr and curr.name not in ["h2", "h3"]:
                if curr.name in ["p", "ul", "ol", "div"]:
                    texto_p = curr.get_text(" ", strip=True)
                    if texto_p:
                        paragrafos.append(texto_p)
                    for a in curr.find_all("a"):
                        if a.get("href"):
                            links_item.append(urljoin(base_url, a.get("href")))
                curr = curr.find_next_sibling()

            bloco_texto = " ".join(paragrafos)
            if not bloco_texto:
                continue

            nome = h_text.replace("Concurso ", "").replace("PSS ", "").strip()
            orgao = nome.split("-")[0].strip()
            cargo = "Diversos Cargos"

            # Busca cargo no texto
            m_cargo = re.search(r'cargo(?:s)?\s+de\s+([a-zA-Záéíóúâêîôûãõç\s,]+?)(?:\.|,|\(|e conta|com)', bloco_texto, re.IGNORECASE)
            if m_cargo:
                cargo = m_cargo.group(1).strip()[:80]

            # Escolaridade
            escolaridade = self.normalizar_escolaridade(bloco_texto)

            # Vagas
            vagas = self.extrair_vagas(bloco_texto)

            # Salário
            salario = self.extrair_salario(bloco_texto)
            salario_texto = f"R$ {salario:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if salario > 0 else "A consultar"

            # Datas
            data_fim = ""
            m_insc = re.search(r'(?:inscriç(?:ões|ão)|recebe inscrições|até)\s+(?:o dia\s+)?([^\.]+?)(?:\.|\,)', bloco_texto, re.IGNORECASE)
            if m_insc:
                data_fim = self.converter_data_por_extenso(m_insc.group(1))

            # Banca
            banca = "A Definir"
            for b in ["Cebraspe", "FGV", "FCC", "Fundatec", "IBFC", "AOCP", "Vunesp", "Idecan", "Cesgranrio", "Fumarc"]:
                if b.lower() in bloco_texto.lower():
                    banca = b
                    break

            estado = self.inferir_estado(f"{h_text} {bloco_texto}")
            area = self.inferir_area(cargo, orgao)
            link_edital = links_item[0] if links_item else url

            item = {
                "nome": h_text[:150],
                "orgao": orgao[:150],
                "instituicao": banca,
                "cargo": cargo[:150],
                "escolaridade": escolaridade,
                "area_formacao": area,
                "salario": salario,
                "salario_texto": salario_texto,
                "vagas": vagas,
                "data_publicacao": str(date.today()),
                "data_inscricao_inicio": None,
                "data_inscricao_fim": data_fim if data_fim else None,
                "data_prova": None,
                "data_taxa_limite": None,
                "cidade": "Nacional / Diversas",
                "estado": estado,
                "link_edital": link_edital,
                "link_original": link_edital,
                "fonte": "Folha QConcursos",
                "situacao_edital": "Inscrições Abertas"
            }
            concursos.append(item)

        logger.info("Folha QConcursos: %d concursos extraídos com sucesso.", len(concursos))
        return concursos
