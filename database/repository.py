"""
Repositórios de Dados para Operações no SQLite
"""
import sqlite3
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from database.connection import get_connection

class ConcursoRepository:
    """Gerencia operações da tabela de concursos e suas relações."""

    @staticmethod
    def gerar_hash(nome: str, orgao: str, cargo: str = "") -> str:
        """Gera um hash único e estável para identificar um concurso e evitar duplicidades."""
        raw = f"{nome.strip().lower()}|{orgao.strip().lower()}|{cargo.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def inserir_concurso(cls, dados: Dict[str, Any]) -> Tuple[int, bool]:
        """
        Insere ou atualiza um concurso.
        Retorna (id, is_novo): is_novo é True se foi inserido um novo registro.
        """
        hash_id = dados.get("hash_id") or cls.gerar_hash(
            dados.get("nome", ""),
            dados.get("orgao", ""),
            dados.get("cargo", "")
        )

        conn = get_connection()
        try:
            with conn:
                # Verificar se já existe pelo hash_id
                cur = conn.execute("SELECT id FROM concursos WHERE hash_id = ?", (hash_id,))
                row = cur.fetchone()

                if row:
                    concurso_id = row["id"]
                    # Atualiza informações que possam ter mudado (ex: edital publicado, datas)
                    conn.execute("""
                        UPDATE concursos SET
                            instituicao = COALESCE(?, instituicao),
                            cargo = COALESCE(?, cargo),
                            escolaridade = COALESCE(?, escolaridade),
                            area_formacao = COALESCE(?, area_formacao),
                            salario = CASE WHEN ? > 0 THEN ? ELSE salario END,
                            salario_texto = COALESCE(?, salario_texto),
                            vagas = CASE WHEN ? > 0 THEN ? ELSE vagas END,
                            data_inscricao_inicio = COALESCE(?, data_inscricao_inicio),
                            data_inscricao_fim = COALESCE(?, data_inscricao_fim),
                            data_prova = COALESCE(?, data_prova),
                            data_taxa_limite = COALESCE(?, data_taxa_limite),
                            cidade = COALESCE(?, cidade),
                            estado = COALESCE(?, estado),
                            link_edital = COALESCE(?, link_edital),
                            link_original = COALESCE(?, link_original),
                            fonte = COALESCE(?, fonte),
                            situacao_edital = COALESCE(?, situacao_edital),
                            atualizado_em = datetime('now', 'localtime')
                        WHERE id = ?
                    """, (
                        dados.get("instituicao"),
                        dados.get("cargo"),
                        dados.get("escolaridade"),
                        dados.get("area_formacao"),
                        dados.get("salario", 0), dados.get("salario", 0),
                        dados.get("salario_texto"),
                        dados.get("vagas", 0), dados.get("vagas", 0),
                        dados.get("data_inscricao_inicio"),
                        dados.get("data_inscricao_fim"),
                        dados.get("data_prova"),
                        dados.get("data_taxa_limite"),
                        dados.get("cidade"),
                        dados.get("estado"),
                        dados.get("link_edital"),
                        dados.get("link_original"),
                        dados.get("fonte"),
                        dados.get("situacao_edital"),
                        concurso_id
                    ))
                    return concurso_id, False
                else:
                    cur = conn.execute("""
                        INSERT INTO concursos (
                            hash_id, nome, orgao, instituicao, cargo, escolaridade,
                            area_formacao, salario, salario_texto, vagas, data_publicacao,
                            data_inscricao_inicio, data_inscricao_fim, data_prova,
                            data_taxa_limite, cidade, estado, link_edital, link_original,
                            fonte, situacao_edital
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        hash_id,
                        dados.get("nome", "Sem Nome"),
                        dados.get("orgao", "Não Informado"),
                        dados.get("instituicao", "A Definir"),
                        dados.get("cargo", "Diversos"),
                        dados.get("escolaridade", "Médio"),
                        dados.get("area_formacao", "Geral"),
                        dados.get("salario", 0.0),
                        dados.get("salario_texto", "A consultar"),
                        dados.get("vagas", 0),
                        dados.get("data_publicacao", str(date.today())),
                        dados.get("data_inscricao_inicio"),
                        dados.get("data_inscricao_fim"),
                        dados.get("data_prova"),
                        dados.get("data_taxa_limite"),
                        dados.get("cidade", "Várias"),
                        dados.get("estado", "Nacional"),
                        dados.get("link_edital"),
                        dados.get("link_original"),
                        dados.get("fonte", "Web"),
                        dados.get("situacao_edital", "Inscrições Abertas")
                    ))
                    novo_id = cur.lastrowid
                    
                    # Cria automaticamente registro inicial em status_usuario
                    conn.execute("""
                        INSERT INTO status_usuario (concurso_id, status)
                        VALUES (?, 'Não analisado')
                    """, (novo_id,))

                    return novo_id, True
        finally:
            conn.close()

    @classmethod
    def buscar_concursos(cls, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Busca concursos aplicando múltiplos filtros combinados."""
        filtros = filtros or {}
        sql = """
            SELECT 
                c.*,
                COALESCE(su.status, 'Não analisado') as status_usuario,
                su.proxima_acao,
                su.data_proxima_acao,
                su.acao_concluida,
                CASE WHEN f.id IS NOT NULL THEN 1 ELSE 0 END as is_favorito,
                (SELECT COUNT(*) FROM observacoes o WHERE o.concurso_id = c.id) as total_observacoes
            FROM concursos c
            LEFT JOIN status_usuario su ON su.concurso_id = c.id
            LEFT JOIN favoritos f ON f.concurso_id = c.id
            WHERE 1=1
        """
        params = []

        # Palavra-chave (nome, órgão, cargo, formação)
        if filtros.get("busca"):
            termo = f"%{filtros['busca'].strip()}%"
            sql += " AND (c.nome LIKE ? OR c.orgao LIKE ? OR c.cargo LIKE ? OR c.area_formacao LIKE ? OR c.instituicao LIKE ?)"
            params.extend([termo, termo, termo, termo, termo])

        # Órgão
        if filtros.get("orgao"):
            sql += " AND c.orgao LIKE ?"
            params.append(f"%{filtros['orgao'].strip()}%")

        # Cargo
        if filtros.get("cargo"):
            sql += " AND c.cargo LIKE ?"
            params.append(f"%{filtros['cargo'].strip()}%")

        # Escolaridade
        if filtros.get("escolaridade") and filtros["escolaridade"] != "Todas":
            sql += " AND c.escolaridade = ?"
            params.append(filtros["escolaridade"])

        # Área de Formação
        if filtros.get("area_formacao") and filtros["area_formacao"] != "Todas":
            sql += " AND (c.area_formacao LIKE ? OR c.cargo LIKE ?)"
            params.extend([f"%{filtros['area_formacao']}%", f"%{filtros['area_formacao']}%"])

        # Estado / UF
        if filtros.get("estado") and filtros["estado"] != "Todos":
            sql += " AND c.estado = ?"
            params.append(filtros["estado"])

        # Faixa Salarial Mínima
        if filtros.get("salario_min") is not None and filtros["salario_min"] > 0:
            sql += " AND c.salario >= ?"
            params.append(filtros["salario_min"])

        # Status do Usuário
        if filtros.get("status_usuario") and filtros["status_usuario"] != "Todos":
            sql += " AND COALESCE(su.status, 'Não analisado') = ?"
            params.append(filtros["status_usuario"])

        # Apenas Favoritos
        if filtros.get("apenas_favoritos"):
            sql += " AND f.id IS NOT NULL"

        # Apenas Inscrições Abertas (data_fim >= hoje ou sem data)
        if filtros.get("apenas_abertos"):
            hoje = date.today().isoformat()
            sql += " AND (c.data_inscricao_fim IS NULL OR c.data_inscricao_fim >= ?)"
            params.append(hoje)

        # Ordenação
        ordem = filtros.get("ordenacao", "recente")
        if ordem == "recente":
            sql += " ORDER BY c.id DESC"
        elif ordem == "prazo_inscricao":
            sql += " ORDER BY CASE WHEN c.data_inscricao_fim IS NULL THEN 1 ELSE 0 END, c.data_inscricao_fim ASC"
        elif ordem == "data_prova":
            sql += " ORDER BY CASE WHEN c.data_prova IS NULL THEN 1 ELSE 0 END, c.data_prova ASC"
        elif ordem == "maior_salario":
            sql += " ORDER BY c.salario DESC"
        elif ordem == "mais_vagas":
            sql += " ORDER BY c.vagas DESC"
        else:
            sql += " ORDER BY c.id DESC"

        conn = get_connection()
        try:
            cur = conn.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    @classmethod
    def buscar_por_id(cls, concurso_id: int) -> Optional[Dict[str, Any]]:
        """Busca um concurso completo pelo ID com seus metadados relacionados."""
        conn = get_connection()
        try:
            sql = """
                SELECT 
                    c.*,
                    COALESCE(su.status, 'Não analisado') as status_usuario,
                    su.proxima_acao,
                    su.data_proxima_acao,
                    su.acao_concluida,
                    CASE WHEN f.id IS NOT NULL THEN 1 ELSE 0 END as is_favorito
                FROM concursos c
                LEFT JOIN status_usuario su ON su.concurso_id = c.id
                LEFT JOIN favoritos f ON f.concurso_id = c.id
                WHERE c.id = ?
            """
            cur = conn.execute(sql, (concurso_id,))
            row = cur.fetchone()
            if not row:
                return None
            res = dict(row)
            
            # Buscar observações
            cur_obs = conn.execute(
                "SELECT id, texto, criado_em FROM observacoes WHERE concurso_id = ? ORDER BY id DESC", 
                (concurso_id,)
            )
            res["observacoes"] = [dict(r) for r in cur_obs.fetchall()]

            # Buscar histórico de status
            cur_hist = conn.execute(
                "SELECT status_anterior, status_novo, motivo_observacao, criado_em FROM historico_status WHERE concurso_id = ? ORDER BY id DESC",
                (concurso_id,)
            )
            res["historico_status"] = [dict(r) for r in cur_hist.fetchall()]

            return res
        finally:
            conn.close()

    @classmethod
    def atualizar_status_usuario(cls, concurso_id: int, novo_status: str, observacao: str = "") -> bool:
        """Atualiza o status do usuário para o concurso e registra no histórico."""
        conn = get_connection()
        try:
            with conn:
                cur = conn.execute("SELECT status FROM status_usuario WHERE concurso_id = ?", (concurso_id,))
                row = cur.fetchone()
                status_anterior = row["status"] if row else "Não analisado"

                if status_anterior != novo_status or observacao:
                    # Atualiza ou insere status_usuario
                    conn.execute("""
                        INSERT INTO status_usuario (concurso_id, status, atualizado_em)
                        VALUES (?, ?, datetime('now', 'localtime'))
                        ON CONFLICT(concurso_id) DO UPDATE SET
                            status = excluded.status,
                            atualizado_em = datetime('now', 'localtime')
                    """, (concurso_id, novo_status))

                    # Registra histórico
                    conn.execute("""
                        INSERT INTO historico_status (concurso_id, status_anterior, status_novo, motivo_observacao)
                        VALUES (?, ?, ?, ?)
                    """, (concurso_id, status_anterior, novo_status, observacao))

                    # Se foi fornecida observação, salva também na tabela de observações
                    if observacao.strip():
                        conn.execute("""
                            INSERT INTO observacoes (concurso_id, texto)
                            VALUES (?, ?)
                        """, (concurso_id, f"Status alterado para '{novo_status}': {observacao.strip()}"))

                return True
        finally:
            conn.close()

    @classmethod
    def definir_proxima_acao(cls, concurso_id: int, acao: str, data_limite: Optional[str] = None, concluida: bool = False) -> bool:
        """Define ou atualiza a próxima ação para um concurso."""
        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO status_usuario (concurso_id, proxima_acao, data_proxima_acao, acao_concluida, atualizado_em)
                    VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
                    ON CONFLICT(concurso_id) DO UPDATE SET
                        proxima_acao = excluded.proxima_acao,
                        data_proxima_acao = excluded.data_proxima_acao,
                        acao_concluida = excluded.acao_concluida,
                        atualizado_em = datetime('now', 'localtime')
                """, (concurso_id, acao, data_limite, 1 if concluida else 0))
            return True
        finally:
            conn.close()

    @classmethod
    def alternar_favorito(cls, concurso_id: int) -> bool:
        """Alterna o status de favorito (adiciona se não existir, remove se existir). Retorna True se agora é favorito."""
        conn = get_connection()
        try:
            with conn:
                cur = conn.execute("SELECT id FROM favoritos WHERE concurso_id = ?", (concurso_id,))
                row = cur.fetchone()
                if row:
                    conn.execute("DELETE FROM favoritos WHERE concurso_id = ?", (concurso_id,))
                    return False
                else:
                    conn.execute("INSERT INTO favoritos (concurso_id) VALUES (?)", (concurso_id,))
                    return True
        finally:
            conn.close()

    @classmethod
    def adicionar_observacao(cls, concurso_id: int, texto: str) -> bool:
        """Adiciona uma observação ao concurso com data e hora."""
        if not texto.strip():
            return False
        conn = get_connection()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO observacoes (concurso_id, texto) VALUES (?, ?)",
                    (concurso_id, texto.strip())
                )
            return True
        finally:
            conn.close()

    @classmethod
    def obter_estatisticas_gerais(cls) -> Dict[str, Any]:
        """Calcula totais consolidados para os cards e KPIs do Dashboard."""
        conn = get_connection()
        try:
            hoje = date.today().isoformat()
            
            # Totais básicos
            total_concursos = conn.execute("SELECT COUNT(*) FROM concursos").fetchone()[0]
            total_favoritos = conn.execute("SELECT COUNT(*) FROM favoritos").fetchone()[0]
            
            # Monitorados (qualquer status diferente de 'Não analisado' e 'Não interessado')
            cur_mon = conn.execute("""
                SELECT COUNT(*) FROM status_usuario 
                WHERE status NOT IN ('Não analisado', 'Não interessado')
            """)
            total_monitorados = cur_mon.fetchone()[0]

            # Inscrições realizadas ('Inscrito', 'Taxa paga', 'Aguardando prova', 'Realizou prova', 'Aprovado', 'Reprovado')
            cur_insc = conn.execute("""
                SELECT COUNT(*) FROM status_usuario 
                WHERE status IN ('Inscrito', 'Taxa paga', 'Aguardando prova', 'Realizou prova', 'Aprovado')
            """)
            total_inscricoes = cur_insc.fetchone()[0]

            # Em estudo ('Estudando')
            cur_est = conn.execute("SELECT COUNT(*) FROM status_usuario WHERE status = 'Estudando'")
            total_estudo = cur_est.fetchone()[0]

            # Próximos vencimentos de inscrição (nos próximos 15 dias)
            cur_venc = conn.execute("""
                SELECT c.id, c.nome, c.orgao, c.data_inscricao_fim, c.salario, c.estado
                FROM concursos c
                WHERE c.data_inscricao_fim >= ? 
                ORDER BY c.data_inscricao_fim ASC
                LIMIT 5
            """, (hoje,))
            proximos_vencimentos = [dict(r) for r in cur_venc.fetchall()]

            # Próximas provas (a partir de hoje)
            cur_prov = conn.execute("""
                SELECT c.id, c.nome, c.orgao, c.data_prova, c.salario, c.estado, c.cargo
                FROM concursos c
                WHERE c.data_prova >= ?
                ORDER BY c.data_prova ASC
                LIMIT 5
            """, (hoje,))
            proximas_provas = [dict(r) for r in cur_prov.fetchall()]

            # Próximas ações pendentes
            cur_acoes = conn.execute("""
                SELECT c.id, c.nome, c.orgao, su.proxima_acao, su.data_proxima_acao, su.status
                FROM status_usuario su
                JOIN concursos c ON c.id = su.concurso_id
                WHERE su.proxima_acao IS NOT NULL AND su.proxima_acao != '' AND su.acao_concluida = 0
                ORDER BY CASE WHEN su.data_proxima_acao IS NULL THEN 1 ELSE 0 END, su.data_proxima_acao ASC
                LIMIT 6
            """)
            proximas_acoes = [dict(r) for r in cur_acoes.fetchall()]

            return {
                "total_concursos": total_concursos,
                "total_monitorados": total_monitorados,
                "total_favoritos": total_favoritos,
                "total_inscricoes": total_inscricoes,
                "total_estudo": total_estudo,
                "proximos_vencimentos": proximos_vencimentos,
                "proximas_provas": proximas_provas,
                "proximas_acoes": proximas_acoes
            }
        finally:
            conn.close()

    @classmethod
    def obter_dados_graficos(cls) -> Dict[str, Any]:
        """Obtém dados estruturados para renderização de gráficos Plotly."""
        conn = get_connection()
        try:
            # 1. Concursos por Status do Usuário
            cur_status = conn.execute("""
                SELECT COALESCE(su.status, 'Não analisado') as status, COUNT(*) as qtd
                FROM concursos c
                LEFT JOIN status_usuario su ON su.concurso_id = c.id
                GROUP BY COALESCE(su.status, 'Não analisado')
                ORDER BY qtd DESC
            """)
            status_data = [dict(r) for r in cur_status.fetchall()]

            # 2. Concursos por Estado (UF)
            cur_uf = conn.execute("""
                SELECT estado, COUNT(*) as qtd
                FROM concursos
                GROUP BY estado
                ORDER BY qtd DESC
                LIMIT 15
            """)
            uf_data = [dict(r) for r in cur_uf.fetchall()]

            # 3. Concursos por Escolaridade
            cur_esc = conn.execute("""
                SELECT escolaridade, COUNT(*) as qtd
                FROM concursos
                GROUP BY escolaridade
                ORDER BY qtd DESC
            """)
            escolaridade_data = [dict(r) for r in cur_esc.fetchall()]

            # 4. Distribuição Salarial
            cur_sal = conn.execute("""
                SELECT 
                    CASE 
                        WHEN salario <= 0 THEN 'A consultar'
                        WHEN salario <= 3000 THEN 'Até R$ 3.000'
                        WHEN salario <= 6000 THEN 'R$ 3.001 - R$ 6.000'
                        WHEN salario <= 10000 THEN 'R$ 6.001 - R$ 10.000'
                        WHEN salario <= 15000 THEN 'R$ 10.001 - R$ 15.000'
                        ELSE 'Acima de R$ 15.000'
                    END as faixa,
                    COUNT(*) as qtd
                FROM concursos
                GROUP BY faixa
                ORDER BY MIN(salario) ASC
            """)
            faixa_salarios = [dict(r) for r in cur_sal.fetchall()]

            # 5. Evolução de inserção / monitoramento por data
            cur_evo = conn.execute("""
                SELECT substr(criado_em, 1, 10) as dia, COUNT(*) as cadastrados
                FROM concursos
                GROUP BY dia
                ORDER BY dia ASC
                LIMIT 30
            """)
            evolucao_data = [dict(r) for r in cur_evo.fetchall()]

            return {
                "status": status_data,
                "estados": uf_data,
                "escolaridade": escolaridade_data,
                "salarios": faixa_salarios,
                "evolucao": evolucao_data
            }
        finally:
            conn.close()


class AlertaRepository:
    """Gerencia a central de alertas persistente."""

    @staticmethod
    def salvar_alerta(tipo: str, titulo: str, mensagem: str, concurso_id: Optional[int] = None, data_referencia: Optional[str] = None):
        """Salva um alerta evitando duplicatas ativas não lidas."""
        conn = get_connection()
        try:
            with conn:
                # Evita recriar exatamente o mesmo alerta não lido
                cur = conn.execute("""
                    SELECT id FROM alertas 
                    WHERE tipo = ? AND titulo = ? AND concurso_id IS ? AND lido = 0
                """, (tipo, titulo, concurso_id))
                if not cur.fetchone():
                    conn.execute("""
                        INSERT INTO alertas (tipo, titulo, mensagem, concurso_id, data_referencia, lido)
                        VALUES (?, ?, ?, ?, ?, 0)
                    """, (tipo, titulo, mensagem, concurso_id, data_referencia))
        finally:
            conn.close()

    @staticmethod
    def listar_alertas(apenas_nao_lidos: bool = False, tipo: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lista alertas salvos no banco com filtros opcionais."""
        conn = get_connection()
        try:
            sql = """
                SELECT a.*, c.nome as concurso_nome, c.orgao as concurso_orgao
                FROM alertas a
                LEFT JOIN concursos c ON c.id = a.concurso_id
                WHERE 1=1
            """
            params = []
            if apenas_nao_lidos:
                sql += " AND a.lido = 0"
            if tipo and tipo != "todos":
                sql += " AND a.tipo = ?"
                params.append(tipo)
            
            sql += " ORDER BY a.id DESC LIMIT 100"
            cur = conn.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def marcar_como_lido(alerta_id: int):
        conn = get_connection()
        try:
            with conn:
                conn.execute("UPDATE alertas SET lido = 1 WHERE id = ?", (alerta_id,))
        finally:
            conn.close()

    @staticmethod
    def marcar_todos_como_lidos():
        conn = get_connection()
        try:
            with conn:
                conn.execute("UPDATE alertas SET lido = 1")
        finally:
            conn.close()

    @staticmethod
    def limpar_alertas_lidos():
        conn = get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM alertas WHERE lido = 1")
        finally:
            conn.close()


class ConfiguracaoRepository:
    """Gerencia preferências e formações de interesse."""

    @staticmethod
    def obter(chave: str, padrao: str = "") -> str:
        conn = get_connection()
        try:
            cur = conn.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
            row = cur.fetchone()
            return row["valor"] if row else padrao
        finally:
            conn.close()

    @staticmethod
    def salvar(chave: str, valor: str):
        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO configuracoes (chave, valor, atualizado_em)
                    VALUES (?, ?, datetime('now', 'localtime'))
                    ON CONFLICT(chave) DO UPDATE SET
                        valor = excluded.valor,
                        atualizado_em = datetime('now', 'localtime')
                """, (chave, valor))
        finally:
            conn.close()

    @staticmethod
    def obter_todas() -> Dict[str, str]:
        conn = get_connection()
        try:
            cur = conn.execute("SELECT chave, valor FROM configuracoes")
            return {row["chave"]: row["valor"] for row in cur.fetchall()}
        finally:
            conn.close()

    @staticmethod
    def listar_formacoes() -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            cur = conn.execute("SELECT id, nome, palavras_chave, ativo FROM formacoes_interesse ORDER BY nome ASC")
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def adicionar_formacao(nome: str, palavras_chave: str = "") -> bool:
        if not nome.strip():
            return False
        conn = get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR IGNORE INTO formacoes_interesse (nome, palavras_chave, ativo)
                    VALUES (?, ?, 1)
                """, (nome.strip(), palavras_chave.strip()))
            return True
        finally:
            conn.close()

    @staticmethod
    def remover_formacao(formacao_id: int):
        conn = get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM formacoes_interesse WHERE id = ?", (formacao_id,))
        finally:
            conn.close()
