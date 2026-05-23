# -*- coding: utf-8 -*-
import re
import numpy as np
from rank_bm25 import BM25Okapi
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path

src_projeto = Path(__file__).parent if "__file__" in locals() else Path.cwd()
raiz_projeto = src_projeto.parent

# Define as pastas de origem e destino
pasta_md = raiz_projeto / "Markdown"

# Função de chunks

def chunking_fixo(texto, tamanho=500):
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        chunks.append(texto[inicio:fim])
        inicio = fim
    return chunks

def chunking_janela(texto, tamanho=500, sobreposicao=100):
    if sobreposicao >= tamanho:
        raise ValueError(f"sobreposicao ({sobreposicao}) deve ser menor que tamanho ({tamanho})")
    chunks = []
    passo = tamanho - sobreposicao
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        chunks.append(texto[inicio:fim])
        inicio += passo
    return chunks

def chunking_paragrafo(texto, min_chars=100):
    paragrafos = [p.strip() for p in texto.split("\n\n")]
    return [p for p in paragrafos if len(p) >= min_chars]

# ── GERENCIADOR DE BIBLIOTECA ────────────────────────────────────

def carregar_e_processar_biblioteca(pasta_origem, estrategia="janela"):
    """
    Lê todos os arquivos .md da pasta e aplica a estratégia escolhida.
    """
    todos_os_chunks = []

    print(f"Processando biblioteca em: {pasta_md}")

    for arquivo_md in pasta_md.glob("*.md"):
        texto_cru = arquivo_md.read_text(encoding="utf-8")

        # Seleciona a estratégia que será implementada nas chunks
        if estrategia == "fixo":
            brutos = chunking_fixo(texto_cru)
        elif estrategia == "janela":
            brutos = chunking_janela(texto_cru)
        else:
            brutos = chunking_paragrafo(texto_cru)

        # Responsável por definir qual a fonte dos dados selecionados
        for i, trecho in enumerate(brutos):
            if trecho.strip():
                todos_os_chunks.append({
                    "id": f"{arquivo_md.stem}_{i:03d}",
                    "fonte": arquivo_md.name,
                    "conteudo": trecho.strip()
                })

    print(f"Sucesso! {len(todos_os_chunks)} chunks carregadas.")
    return todos_os_chunks

# Preparação para o BM25 (Lexical)
def tokenizar(conteudo):
    return re.findall(r"\w+", conteudo.lower())

# Incializador do motor de busca

biblioteca_jarvis = carregar_e_processar_biblioteca(pasta_md, estrategia="janela")

corpus_tokenizado = [tokenizar(c["conteudo"]) for c in biblioteca_jarvis]
indice_bm25 = BM25Okapi(corpus_tokenizado)

# Preparação para o FAISS (Semântico - embeddings)
print("Carregando modelo de embeddings...")
modelo_embed = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

textos = [c["conteudo"] for c in biblioteca_jarvis]
matriz_emb = modelo_embed.encode(textos, normalize_embeddings=True)

# Cria o índice FAISS
dim = matriz_emb.shape[1]
indice_faiss = faiss.IndexFlatIP(dim)
indice_faiss.add(matriz_emb.astype("float32"))

print(f"JARVIS Atualizado! BM25 e FAISS prontos para busca híbrida.")
