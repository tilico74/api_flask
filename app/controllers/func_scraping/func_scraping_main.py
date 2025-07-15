import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from .func_scraping_img import raspar_imagens_por_tipo
from .func_scraping_generic import raspar_texto_generic
from .func_scraping_news import raspar_noticias

load_dotenv()


def func_scraping_main(path):
    url_base = os.getenv("URL_JOVEM_PROGRAMADOR")
    url_full = url_base + path

    if path in ['patrocinadores.php', 'apoiadores.php', 'parceiros.php']:
        tipo = path.replace(".php", "")
        content = raspar_imagens_por_tipo(url_full, tipo)
        return content

    elif path.startswith("n.php?ID="):
        content = raspar_noticias(url_full)
        return content

    else:
        content = raspar_texto_generic(url_full)
        return content

