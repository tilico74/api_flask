# Chatbot Jovem Programador - API Flask

Este projeto integra o 1º Projeto Integrador do curso Jovem Programador 2025. Desenvolvido por Nelson Cristiano Santos Jucoski, o sistema oferece um chatbot inteligente que responde perguntas sobre o programa Jovem Programador com base no conteúdo real extraído do site oficial: [www.jovemprogramador.com.br](https://www.jovemprogramador.com.br)

---

## 🔹 Objetivo

Criar uma API backend que permita:

- Envio de perguntas via requisição HTTP ou interface web
- Respostas automáticas baseadas no conteúdo do site Jovem Programador
- Uso de IA para interpretação e recuperação semântica de dados
- Funcionamento sem cadastro manual de perguntas/respostas

---

## 🔹 Tecnologias Utilizadas

- **Python 3**
- **Flask** – API web
- **BeautifulSoup** – Raspagem de conteúdo do site
- **FAISS** – Indexação e busca vetorial
- **HuggingFace Embeddings** – Vetorização semântica
- **Groq (LLaMA 3)** e **Gemini** – Modelos de linguagem
- **JavaScript (AJAX)** – Requisições dinâmicas do front-end
- **Bootstrap** e **CSS** – Estilização da interface

---

## 🔹 Estrutura do Projeto

```
api_flask/
├── app/
│   ├── controllers/
│   │   ├── func_scraping/
│   │   ├── pergunta_controller.py
│   │   └── views.py
│   ├── models/
│   ├── services/
│   ├── static/
│   ├── templates/
│   │   ├── banner.html
│   │   ├── chatbot.html
│   │   ├── desenvolvedor.html
│   │   ├── funcionalidades.html
│   │   ├── home.html
│   │   ├── menu.html
│   │   ├── modelo.html
│   │   └── requisitos.html
│   ├── __init__.py
│   └── chatbot_class.py
├── data/
│   ├── faiss_index/
│   ├── extras.txt
│   └── vectorstore_cache.json
├── .env
├── .gitignore
├── app.py
├── Procfile
├── README.md
├── requirements.txt
└── runtime.txt
```

---

## 🔹 Funcionalidades

### Funcionais

- **RF01**: Permitir envio de perguntas e exibir respostas via IA
- **RF02**: Usar raspagem de dados do site oficial
- **RF03**: Retornar resposta padrão quando informação não for localizada

### Não Funcionais

- **RNF01**: Tempo médio de resposta inferior a 5 segundos
- **RNF02**: Acessível por dispositivos móveis e desktops
- **RNF03**: Disponível 24h/dia (exceto manutenção)

---

## 🔹 Modo de Funcionamento

1. **Raspagem de conteúdo**: Utiliza BeautifulSoup para extrair dados do site.
2. **Deduplicação semântica**: Usa embeddings e similaridade para eliminar textos repetidos.
3. **Vetorização e indexação**: Dados são vetorizados com HuggingFace e indexados com FAISS.
4. **Busca e Resposta**: A pergunta é vetorizada e comparada com o conteúdo, e a IA responde com base no contexto.

---
## 🔹 Variáveis de ambiente do projeto Flask com IA

Para que o projeto funcione corretamente.

Crie um arquivo `.env` na raiz do projeto:

## Chave de API da Groq (utilizada pela LLM LLaMA3)
GROQ_API_KEY=coloque_sua_chave_groq_aqui
link para criação: https://console.groq.com/keys

## Chave de API do Google Gemini (utilizada para IA generativa)
GOOGLE_API_KEY=coloque_sua_chave_google_gemini_aqui
link para criação: https://makersuite.google.com/app/apikey

## Variável de ambiente
URL_JOVEM_PROGRAMADOR=https://jovemprogramador.com.br/

## Variável de ambiente
USER_AGENT=projetoIntegrador/1.0 (+https://github.com/SEU_GITHUB/api_flask.git)

---
## 🔹 Como executar localmente

```bash
# Clone o repositório
git clone https://github.com/tilico74/api_flask.git
cd api_flask

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute a API localmente
python run.py
```

Acesse em: [http://localhost:5000](http://localhost:5000)

---

## 🔹 Requisitos do Sistema

- Python 3.11 ou superior
- Memória mínima: 1GB recomendável (uso de IA e FAISS)
- Conexão com internet (para uso de APIs externas)

---

## 🔹 Sobre o Desenvolvedor

**Nome**: Nelson Cristiano Santos Jucoski  
**Turma 3**: Jovem Programador 2025  
**Função**: Responsável técnico e desenvolvedor principal  

---

## 🔹 Versão

Versão: 1.0.0

---

## 🔹 Licença

Este projeto é de uso acadêmico, desenvolvido para fins educacionais no Projeto Integrador do programa Jovem Programador. A reutilização comercial requer autorização.

---

## 🔹 Orientadora

**Professora Karina Casola Fernandes** – Responsável pelo acompanhamento técnico e pedagógico do Projeto Integrador.

---

## 🔹 Considerações finais

O projeto demonstra a aplicação prática de técnicas de IA em um contexto real, utilizando tecnologias modernas, código limpo e boas práticas de engenharia de software.