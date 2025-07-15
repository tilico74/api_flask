import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.controllers.func_scraping.func_scraping_main import func_scraping_main

load_dotenv()

class JovemProgramadorChatbot:
    def __init__(self):
        self.groq_model = ChatGroq(
            temperature=0.8,
            model_name="llama3-70b-8192",
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.gemini_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            temperature=0.8,
            api_key=os.getenv("GEMINI_API_KEY")
        )
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = self._load_website_content()
        self.chain = self._setup_chain()
       

    def _load_website_content(self):
        paths = [
            "sobre.php", "duvidas.php", "patrocinadores.php", "parceiros.php", "apoiadores.php",
            "index.php", "hackathon/", "lgpd.php", "privacidade.php", "n.php?ID=136", "n.php?ID=135", "n.php?ID=134",
            "n.php?ID=133", "n.php?ID=132", "n.php?ID=131", "n.php?ID=129", "n.php?ID=128"
        ]
        documentos_raw = []

        for path in paths:
            try:
                conteudo = func_scraping_main(path)

                if isinstance(conteudo, list):
                    conteudo = "\n\n".join(conteudo)

                if isinstance(conteudo, str) and len(conteudo.strip()) > 50:
                    doc = Document(page_content=conteudo.strip(), metadata={"source": path})
                    documentos_raw.append(doc)
                else:
                    print(f"[⚠️] Conteúdo vazio ou ignorado: {path}")

            except Exception as e:
                print(f"[❌] Erro ao carregar '{path}': {str(e)}")

        # ✨ DEDUPLICAÇÃO por similaridade semântica com embeddings
        print("🔁 Removendo conteúdos repetidos semanticamente...")
        textos = [doc.page_content for doc in documentos_raw]
        embeddings_vetores = self.embeddings.embed_documents(textos)

        documentos_filtrados = []
        vetores_filtrados = []

        for i, vetor in enumerate(embeddings_vetores):
            if not vetores_filtrados:
                documentos_filtrados.append(documentos_raw[i])
                vetores_filtrados.append(vetor)
                continue

            similar = False
            for v in vetores_filtrados:
                sim = cosine_similarity([vetor], [v])[0][0]
                if sim >= 0.85:
                    similar = True
                    break

            if not similar:
                documentos_filtrados.append(documentos_raw[i])
                vetores_filtrados.append(vetor)

        print(f"✅ Documentos finais após filtro: {len(documentos_filtrados)}")

        # 🔪 Dividir os documentos em chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200,separators=["\n\n", ".", "?", "!"])
        splits = splitter.split_documents(documentos_filtrados)

        return FAISS.from_documents(splits, self.embeddings)

    def _setup_chain(self):

        template = """
        Você é um assistente especializado em ajudar usuários com informações sobre o site Jovem Programador.
        O site Jovem Programador (https://www.jovemprogramador.com.br/) é uma plataforma educacional que oferece cursos, artigos e recursos para programadores iniciantes.
        
        Use o seguinte contexto para responder à pergunta. Se não souber a resposta, diga que não sabe, não invente informações, sem omitir dados importantes.

        Contexto: {context}

        Pergunta: {question}

        Responda de forma clara, concisa e útil, mantendo um tom amigável e encorajador. Sem saldação na resposta.
        """

        prompt = ChatPromptTemplate.from_template(template)
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.groq_model  # ou self.gemini_model
            | StrOutputParser()
        )

        # 🔍 Rodar uma busca para inspecionar o contexto real depois do teste pode ser remivido!!!
        try:
            docs = retriever.get_relevant_documents("listar tudo")
            print("\n📄 CONTEXTO CARREGADO PELO VETOR FAISS:")
            for i, doc in enumerate(docs, 1):
                print(f"\n--- Documento {i} | Fonte: {doc.metadata.get('source')} ---")
                print(doc.page_content[:10000])  # mostra até 1000 caracteres para não poluir
        except Exception as e:
            print(f"⚠️ Erro ao imprimir contexto: {e}")


        return chain

    def chat(self, question):
        try:
            return self.chain.invoke(question)
        except Exception as e:
            return f"Erro ao processar: {str(e)}"
