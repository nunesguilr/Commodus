import feedparser
import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
import re

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def obter_nome_commodity(ticker: str) -> str:
    nomes_comodities = {
        "GC=F": "Ouro", "SI=F": "Prata", "PL=F": "Platina", "PA=F": "Paládio", "HG=F": "Cobre",
        "CL=F": "Petróleo WTI", "BZ=F": "Petróleo Brent", "NG=F": "Gás Natural",
        "RB=F": "Gasolina RBOB", "HO=F": "Óleo de Aquecimento",
        "ZC=F": "Milho", "ZS=F": "Soja", "ZW=F": "Trigo", "KE=F": "Trigo Vermelho",
        "ZM=F": "Farelo de Soja", "ZL=F": "Óleo de Soja", "ZO=F": "Aveia",
        "LE=F": "Gado Vivo", "HE=F": "Carne de Porco", "GF=F": "Gado de Corte",
        "SB=F": "Açúcar", "CC=F": "Cacau", "KC=F": "Café Arábica", "CT=F": "Algodão",
        "OJ=F": "Suco de Laranja", "LBS=F": "Madeira",
        "DX=F": "Índice Dólar", "ES=F": "S&P 500 Futuros", "NQ=F": "Nasdaq 100 Futuros"
    }
    return nomes_comodities.get(ticker, ticker)


def buscar_noticias_rss(termo: str, termo_ingles: str, fontes_rss: List[str]) -> List[Dict[str, str]]:
    noticias = []
    palavras_relevantes = [
        "price", "market", "futures", "export", "production", "supply", "demand", "commodity", "tariff",
        "preço", "mercado", "exportação", "produção", "oferta", "demanda", "safra", "clima", "arábica",
        "robusta", "cotação", "bolsa", "commodities", "análise", "perspectivas", "tendências",
        "цены", "рынок", "фьючерсы", "экспорт", "производство", "предложение", "спрос", "товар", "тариф",
        "анализ", "перспективы", "тенденции", "новости", "уржай", "погода",
        "prices", "marche", "futures", "exportation", "production", "offre", "demande", "matière première", "tarif",
        "analyse", "perspectives", "tendances", "nouvelles", "récolte", "météo"
    ]
    palavras_ignorar = [
        "recipe", "cooking", "culinary", "lifestyle", "health", "diet", "consumer", "receita", "culinária",
        "estilo de vida", "saúde", "dieta", "café da manhã", "barista", "promoção", "loja", "concurso",
        "receta", "cocina", "culinario", "estilo de vida", "salud", "dieta", "consumidor", "desayuno",
        "barista", "promoción", "tienda", "concurso", "рецепт", "кулинария", "образ жизни", "здоровье", "диета",
        "потребитель", "завтрак", "бариста", "продвижение", "магазин", "конкурс",
        "recette", "cuisine", "culinaire", "style de vie", "santé", "régime", "consommateur", "petit déjeuner",
        "barista", "promotion", "magasin", "concours"
    ]

    for feed_url in fontes_rss:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = entry.title
                link = entry.link
                summary = entry.get("summary", "")
                content = (title + " " + summary).lower()
                if (termo.lower() in content or termo_ingles.lower() in content) and \
                        any(palavra in content for palavra in palavras_relevantes) and \
                        not any(palavra in content for palavra in palavras_ignorar):
                    noticias.append({"titulo": title, "link": link})
        except Exception as e:
            logging.error(f"Erro ao acessar feed {feed_url}: {e}")
    return noticias


def buscar_noticias_scraping(termo: str, termo_ingles: str, fontes_scraping: List[str]) -> List[Dict[str, str]]:
    noticias = []
    palavras_relevantes = [
        "price", "market", "futures", "export", "production", "supply", "demand", "commodity", "tariff",
        "preço", "mercado", "exportação", "produção", "oferta", "demanda", "safra", "clima", "arábica",
        "robusta", "cotação", "bolsa", "commodities", "análise", "perspectivas", "tendências",
        "цены", "рынок", "фьючерсы", "экспорт", "производство", "предложение", "спрос", "товар", "тариф",
        "анализ", "перспективы", "тенденции", "новости", "уржай", "погода",
        "prices", "marche", "futures", "exportation", "production", "offre", "demande", "matière première", "tarif",
        "analyse", "perspectives", "tendances", "nouvelles", "récolte", "météo"
    ]
    palavras_ignorar = [
        "recipe", "cooking", "culinary", "lifestyle", "health", "diet", "consumer", "receita", "culinária",
        "estilo de vida", "saúde", "dieta", "café da manhã", "barista", "promoção", "loja", "concurso",
        "receta", "cocina", "culinario", "estilo de vida", "salud", "dieta", "consumidor", "desayuno",
        "barista", "promoción", "tienda", "concurso", "рецепт", "кулинария", "образ жизни", "здоровье", "диета",
        "потребитель", "завтрак", "бариста", "продвижение", "магазин", "конкурс",
        "recette", "cuisine", "culinaire", "style de vie", "santé", "régime", "consommateur", "petit déjeuner",
        "barista", "promotion", "magasin", "concours"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }

    for url in fontes_scraping:
        try:
            time.sleep(1)
            response = requests.get(
                url, headers=headers, timeout=15, allow_redirects=True)
            if response.status_code != 200:
                logging.warning(
                    f"Erro HTTP {response.status_code} ao acessar {url}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all(re.compile(
                "h[2-3]"), class_=re.compile("title|headline"))

            for article in articles:
                title_element = article.find("a")
                if title_element:
                    title = title_element.text.strip()
                    link = title_element.get("href", "")
                    if not link.startswith("http"):
                        base_url = url.split("/")[0] + "//" + url.split("/")[2]
                        link = base_url + link
                    content = title.lower()
                    if (termo.lower() in content or termo_ingles.lower() in content) and \
                            any(palavra in content for palavra in palavras_relevantes) and \
                            not any(palavra in content for palavra in palavras_ignorar):
                        noticias.append({"titulo": title, "link": link})
        except Exception as e:
            logging.error(f"Erro ao fazer scraping em {url}: {e}")
    return noticias


def buscar_noticias(termo: str, ticker: str) -> List[Dict[str, str]]:
    termos_ingles = {
        "Ouro": "gold", "Prata": "silver", "Platina": "platinum", "Paládio": "palladium", "Cobre": "copper",
        "Petróleo WTI": "WTI oil", "Petróleo Brent": "Brent oil", "Gás Natural": "natural gas",
        "Gasolina RBOB": "gasoline", "Óleo de Aquecimento": "heating oil",
        "Milho": "corn", "Soja": "soybean", "Trigo": "wheat", "Trigo Vermelho": "red wheat",
        "Farelo de Soja": "soybean meal", "Óleo de Soja": "soybean oil", "Aveia": "oats",
        "Gado Vivo": "live cattle", "Carne de Porco": "lean hogs", "Gado de Corte": "feeder cattle",
        "Açúcar": "sugar", "Cacau": "cocoa", "Café Arábica": "coffee", "Algodão": "cotton",
        "Suco de Laranja": "orange juice", "Madeira": "lumber",
        "Índice Dólar": "dollar index"
    }
    termo_ingles = termos_ingles.get(termo, termo.lower())

    fontes_rss = [
        "https://www.investing.com/rss/news_1.rss",
        "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "https://www.marketwatch.com/rss/commodities",
        "https://www.ft.com/markets?format=rss",
        "https://www.cnbc.com/id/10000664/device/rss",
        "https://www.thestreet.com/feed/markets",
        "https://www.barchart.com/stocks/sectors/commodities/rss",
        "https://www.agriculture.com/news/rss",
        "https://www.valor.com.br/empresas/agro/rss.xml",
        "https://www.estadao.com.br/economia/agronegocio/rss.xml",
        "https://www1.folha.uol.com.br/mercado/rss091.xml",
        "https://exame.com/brasil/agro/feed/",
        "https://globorural.globo.com/rss.xml",
        "https://www.canalrural.com.br/rss/",
        "https://www.noticiasagricolas.com.br/rss.xml",
        "https://g1.globo.com/economia/agronegocios/noticia/feed/",
        "https://www.reuters.com/arc/outbound/article/worldNews/",
        "https://www.bloomberg.com/feed/podcast/money-stuff",
        "https://www.ft.com/world/asia-pacific",
        "https://www.theguardian.com/world/rss",
        "https://www.theglobeandmail.com/news/world/rss/",
        "https://www.smh.com.au/rss/world",
        "https://www.aljazeera.com/xml/rss/all.xml",
        "https://www.zeit.de/xml/index",
        "https://www.lemonde.fr/rss/une.xml",
        "https://elpais.com/rss/elpais_portada.xml",
        "https://www.ilsole24ore.com/rss/homepage.xml",
        "https://www.nikkei.com/rss/news",
        "https://www.thehindu.com/news/national/rss/application/",

    ]

    fontes_scraping = [
        "https://www.reuters.com/markets/commodities/",
        "https://www.ft.com/commodities",
        "https://www.cnbc.com/commodities/",
        "https://www.barchart.com/news/commodities",
        "https://www.valor.com.br/agro/",
        "https://www.estadao.com.br/economia/agronegocio/",
        "https://www1.folha.uol.com.br/mercado/",
        "https://www.canalrural.com.br/noticias/mercado/",
        "https://www.noticiasagricolas.com.br/noticias/cafe/",
        "https://g1.globo.com/economia/agronegocios/",
        "https://www.theguardian.com/business/commodities",
        "https://www.thehindu.com/business/economy/",
        "https://www.aljazeera.com/economy/",
        "https://www.smh.com.au/business/markets/",
        "https://www.theglobeandmail.com/investing/markets/",
    ]

    with ThreadPoolExecutor(max_workers=4) as executor:
        rss_future = executor.submit(
            buscar_noticias_rss, termo, termo_ingles, fontes_rss)
        scraping_future = executor.submit(
            buscar_noticias_scraping, termo, termo_ingles, fontes_scraping)

        noticias_rss = rss_future.result()
        noticias_scraping = scraping_future.result()

    noticias = noticias_rss + noticias_scraping
    noticias_unicas = []
    links_vistos = set()
    for noticia in noticias:
        if noticia["link"] not in links_vistos:
            noticias_unicas.append(noticia)
            links_vistos.add(noticia["link"])

    return noticias_unicas[:10]


if __name__ == "__main__":
    ticker = input(
        "Digite o código da commodity (ex: KC=F para Café): ").strip().upper()
    nome_commodity = obter_nome_commodity(ticker)
    noticias = buscar_noticias(nome_commodity, ticker)

    print(f"\n### Últimas notícias sobre {nome_commodity} ###")
    if isinstance(noticias, dict) and ("erro" in noticias or "mensagem" in noticias):
        print(noticias.get("erro", noticias.get("mensagem")))
    else:
        for noticia in noticias:
            print(f"- {noticia['titulo']}: {noticia['link']}")
