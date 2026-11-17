"""
Classe Base e Utilitários de Limpeza para Scrapers de Concursos
"""
import re
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import requests

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Classe base para os scrapers de portais de concursos."""

    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    def fetch_html(self, url: str) -> Optional[str]:
        """Faz requisição HTTP com tratamento de erros e retorno de texto."""
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                return resp.text
            logger.warning("Falha ao acessar %s: Status %d", url, resp.status_code)
            return None
        except Exception as e:
            logger.error("Erro de conexão ao acessar %s: %s", url, e)
            return None

    @abstractmethod
    def coletar_concursos(self) -> List[Dict[str, Any]]:
        """Método obrigatório implementado por cada scraper específico."""
        pass

    @staticmethod
    def extrair_salario(texto: str) -> float:
        """Extrai valor numérico de expressões salariais como 'R$ 12.500,50' ou 'R$ 10 mil'."""
        if not texto:
            return 0.0
        
        # Caso especial "R$ X mil"
        match_mil = re.search(r'R\$\s*([\d,.]+)\s*mil', texto, re.IGNORECASE)
        if match_mil:
            val_str = match_mil.group(1).replace(".", "").replace(",", ".")
            try:
                return float(val_str) * 1000.0
            except ValueError:
                pass

        # Expressões monetárias gerais
        matches = re.findall(r'R\$\s*([\d]{1,3}(?:\.[\d]{3})*(?:,[\d]{2})?)', texto)
        if matches:
            # Pega o maior valor encontrado no trecho
            valores = []
            for m in matches:
                limpo = m.replace(".", "").replace(",", ".")
                try:
                    valores.append(float(limpo))
                except ValueError:
                    continue
            if valores:
                return max(valores)
        
        # Procura números soltos com padrão monetário
        m_num = re.search(r'([\d]{1,3}(?:\.[\d]{3})+,[\d]{2})', texto)
        if m_num:
            try:
                return float(m_num.group(1).replace(".", "").replace(",", "."))
            except ValueError:
                pass

        return 0.0

    @staticmethod
    def extrair_vagas(texto: str) -> int:
        """Extrai quantidade inteira de vagas a partir do texto."""
        if not texto:
            return 0
        if "cr" in texto.lower() or "cadastro de reserva" in texto.lower():
            return 1 # Cadastro de reserva conta como oportunidade
            
        m = re.search(r'([\d.]+)\s*(?:vagas?|oportunidades?)', texto, re.IGNORECASE)
        if m:
            val_str = m.group(1).replace(".", "")
            try:
                return int(val_str)
            except ValueError:
                pass
                
        # Procura dígitos isolados perto da palavra vaga
        m2 = re.search(r'vagas?:\s*([\d.]+)', texto, re.IGNORECASE)
        if m2:
            val_str = m2.group(1).replace(".", "")
            try:
                return int(val_str)
            except ValueError:
                pass

        return 0

    @staticmethod
    def normalizar_escolaridade(texto: str) -> str:
        """Classifica o nível de escolaridade padrão."""
        if not texto:
            return "Médio"
        t = texto.lower()
        if "pós" in t or "doutorado" in t or "mestrado" in t:
            return "Pós-Graduação"
        if "superior" in t or "graduação" in t or "bacharel" in t or "licenciatura" in t:
            return "Superior"
        if "técnico" in t or "tecnólogo" in t:
            return "Técnico"
        if "médio" in t or "ensino médio" in t:
            return "Médio"
        if "fundamental" in t:
            return "Fundamental"
        return "Médio"

    @staticmethod
    def inferir_area(cargo: str, orgao: str) -> str:
        """Infere a área de formação ou atuação a partir do cargo e órgão."""
        t = f"{cargo} {orgao}".lower()
        if any(k in t for k in ["ti", "tecnologia", "informática", "desenvolvedor", "sistemas", "redes", "dados", "computação"]):
            return "Tecnologia da Informação"
        if any(k in t for k in ["polícia", "policial", "militar", "segurança", "guarda", "penal", "agente de segurança", "soldado", "delegado"]):
            return "Segurança Pública / Policial"
        if any(k in t for k in ["tribunal", "judiciário", "juiz", "procurador", "advogado", "jurídico", "defensor", "promotor", "direito"]):
            return "Direito"
        if any(k in t for k in ["auditor", "fiscal", "receita", "tribut", "contábil", "contabilidade", "contador", "ciências contábeis"]):
            return "Fiscal / Tributária"
        if any(k in t for k in ["banco", "bancário", "caixa", "bacen", "financeiro", "crédito"]):
            return "Bancária / Financeira"
        if any(k in t for k in ["médico", "saúde", "enfermeir", "hospital", "sus", "biomed", "farmacêut"]):
            return "Saúde / Enfermagem / Medicina"
        if any(k in t for k in ["professor", "educação", "pedagogo", "pedagogia", "ensino", "docente", "seduc", "escola"]):
            return "Educação / Pedagogia"
        if any(k in t for k in ["engenheiro", "engenharia", "arquiteto", "urbanismo"]):
            return "Engenharia"
        if any(k in t for k in ["administrador", "administração", "adm", "gestão", "assistente administrativo", "técnico administrativo"]):
            return "Administração"
        if "médio" in t:
            return "Ensino Médio"
        return "Geral / Diversas"

    @staticmethod
    def inferir_estado(texto: str) -> str:
        """Infere a UF do concurso baseada no texto."""
        estados = {
            "rio de janeiro": "RJ", "rj": "RJ",
            "são paulo": "SP", "sp": "SP",
            "distrito federal": "DF", "brasília": "DF", "df": "DF",
            "minas gerais": "MG", "mg": "MG",
            "bahia": "BA", "ba": "BA",
            "paraná": "PR", "pr": "PR",
            "rio grande do sul": "RS", "rs": "RS",
            "pernambuco": "PE", "pe": "PE",
            "ceará": "CE", "ce": "CE",
            "santa catarina": "SC", "sc": "SC",
            "goiás": "GO", "go": "GO",
            "maranhão": "MA", "ma": "MA",
            "paraíba": "PB", "pb": "PB",
            "espírito santo": "ES", "es": "ES",
            "amazonas": "AM", "am": "AM",
            "pará": "PA", "pa": "PA",
            "alagoas": "AL", "al": "AL",
            "mato grosso do sul": "MS", "ms": "MS",
            "mato grosso": "MT", "mt": "MT",
            "piauí": "PI", "pi": "PI",
            "rio grande do norte": "RN", "rn": "RN",
            "sergipe": "SE", "se": "SE",
            "rondônia": "RO", "ro": "RO",
            "tocantins": "TO", "to": "TO",
            "acre": "AC", "ac": "AC",
            "amapá": "AP", "ap": "AP",
            "roraima": "RR", "rr": "RR",
            "nacional": "Nacional", "federal": "Nacional", "brasil": "Nacional"
        }
        t = texto.lower()
        for nome_uf, sigla in estados.items():
            # Palavra delimitada por bordas
            if re.search(r'\b' + re.escape(nome_uf) + r'\b', t):
                return sigla
        return "Nacional"
