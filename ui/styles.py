"""
Estilos Customizados CSS para o Painel de Concursos
Proporciona visual moderno estilo SaaS (Notion, Linear, Monday), responsivo e com hierarquia de cores estrita.
"""

CUSTOM_CSS = """
<style>
/* Reset e fontes do Google */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* -------------------------------------------------------------
   SIDEBAR MODERNA ESTILO SAAS (Linear / Notion / Monday)
   ------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background-color: #F8FAFC !important;
    border-right: 1px solid #E2E8F0 !important;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.02) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.1rem !important;
    padding-right: 1.1rem !important;
}

/* Cabeçalho da Sidebar */
.sidebar-brand-container {
    padding: 0.5rem 0.25rem 1.25rem 0.25rem;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid #E2E8F0;
}

.sidebar-brand-header {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}

.sidebar-brand-icon {
    background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
    color: white;
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    box-shadow: 0 4px 10px rgba(79, 70, 229, 0.25);
    flex-shrink: 0;
}

.sidebar-brand-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.025em;
    line-height: 1.2;
}

.sidebar-brand-subtitle {
    font-size: 0.75rem;
    color: #64748B;
    line-height: 1.35;
    margin-top: 0.3rem;
    font-weight: 500;
}

/* -------------------------------------------------------------
   MENU DE NAVEGAÇÃO INTERATIVO
   ------------------------------------------------------------- */
.nav-section-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94A3B8;
    padding: 0.5rem 0.6rem 0.25rem 0.6rem;
    margin-bottom: 0.25rem;
}

/* Container do stRadio transformado em Lista SaaS */
div[data-testid="stRadio"] > label {
    display: none !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
}

/* Itens individuais de navegação */
div[data-testid="stRadio"] div[role="radiogroup"] > label {
    display: flex !important;
    align-items: center !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    cursor: pointer !important;
    background-color: transparent !important;
    border: 1px solid transparent !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    margin: 0 !important;
    user-select: none !important;
}

/* Ocultar o círculo/radio padrão */
div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* Tipografia do item */
div[data-testid="stRadio"] div[role="radiogroup"] > label p {
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #475569 !important;
    margin: 0 !important;
    transition: color 0.15s ease !important;
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
}

/* Efeito Hover estilo Linear */
div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
    background-color: #F1F5F9 !important;
    transform: translateX(4px) !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] > label:hover p {
    color: #0F172A !important;
    font-weight: 600 !important;
}

/* Item ATIVO / Selecionado */
div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%) !important;
    border: 1px solid #C7D2FE !important;
    border-left: 4px solid #6366F1 !important;
    box-shadow: 0 2px 5px rgba(99, 102, 241, 0.12) !important;
    transform: translateX(3px) !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p {
    color: #4338CA !important;
    font-weight: 700 !important;
}

/* -------------------------------------------------------------
   RODAPÉ DA SIDEBAR
   ------------------------------------------------------------- */
.sidebar-footer-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1rem;
    margin-top: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.footer-status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}

.status-badge-online {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background-color: #ECFDF5;
    color: #065F46;
    border: 1px solid #A7F3D0;
    padding: 3px 9px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

.pulsing-dot {
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    animation: pulseGreen 1.8s infinite;
}

@keyframes pulseGreen {
    0% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
        box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

.footer-version {
    font-size: 0.75rem;
    color: #64748B;
    font-weight: 600;
    background: #F1F5F9;
    padding: 2px 7px;
    border-radius: 6px;
}

.footer-divider {
    height: 1px;
    background-color: #F1F5F9;
    margin: 0.5rem 0;
}

.footer-update-text {
    font-size: 0.74rem;
    color: #64748B;
    line-height: 1.4;
}

.footer-update-text strong {
    color: #334155;
}

/* -------------------------------------------------------------
   HEADER PRINCIPAL DAS PÁGINAS
   ------------------------------------------------------------- */
.app-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    padding: 1.5rem 2rem;
    border-radius: 14px;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
    border-left: 6px solid #6366F1;
}

.app-header h1 {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.app-header p {
    margin: 0.35rem 0 0 0;
    color: #94A3B8;
    font-size: 0.95rem;
}

/* KPI Cards */
.kpi-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.25rem 1rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.08);
}

.kpi-title {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748B;
    margin-bottom: 0.4rem;
}

.kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.1;
}

.kpi-sub {
    font-size: 0.75rem;
    color: #94A3B8;
    margin-top: 0.5rem;
}

/* Cores de Alerta Padronizadas */
.alert-box {
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.85rem;
    display: flex;
    align-items: flex-start;
    gap: 0.85rem;
    border-left: 5px solid;
    font-size: 0.9rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.alert-box.urgente {
    background-color: #FEF2F2;
    border-left-color: #EF4444;
    color: #991B1B;
}

.alert-box.atencao {
    background-color: #FFFBEB;
    border-left-color: #F59E0B;
    color: #92400E;
}

.alert-box.novidade {
    background-color: #F0FDF4;
    border-left-color: #10B981;
    color: #065F46;
}

.alert-box.info {
    background-color: #EFF6FF;
    border-left-color: #3B82F6;
    color: #1E40AF;
}

/* Badges */
.badge-tag {
    display: inline-block;
    padding: 0.2rem 0.55rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
}

.badge-compatible {
    background-color: #DCFCE7;
    color: #15803D;
    border: 1px solid #86EFAC;
}

.badge-uf {
    background-color: #E0E7FF;
    color: #3730A3;
}

.badge-vagas {
    background-color: #F1F5F9;
    color: #334155;
}

.badge-salario {
    background-color: #FEF3C7;
    color: #92400E;
    font-weight: 700;
}

/* Timeline */
.timeline-item {
    border-left: 2px solid #E2E8F0;
    padding-left: 1rem;
    margin-left: 0.5rem;
    margin-bottom: 0.85rem;
    position: relative;
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: -5px;
    top: 4px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #6366F1;
}

.timeline-date {
    font-size: 0.75rem;
    color: #94A3B8;
}

.timeline-text {
    font-size: 0.85rem;
    color: #334155;
    margin-top: 0.2rem;
}
</style>
"""
