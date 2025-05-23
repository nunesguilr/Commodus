from flask import Flask, render_template, request, jsonify
from previsao import executar_previsao, carregar_dados_csv
import logging
import pandas as pd
from datetime import datetime
import json
import os
from typing import Dict, Any, Optional
from assistent import gerar_conselho
from noticias import buscar_noticias
from markdown import markdown

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

TICKERS_VALIDOS = {
    "Ouro": "Ouro", "Prata": "Prata", "Cobre": "Cobre", "Alumínio": "Alumínio", "Zinco": "Zinco",
    "Gado_Vivo": "Gado_Vivo", "Carne_Porco": "Carne_Porco", "Milho": "Milho", "Soja": "Soja", "Trigo": "Trigo",
    "Petróleo_WTI": "Petróleo_WTI", "Petróleo_Brent": "Petróleo_Brent", "Gás_Natural": "Gás_Natural",
    "Gasolina_RBOB": "Gasolina_RBOB", "Óleo_Aquecimento": "Óleo_Aquecimento", "Suco_Laranja": "Suco_Laranja",
    "Algodão": "Algodão", "Café_Arábica": "Café_Arábica", "Açúcar": "Açúcar", "Cacau": "Cacau",
    "Madeira": "Madeira", "Platina": "Platina", "Paládio": "Paládio"
}

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(ticker: str) -> str:
    return os.path.join(CACHE_DIR, f"{ticker}.json")

def load_from_cache(ticker: str) -> Optional[Dict[str, Any]]:
    cache_file = get_cache_path(ticker)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if (datetime.now() - cache_time).days < 1:
                    cached_data_result = cache_data['data']
                    if 'analise_gemini' not in cached_data_result:
                        cached_data_result['analise_gemini'] = ''
                    return cached_data_result
        except Exception as e:
            logging.error(f"Erro ao ler cache: {e}")
    return None

def save_to_cache(ticker: str, data: Dict[str, Any]) -> None:
    cache_file = get_cache_path(ticker)
    try:
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "data": {
                "preco_atual": float(data['preco_atual']),
                "previsao_amanha": float(data['previsao_amanha']),
                "rmse": float(data.get('rmse', 0)),
                "acuracia": float(data.get('acuracia', 0)),
                "grafico_html": data.get('grafico_html', ''),
                "analise_gemini": data.get('analise_gemini', '')
            }
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=4)
    except Exception as e:
        logging.error(f"Erro ao salvar cache: {e}")

try:
    df_commodities = carregar_dados_csv()
    logging.info("Dados de commodities carregados com sucesso")
except Exception as e:
    logging.error(f"Falha ao carregar dados: {str(e)}")
    df_commodities = pd.DataFrame()

@app.route('/')
def index():
    return render_template(
        'index.html',
        commodities=sorted(TICKERS_VALIDOS.values()),
        last_update=datetime.now().strftime("%d/%m/%Y %H:%M")
    )

@app.route('/previsao/<nome_commodity>')
def previsao_commodity(nome_commodity: str):
    if nome_commodity not in TICKERS_VALIDOS.values():
        return render_template(
            'erro.html',
            mensagem=f"Commodity '{nome_commodity}' não encontrada"
        ), 404

    ticker = [k for k, v in TICKERS_VALIDOS.items() if v == nome_commodity][0]
    cached_data = load_from_cache(ticker)

    try:
        if cached_data:
            resultado = cached_data
            noticias = buscar_noticias(nome_commodity, ticker)
            logging.info(f"Usando dados em cache para {nome_commodity}")
        else:
            raw_result = executar_previsao(nome_commodity, df_commodities)
            noticias = buscar_noticias(nome_commodity, ticker)
            analise_gemini_raw = gerar_conselho(
                raw_result['preco_atual'],
                raw_result['previsao_amanha'],
                raw_result['acuracia'],
                noticias
            )
            analise_gemini = markdown(analise_gemini_raw)
            resultado = {
                "preco_atual": float(raw_result['preco_atual']),
                "previsao_amanha": float(raw_result['previsao_amanha']),
                "rmse": float(raw_result.get('rmse', 0)),
                "acuracia": float(raw_result.get('acuracia', 0)),
                "grafico_html": raw_result.get('grafico_html', ''),
                "analise_gemini": analise_gemini
            }
            save_to_cache(ticker, resultado)
            logging.info(f"Dados atualizados para {nome_commodity}")

        return render_template(
            'previsao.html',
            nome=nome_commodity,
            resultado=resultado,
            grafico_html=resultado['grafico_html'],
            analise_gemini=resultado['analise_gemini'],
            noticias=noticias
        )

    except Exception as e:
        logging.error(f"Erro na previsão para {nome_commodity}: {str(e)}")
        return render_template(
            'erro.html',
            mensagem=f"Erro ao processar {nome_commodity}: {str(e)}"
        ), 500

@app.route('/api/previsao/<nome_commodity>', methods=['GET'])
def api_previsao(nome_commodity: str):
    try:
        if nome_commodity not in TICKERS_VALIDOS.values():
            return jsonify({"error": "Commodity não encontrada"}), 404

        resultado = executar_previsao(nome_commodity, df_commodities)
        noticias = buscar_noticias(nome_commodity)
        analise_gemini_raw = gerar_conselho(
            resultado['preco_atual'], resultado['previsao_amanha'], resultado['acuracia'], noticias
        )
        analise_gemini = markdown(analise_gemini_raw)

        return jsonify({
            "commodity": nome_commodity,
            "preco_atual": float(resultado['preco_atual']),
            "previsao_amanha": float(resultado['previsao_amanha']),
            "acuracia": float(resultado['acuracia']),
            "ultima_atualizacao": datetime.now().isoformat(),
            "analise_gemini": analise_gemini,
            "noticias": noticias
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
