# -*- coding: utf-8 -*-

# Instalação limpa e específica
!pip install -qU rank_bm25 faiss-cpu sentence-transformers

import re
import numpy as np
from rank_bm25 import BM25Okapi
import faiss
from sentence_transformers import SentenceTransformer

# Preparação para o BM25 (Lexical)
def tokenizar(conteudo):
    return re.findall(r"\w+", conteudo.lower())

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

import textwrap

# ── Teste de Retrieval ────────────────────────────────────────────────────────
# Troque a pergunta por algo relacionado ao seu PDF!

PERGUNTA_TESTE = "processors"   # ← edite aqui
METODO        = "hibrido"                                  # "bm25", "dense" ou "hibrido"
K             = 3                                          # quantos trechos recuperar

if METODO == "bm25":
    resultados = recuperar_bm25(PERGUNTA_TESTE, k=K)
elif METODO == "dense":
    resultados = recuperar_dense(PERGUNTA_TESTE, k=K)
else:
    resultados = recuperar_hibrido(PERGUNTA_TESTE, k=K, alpha=0.6)

print(f"Pergunta : {PERGUNTA_TESTE}")
print(f"Método   : {METODO}")
print(f"k        : {K}")
print()
for r in resultados:
    print(f"[{r['id']}] Score: {r['score']:.4f}")
    print(textwrap.fill(r['conteudo'][:300], width=90))
    print("─" * 90)

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
pergunta = "Processors"
resultados = busca_hibrida(pergunta, top_k=3)

print(f"JARVIS encontrou {len(resultados)} trechos usando Busca Híbrida:")
for r in resultados:
    print(f"- Fonte: {r['fonte']} | Trecho: {r['conteudo'][:150]}...")

def construir_prompt(pergunta, docs):
    """
    Monta o conteúdo da mensagem do usuário enviada ao LLM.
    O modelo deve responder APENAS com base no contexto fornecido.
    """
    contexto = "\n\n".join(
        [f"Trecho {i+1}:\n{d['conteudo']}" for i, d in enumerate(docs)]
    )
    return (
        "Responda em portugues usando apenas o contexto abaixo. "
        "Se nao houver informacao suficiente, diga: nao encontrado no contexto.\n\n"
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
    # ── Passo 1: Recuperação ──
    if metodo == "bm25":
        docs = recuperar_bm25(pergunta, k=k)
    elif metodo == "dense":
        docs = recuperar_dense(pergunta, k=k)
    else:
        docs = recuperar_hibrido(pergunta, k=k, alpha=alpha)

    # ── Passo 2: Construção do prompt via chat template ──
    conteudo = construir_prompt(pergunta, docs)
    messages = [{"role": "user", "content": conteudo}]
    resp = client.chat.completions.create(
        model='google/gemma-3-12b-it',
        messages=messages,
    )


    return resp.choices[0].message.content, docs


print("Pipeline RAG pronto!")

import textwrap
# ── Teste do RAG ──────────────────────────────────────────────────────────────
# Faça várias perguntas sobre o seu PDF e observe as respostas!

PERGUNTA = "Computacao aproximada é interessante para pesquisadores?"   # ← edite aqui
METODO   = "hibrido"                                  # "bm25", "dense" ou "hibrido"

resposta, docs = responder_rag(PERGUNTA, metodo=METODO, k=10)

print(f"PERGUNTA: {PERGUNTA}")
print()
print("TRECHOS RECUPERADOS:")
for d in docs:
    print(f"  [{d['id']}] score={d['score']:.4f} | {d['conteudo'][:100]}...")
print()
print("RESPOSTA DO RAG:")
print(textwrap.fill(resposta, width=90))

import json
import pytz # Para colocar a data no fuso-horário local
from datetime import date, timedelta, datetime

# --- Agenda simples para testes ---
"""
# Data adquirida de forma dinâmica
hoje = date.today()
amanha = hoje + timedelta(days=1)
depois_de_amanha = hoje + timedelta(days=2)

# criação da agenda de teste
agenda = [
    {
        "data": hoje.strftime("%d/%m/%Y"),
        "tipo": "reuniao",
        "titulo": "TCC",
        "horario": "15:25 - 16:25"
    },
    {
        "data": hoje.strftime("%d/%m/%Y"),
        "tipo": "aula",
        "titulo": "Inteligência Artificial",
        "horario": "18:30 - 22:30"
    },
    {
        "data": amanha.strftime("%d/%m/%Y"),
        "tipo": "prova",
        "titulo": "Avaliação de Banco de Dados",
        "horario": "07:15 - 09:15"
    },
    {
        "data": depois_de_amanha.strftime("%d/%m/%Y"),
        "tipo": "aula",
        "titulo": "Programação Paralela",
        "horario": "07:15 - 09:15"
    }
]
"""

# --- Agenda melhorada ---
agenda = [

    # Compromissos Recorrentes (Toda semana)
     {
       "titulo": "Reunião de TCC",
       "tipo": "reuniao",
       "horario": "15:25 - 16:25",
       "recorrencia": "semanal",
       "dia_de_semana": 3 # Quinta feira
    },
    {
        "titulo": "Aula de Inteligência Artificial",
        "tipo": "aula",
        "horario": "18:30 - 22:30",
        "recorrencia": "semanal",
        "dia_de_semana": 0 # Segunda feira
    },
    # Compromissos Únicos (data específica)
    {
        "titulo": "Prova de Banco de Dados",
        "tipo": "prova",
        "horario": "07:15 - 09:15",
        "recorrencia": "unica",
        "data": "22/05/2026"
    },
    {
        "titulo": "Prova de Inteligência Artifical",
        "tipo": "prova",
        "horario": "18:30 - 22:30",
        "recorrencia": "unica",
        "data": "01/06/2026"
    },
    {
        "titulo": "Prova de Banco de Dados",
        "tipo": "prova",
        "horario": "07:15 - 09:15",
        "recorrencia": "unica",
        "data": "19/05/2026"
    }
]

#Planilha armazenada localmente (JSON)
caminho_agenda = "agenda.json"
with open(caminho_agenda, "w", encoding= "utf-8") as arquivo:
    json.dump(agenda, arquivo, indent=4, ensure_ascii=False)

print(f"Agenda salva em {caminho_agenda} e pronta para os testes")

def carregar_agenda():
  with open("agenda.json", "r", encoding="utf-8") as arquivo:
    return json.load(arquivo)

def consultar_agenda_simples(periodo="hoje"):
  # Realiza as consultas com base no tempo
  agenda = carregar_agenda()
  hoje = date.today()
  compromissos = []

  if periodo == "hoje":
    data_inicio = data_fim = hoje
  elif periodo == "amanha":
    data_inicio = data_fim = hoje + timedelta(days=1)
  elif periodo == "semana":
    data_inicio = hoje - timedelta(days=hoje.weekday())
    data_fim = data_inicio + timedelta(days=6)
  else:
    raise ValueError(f"Periodo desconhecido: {periodo}")

  for item in agenda:
    data_item = datetime.strptime(item["data"], "%d/%m/%Y").date()
    if data_inicio <= data_item <= data_fim:
      compromissos.append(item)

  return compromissos

def consultar_agenda_melhorada(periodo="hoje"):
  # Vai considerar compromissos recorrentes ao longo das semanas

  with open("agenda.json", "r", encoding="utf-8") as arquivo:
    agenda = json.load(arquivo)

  fuso_local = pytz.timezone('America/Campo_Grande')
  hoje = datetime.now(fuso_local).date()
  compromissos = []

  if periodo in ["hoje", "hoje "]:
    data_inicio = data_fim = hoje
  elif periodo in ["amanha","amanhã"]:
    data_inicio = data_fim = hoje + timedelta(days=1)
  elif periodo == "semana":
    data_inicio = hoje - timedelta(days=hoje.weekday())
    data_fim = data_inicio + timedelta(days=6)
  elif periodo in ["proxima_semana", "proxima semana", "semana que vem"]:
    data_inicio = hoje + timedelta(days=7 - hoje.weekday())
    data_fim = data_inicio + timedelta(days=6)
  else:
    raise ValueError(f"Periodo desconhecido: {periodo}")
    return []

  # Loop que percorre cada dia do período solicitado
  dia = data_inicio
  while dia <= data_fim:
    dia_da_semana_atual = dia.weekday()
    data_atual = dia.strftime("%d/%m/%Y")

    for item in agenda:

      if item.get("recorrencia") == "unica" and item.get("data") == data_atual:
        item_formatado = item.copy()
        item_formatado["data"] = data_atual
        compromissos.append(item_formatado)

      elif item.get("recorrencia") == "semanal" and item.get("dia_de_semana") == dia_da_semana_atual:
        item_formatado = item.copy()
        item_formatado["data"] = data_atual
        compromissos.append(item_formatado)

    dia += timedelta(days=1) # Avança para o dia seguinte

  return compromissos