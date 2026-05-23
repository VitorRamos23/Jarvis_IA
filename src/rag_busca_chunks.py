import re
import numpy as np
import textwrap
from rank_bm25 import BM25Okapi
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path
from config import client

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

# --- TESTE DO JARVIS HÍBRIDO ---
if __name__ == "__main__":
    pergunta = "quais são os avanços da inteligência artificial"
    resultados = busca_hibrida(pergunta, top_k=3)

    print(f"JARVIS encontrou {len(resultados)} trechos usando Busca Híbrida:")
    for r in resultados:
        print(f"- Fonte: {r['fonte']} | Trecho: {r['conteudo'][:150]}...")


def construir_prompt(pergunta, docs):
    contexto = "\n\n".join(
        [f"Trecho {i+1}:\n{d['conteudo']}" for i, d in enumerate(docs)]
    )
    return (
        "Você é o JARVIS. Responda à pergunta do usuário usando APENAS as informações do Contexto fornecido. "
        "Atenção: O Contexto pode estar em inglês, mas você deve traduzir as informações e responder em PORTUGUÊS. "
        "Se não houver informação suficiente no Contexto para responder, diga: 'não encontrado no contexto'.\n\n"
        f"Contexto:\n{contexto}\n\n"
        f"Pergunta: {pergunta}"
    )


def responder_rag(pergunta, metodo="hibrido", k=3, alpha=0.6, max_tokens=512):
    """
    Função principal do RAG:
      1. Recupera os k chunks mais relevantes
      2. Monta o prompt com o contexto usando o chat template do Qwen2.5
      3. Gera a resposta com o LLM
    """
    
    docs = busca_hibrida(pergunta, top_k=k)

    # ── Passo 2: Construção do prompt via chat template ──
    conteudo = construir_prompt(pergunta, docs)
    messages = [{"role": "user", "content": conteudo}]
    resp = client.chat.completions.create(
        model='google/gemma-3-12b-it',
        messages=messages,
    )


    return resp.choices[0].message.content, docs


print("Pipeline RAG pronto!")


# ── Teste do RAG ──────────────────────────────────────────────────────────────
# Faça várias perguntas sobre o seu PDF e observe as respostas!

if __name__ == "__main__":
    
    PERGUNTA = "Quando foi criada a interligência artificial?"   # ← edite aqui
    
    resposta, docs = responder_rag(PERGUNTA, k=3)

    print(f"PERGUNTA: {PERGUNTA}")
    print()
    print("TRECHOS RECUPERADOS:")
    for d in docs:
        print(f"  [{d['id']}] {d['conteudo'][:100]}...")
    print()
    print("RESPOSTA DO RAG:")
    print(textwrap.fill(resposta, width=90))
    print("\n" + "="*90)
