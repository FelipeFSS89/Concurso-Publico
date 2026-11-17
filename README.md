# 🏛️ Painel de Concursos

Sistema inteligente e completo de monitoramento, gestão estratégica e alertas para concursos públicos no Brasil, desenvolvido com **Python 3.12+**, **Streamlit** e **SQLite**.

A aplicação coleta, unifica e analisa periodicamente concursos publicados nos portais:
- 🌐 **[Degrau Cultural](https://degraucultural.com.br)**
- 🌐 **[Folha QConcursos](https://folha.qconcursos.com)**

---

## 🚀 Como Executar a Aplicação

### 1. Pré-requisitos
Certifique-se de possuir o Python 3.12 ou superior instalado em sua máquina.

### 2. Instalação das Dependências
Na pasta raiz do projeto, instale os pacotes necessários:
```bash
pip install -r requirements.txt
```

### 3. Inicialização do Painel Web
Execute o comando do Streamlit:
```bash
streamlit run app.py
```
O sistema abrirá automaticamente em seu navegador padrão no endereço:
👉 **`http://localhost:8501`**

---

## 🧭 Navegação Moderna e Design SaaS

A interface conta com uma barra lateral estilizada inspirada em ferramentas profissionais (como Notion, Linear e Monday):
- **Barra lateral recolhível (collapse/expand)** para máximo aproveitamento de tela.
- **Destaque visual do item ativo** com transições e animações suaves de hover.
- **Cabeçalho com identidade visual moderna**: Logotipo, título `Painel de Concursos` e subtítulo oficial.
- **Rodapé da Sidebar**: Indicador de status do sistema **Online** (com ponto pulsante animado em verde), versão `v1.0.0` e data de última atualização dinâmica.

### Menus Disponíveis:
1. 🏠 **Dashboard**: Resumo geral de métricas, alertas críticos, vencimentos de inscrição, próximas provas e gráficos.
2. 📋 **Concursos**: Listagem completa, busca, filtros combinados (UF, escolaridade, formação, salário, vagas), detalhes e edição rápida de status.
3. ⭐ **Favoritos**: Acesso rápido aos concursos marcados como prioridade.
4. 🔔 **Alertas**: Central de notificações dividida por criticidade (Vermelho, Amarelo, Verde, Azul).
5. 📅 **Calendário**: Linha do tempo cronológica com datas de inscrição, taxa e provas.
6. 📈 **Estatísticas**: Gráficos analíticos e interativos com Plotly.
7. ⚙️ **Configurações**: Cadastro de cursos de interesse, ajuste do robô de monitoramento e integrações.
8. ℹ️ **Recursos Extras**: Informações sobre a plataforma, desenvolvedor (**Felipe Sousa**), stack técnica e roadmap futuro.

---

## 📂 Estrutura Modular do Projeto

```
Concurso Publico/
├── app.py                          # Ponto de entrada (Entrypoint) do Streamlit
├── config.py                       # Constantes, caminhos e parâmetros globais
├── requirements.txt                # Dependências do projeto
├── README.md                       # Documentação e instruções de execução
├── .streamlit/
│   └── config.toml                 # Configurações do servidor Streamlit
├── data/
│   └── concursos.db                # Banco de dados persistente SQLite (WAL Mode)
├── database/
│   ├── __init__.py
│   ├── connection.py               # Gerenciador de conexão e inicialização DDL
│   ├── schema.py                   # Esquema DDL de todas as tabelas e índices
│   └── repository.py               # Repositórios CRUD (Concursos, Alertas, Configurações)
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py             # Classe base, headers, parsers e regex de salários/vagas
│   ├── degrau_scraper.py           # Coleta e parsing do portal Degrau Cultural
│   ├── folha_scraper.py            # Coleta e parsing do portal Folha QConcursos
│   ├── mock_data.py                # Base semente rica para funcionamento offline/resiliente
│   └── coordinator.py              # Orquestrador com deduplicação por hash SHA-256
├── services/
│   ├── __init__.py
│   ├── alert_service.py            # Central de alertas por criticidade (Vermelho, Amarelo, etc.)
│   ├── matcher_service.py          # Comparador de compatibilidade com áreas de interesse
│   ├── scheduler_service.py        # Agendador em background com schedule e threading
│   ├── export_service.py           # Exportador profissional para Excel (.xlsx) e CSV (.csv)
│   └── notification_service.py     # Hooks prontos para E-mail (SMTP), Telegram e WhatsApp
└── ui/
    ├── __init__.py
    ├── styles.py                   # CSS responsivo estilo SaaS, cores semânticas e animações
    ├── components.py               # Componentes reutilizáveis (KPI cards, badges, banners)
    └── views/
        ├── __init__.py
        ├── dashboard_view.py       # Dashboard Principal com KPIs, alertas e gráficos
        ├── concursos_view.py       # Listagem rica, busca, filtros combinados e gestão
        ├── alertas_view.py         # Central de notificações e alertas categorizados
        ├── favoritos_view.py       # Página exclusiva de certames favoritados
        ├── estatisticas_view.py    # Gráficos interativos com Plotly
        ├── calendario_view.py      # Calendário mensal e cronograma de provas/taxas
        ├── config_view.py          # Formações de interesse e ajustes do robô
        └── about_view.py           # Página Sobre o Projeto, Desenvolvedor e Roadmap
```

---

## 👨‍💻 Desenvolvedor

- **Nome:** Felipe Sousa
- **Projeto:** Painel de Concursos
- **Tecnologias Utilizadas:** Python, Streamlit, SQLite, Pandas, BeautifulSoup, Plotly

---

## 🔮 Objetivos Futuros (Roadmap)

- Integração com Telegram (Bot de avisos)
- Integração com WhatsApp (Disparador de alertas)
- Integração com E-mail (Boletim semanal)
- Aplicativo Mobile nativo
- Dashboard Avançado de notas de corte
- Sincronização em Nuvem multi-dispositivo

---

© 2026 - Desenvolvido por **Felipe Sousa**. Todos os direitos reservados.
