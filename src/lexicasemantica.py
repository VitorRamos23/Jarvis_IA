import textwrap
import re
import numpy as np
from rank_bm25 import BM25Okapi
import faiss
from sentence_transformers import SentenceTransformer


def recuperar_bm25(pergunta, k=3):
    """Busca léxica: pontua chunks por frequência de termos da pergunta."""
    scores = indice_bm25.get_scores(tokenizar(pergunta))
    idx = np.argsort(scores)[::-1][:k]
    return [{"id": biblioteca_jarvis[i]["id"], "texto": biblioteca_jarvis[i]["texto"], "score": float(scores[i])} for i in idx]


def recuperar_dense(pergunta, k=3):
    """Busca semântica: encontra chunks com significado similar à pergunta."""
    q = modelo_embed.encode([pergunta], normalize_embeddings=True).astype("float32")
    scores, idx = indice_faiss.search(q, k)
    # Quando k > total de chunks, FAISS preenche com índice -1.
    # Em Python, chunks[-1] retornaria o último chunk (errado!), então filtramos.
    return [
        {"id": biblioteca_jarvis[i]["id"], "conteudo": biblioteca_jarvis[i]["conteudo"], "score": float(scores[0][j])}
        for j, i in enumerate(idx[0])
        if i >= 0
    ]


def normalizar(v):
    """Normaliza um vetor para o intervalo [0, 1]."""
    v = np.array(v, dtype="float32")
    delta = float(v.max() - v.min())
    if delta < 1e-9:
        return np.zeros_like(v)
    return (v - v.min()) / delta


def recuperar_hibrido(pergunta, k=3, alpha=0.6):
    """
    Combina BM25 e semântico.
    alpha = peso do semântico (0 = só BM25, 1 = só semântico, 0.6 = padrão)
    """
    sb = normalizar(indice_bm25.get_scores(tokenizar(pergunta)))
    q = modelo_embed.encode([pergunta], normalize_embeddings=True).astype("float32")
    sd = normalizar(np.dot(matriz_emb, q[0]))
    score_final = alpha * sd + (1.0 - alpha) * sb
    idx = np.argsort(score_final)[::-1][:k]
    return [{"id": biblioteca_jarvis[i]["id"], "conteudo": biblioteca_jarvis[i]["conteudo"], "score": float(score_final[i])}
            for i in idx]


print("Funções de retrieval prontas!")

def busca_hibrida(pergunta, top_k=3, peso_bm25=0.3, peso_faiss=0.7):
    # 1. Busca Lexical (BM25)
    tokens_pergunta = tokenizar(pergunta)
    scores_bm25 = indice_bm25.get_scores(tokens_pergunta)

    # 2. Busca Semântica (FAISS)
    pergunta_emb = modelo_embed.encode([pergunta], normalize_embeddings=True).astype("float32")
    scores_faiss, indices_faiss = indice_faiss.search(pergunta_emb, len(biblioteca_jarvis))

    # Um array de zeros para o score semântico na ordem original da biblioteca
    final_faiss_scores = np.zeros(len(biblioteca_jarvis))
    for score, idx in zip(scores_faiss[0], indices_faiss[0]):
        final_faiss_scores[idx] = score

    # 3. Normalização e Combina
    # Normalizamos os scores para ficarem entre 0 e 1
    max_bm25 = np.max(scores_bm25) if np.max(scores_bm25) > 0 else 1

    scores_combinados = []
    for i in range(len(biblioteca_jarvis)):
        s_bm25 = (scores_bm25[i] / max_bm25) * peso_bm25
        s_faiss = final_faiss_scores[i] * peso_faiss # FAISS já costuma vir normalizado por IP

        score_total = s_bm25 + s_faiss
        scores_combinados.append((score_total, biblioteca_jarvis[i]))

    # Ordena pelo score combinado
    scores_combinados.sort(key=lambda x: x[0], reverse=True)

    return [item[1] for item in scores_combinados[:top_k]]
