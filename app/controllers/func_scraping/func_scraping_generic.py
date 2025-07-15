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

        # Tenta fazer a requisição para a URL
        response = requests.get(url, headers=headers, timeout=10)  # ⛑️ Adiciona timeout para evitar travamentos

        # Verifica se o status da resposta é sucesso (200)
        response.raise_for_status()

        # Converte HTML para objeto BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove tags que não queremos processar
        for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'form']):
            tag.decompose()

        textos_unicos = set()  # Evita texto duplicado
        resultados = []

        # Define a ordem de prioridade das tags de texto
        ordem_tags = ['h1', 'h2', 'h3', 'h4', 'p', 'li']

        for tag_name in ordem_tags:
            for tag in soup.find_all(tag_name):
                texto = limpar_texto(tag.get_text())

                # Evita textos curtos (como links ou itens vazios)
                if len(texto) > 40:
                    hash_texto = hashlib.md5(texto.encode('utf-8')).hexdigest()

                    # Garante que o texto ainda não foi adicionado
                    if hash_texto not in textos_unicos:
                        textos_unicos.add(hash_texto)
                        resultados.append(texto)

        # Junta os textos formatados com espaçamento entre eles
        texto_formatado = "\n\n".join(resultados)

        # Retorna o conteúdo limpo e formatado
        return texto_formatado

    except requests.exceptions.RequestException as e:
        # ⚠️ Tratamento de erro de conexão, URL inválida, timeout, etc.
        return f"Erro de requisição: {e}"

    except Exception as e:
        # ⚠️ Tratamento de erro inesperado (ex: falha ao processar HTML)
        return f"Erro inesperado: {e}"
