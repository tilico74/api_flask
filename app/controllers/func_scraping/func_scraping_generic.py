import os
import requests
from bs4 import BeautifulSoup
import hashlib
from dotenv import load_dotenv

load_dotenv()


def limpar_texto(texto):
    # Remove espaços em branco duplicados e quebras de linha
    return ' '.join(texto.strip().split())

def raspar_texto_generic(url):
    try:
        headers = {"User-Agent": os.getenv("USER_AGENT", "projetoIntegrador/1.0")}

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove tags que não queremos processar
        for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'form']):
            tag.decompose()

        textos_unicos = set()
        resultados = []

        
        # Define as tags de texto relevantes
        tags_relevantes = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'span', 'div'] # Adicione outras tags se for relevante, como 'span', 'div' se contiverem texto principal

        # Encontra TODAS as tags relevantes na ordem em que aparecem no documento
        # Isso preserva a ordem natural do HTML
        for tag in soup.find_all(tags_relevantes):
            texto = limpar_texto(tag.get_text())

            # Considera o texto apenas se for suficientemente longo e não um link órfão
            # Tente aumentar o limite de 10 se ainda pegar muito lixo
            if len(texto) > 10 and not tag.name == 'a': # Exemplo: Ignora se for uma tag <a>, a menos que o texto seja muito grande
                hash_texto = hashlib.md5(texto.encode('utf-8')).hexdigest()

                if hash_texto not in textos_unicos:
                    textos_unicos.add(hash_texto)
                    resultados.append(texto)
        

        texto_formatado = "\n\n".join(resultados)
        return texto_formatado

    except requests.exceptions.RequestException as e:
        return f"Erro de requisição: {e}"
    except Exception as e:
        return f"Erro inesperado: {e}"