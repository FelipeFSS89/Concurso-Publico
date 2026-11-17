"""
Módulo de Telas / Visões do Painel de Concursos
"""
from ui.views.dashboard_view import render_dashboard_view
from ui.views.concursos_view import render_concursos_view
from ui.views.alertas_view import render_alertas_view
from ui.views.favoritos_view import render_favoritos_view
from ui.views.estatisticas_view import render_estatisticas_view
from ui.views.calendario_view import render_calendario_view
from ui.views.config_view import render_config_view
from ui.views.about_view import render_about_view

__all__ = [
    "render_dashboard_view",
    "render_concursos_view",
    "render_alertas_view",
    "render_favoritos_view",
    "render_estatisticas_view",
    "render_calendario_view",
    "render_config_view",
    "render_about_view"
]
