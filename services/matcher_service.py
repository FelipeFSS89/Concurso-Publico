"""
Serviço de Compatibilidade entre Concursos e Formações de Interesse do Usuário
"""
import re
from typing import List, Dict, Any, Tuple
from database.repository import ConfiguracaoRepository

class MatcherService:
    """Verifica e pontua a compatibilidade de cada concurso com os interesses do candidato."""

    @classmethod
    def verificar_compatibilidade(cls, concurso: Dict[str, Any], formacoes_ativas: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Avalia se o concurso coincide com as áreas e palavras-chave de formação do usuário.
        Retorna (is_compativel, lista_de_matches).
        """
        if not formacoes_ativas:
            return True, ["Todas as áreas"]

        texto_concurso = f"{concurso.get('nome', '')} {concurso.get('cargo', '')} {concurso.get('orgao', '')} {concurso.get('area_formacao', '')} {concurso.get('escolaridade', '')}".lower()
        
        matches = []
        for f in formacoes_ativas:
            nome_f = f.get("nome", "").strip()
            kw_str = f.get("palavras_chave", "") or ""
            palavras = [p.strip().lower() for p in kw_str.split(",") if p.strip()]
            palavras.append(nome_f.lower())

            for kw in palavras:
                # Busca por palavra ou termo exato
                padrao = r'\b' + re.escape(kw) + r'\b'
                if re.search(padrao, texto_concurso):
                    matches.append(nome_f)
                    break

        matches_unicos = list(dict.fromkeys(matches))
        return len(matches_unicos) > 0, matches_unicos

    @classmethod
    def enriquecer_concursos_com_match(cls, concursos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Adiciona as propriedades 'is_compativel' e 'areas_match' a cada concurso na lista."""
        formacoes = ConfiguracaoRepository.listar_formacoes()
        formacoes_ativas = [f for f in formacoes if f.get("ativo", 1)]

        for c in concursos:
            compativel, matches = cls.verificar_compatibilidade(c, formacoes_ativas)
            c["is_compativel"] = compativel
            c["areas_match"] = matches

        return concursos
