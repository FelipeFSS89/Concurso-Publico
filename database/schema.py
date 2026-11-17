"""
Definições de Schema DDL para SQLite
"""

SCHEMA_SQL = """
-- Tabela principal de Concursos Públicos
CREATE TABLE IF NOT EXISTS concursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hash_id TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    orgao TEXT NOT NULL,
    instituicao TEXT,
    cargo TEXT,
    escolaridade TEXT,
    area_formacao TEXT,
    salario REAL DEFAULT 0,
    salario_texto TEXT,
    vagas INTEGER DEFAULT 0,
    data_publicacao TEXT,
    data_inscricao_inicio TEXT,
    data_inscricao_fim TEXT,
    data_prova TEXT,
    data_taxa_limite TEXT,
    cidade TEXT,
    estado TEXT DEFAULT 'Nacional',
    link_edital TEXT,
    link_original TEXT,
    fonte TEXT,
    situacao_edital TEXT DEFAULT 'Inscrições Abertas',
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    atualizado_em TEXT DEFAULT (datetime('now', 'localtime'))
);

-- Tabela de Status do Usuário por Concurso
CREATE TABLE IF NOT EXISTS status_usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concurso_id INTEGER UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'Não analisado',
    proxima_acao TEXT,
    data_proxima_acao TEXT,
    acao_concluida INTEGER DEFAULT 0,
    atualizado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (concurso_id) REFERENCES concursos(id) ON DELETE CASCADE
);

-- Tabela de Favoritos
CREATE TABLE IF NOT EXISTS favoritos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concurso_id INTEGER UNIQUE NOT NULL,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (concurso_id) REFERENCES concursos(id) ON DELETE CASCADE
);

-- Tabela de Observações por Concurso
CREATE TABLE IF NOT EXISTS observacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concurso_id INTEGER NOT NULL,
    texto TEXT NOT NULL,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (concurso_id) REFERENCES concursos(id) ON DELETE CASCADE
);

-- Tabela de Histórico de Alterações de Status
CREATE TABLE IF NOT EXISTS historico_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concurso_id INTEGER NOT NULL,
    status_anterior TEXT,
    status_novo TEXT NOT NULL,
    motivo_observacao TEXT,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (concurso_id) REFERENCES concursos(id) ON DELETE CASCADE
);

-- Tabela de Alertas (Vermelho, Amarelo, Verde, Azul)
CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concurso_id INTEGER,
    tipo TEXT NOT NULL, -- urgente, atencao, novidade, info
    titulo TEXT NOT NULL,
    mensagem TEXT NOT NULL,
    data_referencia TEXT,
    lido INTEGER DEFAULT 0,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (concurso_id) REFERENCES concursos(id) ON DELETE SET NULL
);

-- Tabela de Formações e Áreas de Interesse do Usuário
CREATE TABLE IF NOT EXISTS formacoes_interesse (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    palavras_chave TEXT,
    ativo INTEGER DEFAULT 1,
    criado_em TEXT DEFAULT (datetime('now', 'localtime'))
);

-- Tabela de Configurações do Sistema
CREATE TABLE IF NOT EXISTS configuracoes (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL,
    atualizado_em TEXT DEFAULT (datetime('now', 'localtime'))
);

-- Índices para otimização de consultas
CREATE INDEX IF NOT EXISTS idx_concursos_estado ON concursos(estado);
CREATE INDEX IF NOT EXISTS idx_concursos_escolaridade ON concursos(escolaridade);
CREATE INDEX IF NOT EXISTS idx_concursos_inscricao_fim ON concursos(data_inscricao_fim);
CREATE INDEX IF NOT EXISTS idx_concursos_prova ON concursos(data_prova);
CREATE INDEX IF NOT EXISTS idx_status_usuario_status ON status_usuario(status);
CREATE INDEX IF NOT EXISTS idx_alertas_tipo ON alertas(tipo);
CREATE INDEX IF NOT EXISTS idx_alertas_lido ON alertas(lido);
"""
