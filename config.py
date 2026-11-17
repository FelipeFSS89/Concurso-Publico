"""
Configurações Globais do Painel de Concursos
"""
import os
from pathlib import Path

# Caminhos base
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Banco de dados SQLite persistente
DB_PATH = DATA_DIR / "concursos.db"

# Status do usuário para cada concurso
STATUS_USUARIO_LISTA = [
    "Não analisado",
    "Interessado",
    "Avaliando",
    "Estudando",
    "Inscrito",
    "Taxa paga",
    "Aguardando prova",
    "Realizou prova",
    "Aprovado",
    "Reprovado",
    "Não interessado",
    "Encerrado"
]

# Cores e Ícones de Status
STATUS_CONFIG = {
    "Não analisado": {"color": "#64748B", "icon": "fa-regular fa-circle-question", "badge": "secondary"},
    "Interessado": {"color": "#3B82F6", "icon": "fa-solid fa-star", "badge": "primary"},
    "Avaliando": {"color": "#6366F1", "icon": "fa-solid fa-magnifying-glass", "badge": "info"},
    "Estudando": {"color": "#8B5CF6", "icon": "fa-solid fa-book-open", "badge": "purple"},
    "Inscrito": {"color": "#F59E0B", "icon": "fa-solid fa-clipboard-check", "badge": "warning"},
    "Taxa paga": {"color": "#10B981", "icon": "fa-solid fa-receipt", "badge": "teal"},
    "Aguardando prova": {"color": "#06B6D4", "icon": "fa-solid fa-hourglass-half", "badge": "cyan"},
    "Realizou prova": {"color": "#475569", "icon": "fa-solid fa-pen-nib", "badge": "dark"},
    "Aprovado": {"color": "#22C55E", "icon": "fa-solid fa-trophy", "badge": "success"},
    "Reprovado": {"color": "#EF4444", "icon": "fa-solid fa-xmark", "badge": "danger"},
    "Não interessado": {"color": "#94A3B8", "icon": "fa-solid fa-ban", "badge": "light"},
    "Encerrado": {"color": "#334155", "icon": "fa-solid fa-lock", "badge": "secondary"}
}

# Níveis de escolaridade padrão
ESCOLARIDADE_LISTA = [
    "Fundamental",
    "Médio",
    "Técnico",
    "Superior",
    "Pós-Graduação"
]

# Áreas de formação comuns
AREAS_FORMACAO_SUGESTOES = [
    "Administração",
    "Direito",
    "Ciências Contábeis",
    "Engenharia",
    "Pedagogia",
    "Tecnologia da Informação",
    "Ensino Médio",
    "Saúde / Enfermagem / Medicina",
    "Segurança Pública / Policial",
    "Fiscal / Tributária",
    "Bancária / Financeira",
    "Educação",
    "Qualquer Área"
]

# Estados Brasileiros (UF)
ESTADOS_BRASIL = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", 
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO", "Nacional"
]

# URLs dos sites monitorados
SITES_MONITORADOS = {
    "degrau_cultural": {
        "nome": "Degrau Cultural",
        "url": "https://degraucultural.com.br/concursos",
        "base_url": "https://degraucultural.com.br"
    },
    "folha_qconcursos": {
        "nome": "Folha QConcursos",
        "url": "https://folha.qconcursos.com/n/concursos-publicos-abertos",
        "base_url": "https://folha.qconcursos.com"
    }
}
