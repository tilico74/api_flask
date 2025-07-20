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
import traceback
from typing import List, Optional
import hashlib
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from app.controllers.func_scraping.func_scraping_main import func_scraping_main


load_dotenv()

class JovemProgramadorChatbot:
    def __init__(self):
        """Inicializa o chatbot com configurações otimizadas."""
        self._initialize_models()
        self.vectorstore = self._load_or_create_vectorstore()
        self.chain = self._setup_chain()
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(exist_ok=True)

    def _initialize_models(self):
        """Configura os modelos LLM e embeddings."""
        self.groq_model = ChatGroq(
            temperature=0.8,
            model_name="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            max_retries=3,
            request_timeout=30
        )

        self.gemini_model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.8,
            api_key=os.getenv("GEMINI_API_KEY"),
            max_output_tokens=2048
        )
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    def _load_or_create_vectorstore(self) -> FAISS:
        """Carrega ou cria o índice vetorial."""
        index_path = Path("data/faiss_index")
        cache_file = Path("data/vectorstore_cache.json")
        
        if self._check_vectorstore_cache(index_path, cache_file):
            print("🔄 Carregando índice FAISS do cache...")
            return FAISS.load_local(str(index_path), self.embeddings, allow_dangerous_deserialization=True)

        print("🔁 Criando novo índice FAISS...")
        
        # 1. Carrega todos os documentos (scraping + extras)
        documentos = self._load_documents_parallel()
        documentos.extend(self._carregar_extras_txt("data/extras.txt"))  # Adiciona ANTES da deduplicação
        
        # 2. Aplica filtros
        documentos_filtrados = self._deduplicate_documents(documentos)
        
        # 3. Divide em chunks
        splits = self._split_documents(documentos_filtrados)
        
        # 4. Cria e salva o índice
        vectorstore = FAISS.from_documents(splits, self.embeddings)
        vectorstore.save_local(str(index_path))
        self._update_vectorstore_cache(index_path, cache_file)
        
        # Verificação adicional
        self._verify_extras_in_index(vectorstore)
        
        return vectorstore

    def _verify_extras_in_index(self, vectorstore):
        """Verifica se o extras.txt foi corretamente indexado"""
        print("\n🔍 Verificando inclusão do extras.txt no índice...")
        
        # Busca por conteúdo que deveria estar no extras.txt
        test_queries = [
            "conteúdo do arquivo extras",
            "informações extras",
            "dados complementares"
        ]
        
        for query in test_queries:
            docs = vectorstore.similarity_search(query, k=2)
            print(f"\n🔎 Resultados para '{query}':")
            
            found = False
            for doc in docs:
                if doc.metadata.get("source") == "extras.txt":
                    print(f"✅ Encontrado extras.txt (score: {doc.metadata.get('score', 'N/A')})")
                    print(f"Trecho: {doc.page_content[:200]}...")
                    found = True
            
            if not found:
                print("❌ extras.txt não encontrado nos resultados")
                for doc in docs:
                    print(f"Documento de {doc.metadata.get('source')}: {doc.page_content[:200]}...")

    def _load_documents_parallel(self) -> List[Document]:
        """Carrega documentos em paralelo."""
        paths = [
            "sobre.php", "duvidas.php", "patrocinadores.php", "parceiros.php", 
            "apoiadores.php", "index.php", "hackathon/", "lgpd.php", 
            "privacidade.php", "n.php?ID=136", "n.php?ID=135", "n.php?ID=134",
            "n.php?ID=133", "n.php?ID=132", "n.php?ID=131", "n.php?ID=129", 
            "n.php?ID=128"
        ]
        
        documentos = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self._fetch_document, path): path for path in paths}
            
            for future in as_completed(futures):
                path = futures[future]
                try:
                    doc = future.result()
                    if doc:
                        documentos.append(doc)
                except Exception as e:
                    print(f"[❌] Erro ao carregar '{path}': {str(e)}")
        
        return documentos

    def _fetch_document(self, path: str) -> Optional[Document]:
        """Busca um documento individual."""
        try:
            # Substitua por sua função de scraping real
            conteudo = func_scraping_main(path)
            
            if isinstance(conteudo, list):
                conteudo = "\n\n".join(conteudo)
            
            if isinstance(conteudo, str) and len(conteudo.strip()) > 50:
                return Document(
                    page_content=conteudo.strip(), 
                    metadata={"source": path, "timestamp": int(time.time())}
                )
            print(f"[⚠️] Conteúdo vazio ou ignorado: {path}")
            return None
                
        except Exception as e:
            print(f"[❌] Erro ao carregar '{path}': {str(e)}")
            traceback.print_exc()
            return None

    def _deduplicate_documents(self, documentos: List[Document]) -> List[Document]:
        """Remove documentos duplicados."""
        if not documentos:
            return []
            
        print("🔁 Removendo conteúdos repetidos...")
        seen_hashes = set()
        unique_docs = []
        
        for doc in documentos:
            content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_docs.append(doc)
        
        return self._semantic_deduplication(unique_docs) if len(unique_docs) > 50 else unique_docs

    def _semantic_deduplication(self, documentos: List[Document]) -> List[Document]:
        """Deduplicação semântica com similaridade de cosseno."""
        textos = [doc.page_content for doc in documentos]
        embeddings = self.embeddings.embed_documents(textos)
        embeddings_array = np.array(embeddings)
        similarity_matrix = cosine_similarity(embeddings_array)
        
        to_remove = set()
        n = len(embeddings_array)
        
        for i in range(n):
            if i not in to_remove:
                for j in range(i+1, n):
                    if similarity_matrix[i,j] >= 0.55:
                        to_remove.add(j)
        
        return [doc for idx, doc in enumerate(documentos) if idx not in to_remove]

    def _split_documents(self, documentos: List[Document]) -> List[Document]:
        """Divide documentos em chunks."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
            length_function=len,
            is_separator_regex=False
        )
        
        splits = []
        for doc in documentos:
            for split in splitter.split_documents([doc]):
                splits.append(split)
        
        return splits

    def _check_vectorstore_cache(self, index_path: Path, cache_file: Path) -> bool:
        """Verifica se o cache está válido."""
        if not index_path.exists() or not cache_file.exists():
            return False
            
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                
            for path, timestamp in cache_data.items():
                if not os.path.exists(path) or os.path.getmtime(path) > timestamp:
                    return False
            return True
        except:
            return False

    def _update_vectorstore_cache(self, index_path: Path, cache_file: Path):
        """Atualiza o cache do vectorstore."""
        cache_data = {}
        paths = [
            "sobre.php", "duvidas.php", "patrocinadores.php", "parceiros.php", 
            "apoiadores.php", "index.php", "hackathon/", "lgpd.php", 
            "privacidade.php", "n.php?ID=139", "n.php?ID=136", "n.php?ID=135", "n.php?ID=134",
            "n.php?ID=133", "n.php?ID=132", "n.php?ID=131", "n.php?ID=128", 
            "n.php?ID=123","n.php?ID=122", "n.php?ID=121", "n.php?ID=120", "n.php?ID=115", "n.php?ID=114", "n.php?ID=119", "data/extras.txt"
        ]
        
        for path in paths:
            if os.path.exists(path):
                cache_data[path] = os.path.getmtime(path)
                
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)

    def _carregar_extras_txt(self, caminho: str) -> List[Document]:
        """Carrega arquivo extras.txt."""
        caminho = Path(caminho)
        if not caminho.exists():
            print("⚠️ Arquivo 'extras.txt' não encontrado.")
            return []
            
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                texto = f.read().strip()
                
                if len(texto) < 50:
                    print("⚠️ 'extras.txt' está vazio ou muito curto.")
                    return []
                    
                if "====" in texto:
                    docs = []
                    sections = texto.split("====")
                    for section in sections:
                        if section.strip():
                            docs.append(Document(
                                page_content=section.strip(),
                                metadata={"source": "extras.txt", "section": "custom"}
                            ))
                    print(f"📄 Carregadas {len(docs)} seções de 'extras.txt'")
                    return docs
                else:
                    doc = Document(
                        page_content=texto,
                        metadata={"source": "extras.txt"}
                    )
                    print("📄 'extras.txt' carregado para o contexto.")
                    return [doc]
                    
        except Exception as e:
            print(f"⚠️ Erro ao ler 'extras.txt': {str(e)}")
            return []

    def _setup_chain(self):
        """Configura a chain de processamento."""
        template = """ Você é um assistente especializado em ajudar usuários com informações sobre o site Jovem Programador.
        O site Jovem Programador (https://www.jovemprogramador.com.br/) é uma plataforma educacional que oferece cursos, artigos e recursos para programadores iniciantes.
        O Projeto Jovem Programador tambem pode ser referenciado pelo seu apelido 'PJP' ou também 'Jovem Programador'. 
        Use este contexto para responder:
        
        Contexto: {context}
        
        Pergunta: {question}
        
        Regras:
        - Seja conciso mas completo.
        - Evite resposta longas.
        - Prenda a atenção do usuário.        
        - Evite simbolos como * e outros e emojis no texto para não atrapalhar.
        - Sem saudações/despedidas.
        - Se não souber, diga "Não encontrei essa informação".
        - Nunca invente URLs ou links.                    
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 6,
                "score_threshold": 0.7,
                "fetch_k": 20
            }
        )
        
        groq_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.groq_model
            | StrOutputParser()
        )
        
        gemini_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.gemini_model
            | StrOutputParser()
        )
        
        self.fallback_chain = groq_chain.with_fallbacks([gemini_chain])
        return self.fallback_chain

    def chat(self, question: str, use_cache: bool = True) -> str:
        """Processa uma pergunta do usuário."""
        if not question.strip():
            return "Por favor, faça uma pergunta sobre o Jovem Programador."
            
        question_hash = hashlib.md5(question.lower().encode()).hexdigest()
        cache_file = self.cache_dir / f"{question_hash}.json"
        
        if use_cache and cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                    if time.time() - cached['timestamp'] < 86400:
                        return cached['response']
            except:
                pass
                
        try:
            start_time = time.time()
            response = self.chain.invoke(question)
            elapsed = time.time() - start_time
            
            with open(cache_file, 'w') as f:
                json.dump({
                    'question': question,
                    'response': response,
                    'timestamp': time.time(),
                    'elapsed': elapsed
                }, f)
                
            return response
            
        except Exception as e:
            error_msg = "Desculpe, ocorreu um erro. Por favor, tente novamente."
            print(f"Erro no chat: {str(e)}")
            traceback.print_exc()
            return error_msg


# Exemplo de uso
if __name__ == "__main__":
    print("Inicializando chatbot... (isso pode demorar na primeira execução)")
    bot = JovemProgramadorChatbot()
    
    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() in ['sair', 'exit', 'quit']:
            break
            
        print("\nJovem Programador:", end=" ")
        response = bot.chat(user_input)
        print(response)