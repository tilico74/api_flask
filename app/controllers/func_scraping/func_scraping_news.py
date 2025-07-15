import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def raspar_noticias(url):
    try:
        headers = {
            "User-Agent": os.getenv("USER_AGENT", "projeto_integrador/1.0")
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove tags desnecessárias
        for tag in soup.select('script, style, nav, footer, header, form'):
            tag.decompose()

        # Extrai título
        titulo = soup.select_one("h1.title")
        titulo_texto = titulo.get_text(strip=True) if titulo else "Título não encontrado"

        # Extrai data
        data = soup.select_one("h5.date")
        data_texto = data.get_text(strip=True) if data else "Data não encontrada"

        # Extrai conteúdo
        conteudo_div = soup.select_one("div.v-align-middle")
        paragrafos = conteudo_div.find_all("p") if conteudo_div else []
        corpo = "\n\n".join([
            p.get_text(strip=True)
            for p in paragrafos if len(p.get_text(strip=True)) > 30
        ])

        if not corpo:
            return f"[⚠️] Conteúdo não encontrado em: {url}"

        return f"{titulo_texto}\n{data_texto}\n\n{corpo}"

    except requests.exceptions.RequestException as e:
        return f"[Erro de requisição] {e}"

    except Exception as e:
        return f"[Erro inesperado] {e}"
