# 🌾 Comodus - Previsão e Análise de Commodities

## 📌 Visão Geral

Comodus é uma aplicação web desenvolvida em **Flask** que oferece:

✅ Previsão de preços de commodities com Machine Learning

✅ Análises de mercado com Inteligência Artificial

✅ Notícias relevantes do setor

A plataforma é **intuitiva**, com foco em auxiliar na compreensão das tendências do mercado.


## ⚙️ Funcionalidades

* 🔮 **Previsão de Preços:** Modelos LSTM para prever preços futuros.
* 🧠 **Análise de Mercado:** Geração automática de análises com **Google Gemini**.
* 🗞️ **Notícias Recentes:** Coleta inteligente de informações sobre commodities.
* 📊 **Gráficos Interativos:** Visualização clara com **Plotly**.
* 🌓 **Interface Moderna:** Modo escuro, responsiva e intuitiva.
* 🔍 **Autocompletar:** Busca com sugestões automáticas.
* ⚡ **Cache de Dados:** Otimiza desempenho e reduz carregamento.


## 🗂️ Estrutura do Projeto

```
.
├── cache/                  # Cache de dados
├── data_cache/             # Dados históricos (commodities.csv)
├── static/                 # Arquivos estáticos (CSS, JS, imagens)
│   └── logo-g.svg          # Logo do sistema
├── templates/              # Templates HTML
│   ├── erro.html
│   ├── index.html
│   └── previsao.html
├── .env                    # Variáveis de ambiente
├── .gitignore              # Configurações do Git
├── app.py                  # Aplicação Flask principal
├── assistent.py            # Geração de análises com IA
├── noticias.py             # Coleta e processamento de notícias
├── previsao.py             # Modelo de previsão LSTM
├── Procfile                # Configuração para deploy
├── render.yaml             # Deploy na Render
└── requirements.txt        # Dependências Python
```


## 🚀 Configuração e Execução

### ✅ Pré-requisitos

* Python 3.8+
* pip

### 📝 Passos

1️⃣ **Clonar o Repositório**

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd comodus
```

2️⃣ **Criar e Ativar Ambiente Virtual**

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3️⃣ **Instalar Dependências**

```bash
pip install -r requirements.txt
```

4️⃣ **Configurar Variáveis de Ambiente**

Crie o arquivo `.env` na raiz:

```
GOOGLE_API_KEY="SUA_CHAVE_API_DO_GEMINI"
```

5️⃣ **Preparar Dados Históricos**

Adicione o arquivo `commodities.csv` em `data_cache/` com colunas como:

* `Date`
* Nome das commodities (ex: Ouro, Milho, Soja)

6️⃣ **Executar a Aplicação**

```bash
python app.py
```

Acesse: **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**


## 🖥️ Uso

* **Página Inicial:** Campo para buscar ou selecionar a commodity.
* **Página de Previsão:**

  * 📈 Gráfico interativo
  * 💰 Valores previstos
  * 📊 Métricas: RMSE, acurácia
  * 🧠 Análise de mercado por IA
  * 🗞️ Notícias recentes


## 🛠️ Tecnologias Utilizadas

* **Backend:** Python, Flask
* **Machine Learning:** PyTorch, scikit-learn
* **IA:** Google Gemini API
* **Dados:** Pandas, NumPy
* **Gráficos:** Plotly
* **Web Scraping:** requests, BeautifulSoup, feedparser
* **Frontend:** HTML, CSS (Tailwind CSS), JavaScript
* **Fontes:** Google Fonts (Montserrat)
* **Ícones:** Font Awesome


## 🚧 Melhorias Futuras

* 🔐 Autenticação de usuários
* 📢 Alertas personalizados
* 🔗 Integração com mais APIs
* 🧪 Otimização e ajuste do modelo
* 🤖 Deploy contínuo (CI/CD)
* 🌍 Suporte a múltiplos idiomas
* 🖼️ Dashboard personalizável


## 👥 Contribuidores

* **\[Guilherme Nunes]** — Desenvolvedor Principal
* **\[Eduardo Guimarães]** — Colaborador
* **\[Yasmin Schultz]** — Colaborador


✨ **Comodus** — Previsão inteligente e análise de commodities.
