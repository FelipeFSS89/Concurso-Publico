"""
Gerenciador de Conexão com SQLite
"""
import sqlite3
import logging
from config import DB_PATH, AREAS_FORMACAO_SUGESTOES
from database.schema import SCHEMA_SQL

logger = logging.getLogger(__name__)

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão ativa com o banco SQLite configurado."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db():
    """Inicializa as tabelas do banco de dados e dados padrão se não existirem."""
    conn = get_connection()
    try:
        with conn:
            conn.executescript(SCHEMA_SQL)
            
            # Inserir configurações padrão caso não existam
            config_padrao = [
                ("atualizacao_automatica", "true"),
                ("intervalo_horas", "6"),
                ("horario_verificacao", "08:00"),
                ("estados_interesse", "RJ, SP, DF, Nacional"),
                ("salario_minimo", "3000"),
                ("vagas_minimas", "1"),
                ("notificacoes_email", "false"),
                ("notificacoes_telegram", "false"),
                ("notificacoes_whatsapp", "false"),
                ("ultimo_scraping", "")
            ]
            
            for chave, valor in config_padrao:
                conn.execute(
                    "INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES (?, ?)",
                    (chave, valor)
                )
                
            # Inserir algumas formações padrão sugeridas se tabela estiver vazia
            cur = conn.execute("SELECT COUNT(*) as count FROM formacoes_interesse")
            if cur.fetchone()["count"] == 0:
                padroes = [
                    ("Administração", "administrador, administração, adm, gestão pública"),
                    ("Direito", "direito, jurídico, analista judiciário, técnico judiciário, procurador, delegado"),
                    ("Ciências Contábeis", "contabilidade, contábil, contador, auditoria"),
                    ("Tecnologia da Informação", "ti, informática, desenvolvimento, sistemas, redes, dados, computação"),
                    ("Ensino Médio", "nível médio, médio, técnico administrativo, agente administrativo, assistente")
                ]
                for nome, kw in padroes:
                    conn.execute(
                        "INSERT OR IGNORE INTO formacoes_interesse (nome, palavras_chave) VALUES (?, ?)",
                        (nome, kw)
                    )
        logger.info("Banco de dados SQLite inicializado com sucesso em %s", DB_PATH)
    except Exception as e:
        logger.error("Erro ao inicializar o banco de dados: %s", e)
        raise e
    finally:
        conn.close()
