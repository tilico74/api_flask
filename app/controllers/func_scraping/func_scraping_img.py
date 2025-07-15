import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def raspar_imagens_por_tipo(url: str, tipo: str):
    """
    Raspador de imagens com base no tipo (Patrocinadores, Parceiros, Apoiadores)

    Parâmetros:
        url  -> str: URL da página que será raspada
        tipo -> str: Título da seção desejada ("Patrocinadores", "Parceiros", "Apoiadores")

    Retorna:
        Lista de strings com os atributos alt das imagens ou mensagens de erro
    """

    try:

        headers = {"User-Agent": os.getenv("USER_AGENT", "projetoIntegrador/1.0")}

        # Faz requisição HTTP para obter o conteúdo da página
        response = requests.get(url,headers=headers, timeout=10)

        # Lança erro caso o status da resposta não seja 200 (OK)
        response.raise_for_status()

        # Converte o conteúdo HTML em um objeto BeautifulSoup para facilitar a manipulação
        soup = BeautifulSoup(response.content, 'html.parser')

        # Localiza todas as seções com id específico onde estão as imagens
        secoes = soup.find_all('div', id='fh5co-blog-section')

        # Lista que vai armazenar os textos (alt) das imagens
        alts = []

        # Percorre cada seção para encontrar o título correspondente ao tipo
        for secao in secoes:
            titulo = secao.find('h2')  # Procura o título da seção
            # Compara o título com o tipo esperado (ignora letras maiúsculas/minúsculas)
            if titulo and tipo.lower() in titulo.text.lower():
                # Procura todas as imagens dentro da seção com a classe específica
                imagens = secao.find_all('img', class_='img-responsive')
                for img in imagens:
                    alt = img.get('alt')  # Extrai o texto alternativo da imagem
                    if alt:
                        alts.append(alt)  # Adiciona na lista se não for vazio

        # Retorna os resultados ou uma mensagem se nada foi encontrado
        if alts:
            return f"Estas são as empresas {tipo.capitalize()} do Projeto Jovem Programador: " + ", ".join(alts) + ".\n\n"
        
        else:
            return f"Nenhuma imagem com alt encontrada para '{tipo}' em {url}"

    except requests.exceptions.RequestException as e:
        # Trata erros de conexão, timeout, domínio inválido, etc.
        return [f"Erro de conexão ou requisição: {e}"]

    except Exception as e:
        # Captura qualquer outro erro inesperado
        return [f"Erro inesperado: {e}"]