import os
import google.generativeai as genai
import google
from dotenv import load_dotenv
import logging
from typing import List, Dict

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")  

def resumir_texto(texto):
    prompt = rf"""Resuma o seguinte conteúdo de notícia em até 3 linhas, focando no impacto para o mercado de commodities:

{texto}
"""
    try:
        resposta = model.generate_content(prompt)
        return resposta.text.strip()
    except google.api_core.exceptions.ServiceUnavailable as e:
        logging.error(f"Serviço indisponível ao resumir texto: {e}")
        return "Erro: Serviço indisponível. Tente novamente mais tarde."
    except Exception as e:
        logging.error(f"Erro inesperado ao resumir texto: {e}")
        return f"Erro ao resumir: {e}"

def gerar_conselho(preco_atual: float, previsao: float, acuracia: float, noticias: List[Dict] = None):
    noticias_formatadas = ""
    if noticias and len(noticias) > 0:
        noticias_formatadas = "\n\nNotícias relevantes:\n"
        for i, noticia in enumerate(noticias[:3], 1):  # Limita a 3 notícias
            noticias_formatadas += f"{i}. {noticia.get('titulo', '')}\n"
            if 'resumo' in noticia:
                noticias_formatadas += f"   Resumo: {noticia['resumo']}\n"
    
    prompt = rf"""Com base nos dados técnicos e notícias recentes, forneça uma análise completa:
    
Dados Técnicos:
- Preço atual: {preco_atual:.2f} USD
- Previsão para amanhã: {previsao:.2f} USD
- Confiança do modelo: {acuracia:.2%}

{noticias_formatadas}

Forneça:
1. Uma análise técnica concisa (2-3 frases)
2. Impacto das notícias no mercado (1-2 frases)
3. Recomendação de curto prazo para investidores (1 frase)

Mantenha o tom profissional e objetivo, destacando fatores de risco quando relevantes.
"""
    
    try:
        resposta = model.generate_content(prompt)
        return resposta.text.strip()
    except Exception as e:
        logging.error(f"Erro ao gerar conselho: {e}")
        return f"Análise técnica: O modelo prevê {'alta' if previsao > preco_atual else 'baixa'} com {acuracia:.2%} de confiança.\n\nErro na análise de notícias: {str(e)}"