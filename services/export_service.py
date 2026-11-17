"""
Serviço de Exportação de Dados para Excel (.xlsx) e CSV (.csv)
"""
import io
import pandas as pd
from typing import List, Dict, Any

class ExportService:
    """Gera arquivos formatados para download."""

    COLUNAS_MAPEAMENTO = {
        "nome": "Nome do Concurso",
        "orgao": "Órgão",
        "instituicao": "Banca / Instituição",
        "cargo": "Cargo",
        "escolaridade": "Escolaridade",
        "area_formacao": "Área de Formação",
        "salario_texto": "Remuneração",
        "salario": "Salário (R$)",
        "vagas": "Vagas",
        "data_inscricao_inicio": "Início Inscrições",
        "data_inscricao_fim": "Término Inscrições",
        "data_taxa_limite": "Vencimento Taxa",
        "data_prova": "Data da Prova",
        "estado": "UF",
        "cidade": "Cidade",
        "status_usuario": "Meu Status",
        "proxima_acao": "Próxima Ação",
        "fonte": "Fonte",
        "link_edital": "Link do Edital",
        "link_original": "Página da Notícia"
    }

    @classmethod
    def preparar_dataframe(cls, concursos: List[Dict[str, Any]]) -> pd.DataFrame:
        """Converte lista de dicionários para DataFrame com nomes amigáveis."""
        if not concursos:
            return pd.DataFrame(columns=list(cls.COLUNAS_MAPEAMENTO.values()))

        df = pd.DataFrame(concursos)
        # Seleciona apenas as colunas mapeadas que existem no df
        cols_presentes = [c for c in cls.COLUNAS_MAPEAMENTO.keys() if c in df.columns]
        df_sub = df[cols_presentes].copy()
        df_sub.rename(columns=cls.COLUNAS_MAPEAMENTO, inplace=True)
        return df_sub

    @classmethod
    def exportar_csv(cls, concursos: List[Dict[str, Any]]) -> bytes:
        """Exporta para CSV delimitado por ponto e vírgula com encoding UTF-8-SIG (compatível com Excel PT-BR)."""
        df = cls.preparar_dataframe(concursos)
        return df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")

    @classmethod
    def exportar_excel(cls, concursos: List[Dict[str, Any]]) -> bytes:
        """Exporta para pasta de trabalho Excel (.xlsx) estilizada."""
        df = cls.preparar_dataframe(concursos)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Concursos")
            # Ajuste de largura automática das colunas
            worksheet = writer.sheets["Concursos"]
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = min(max_len + 4, 50)
        return output.getvalue()
