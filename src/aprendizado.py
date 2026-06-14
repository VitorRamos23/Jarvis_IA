import json
from pathlib import Path
from  config import client
from rag_busca_chunks import busca_hibrida

# Configuração de memória para as perguntas

diretorio_src = Path(__file__).parent if "__file__" in locals() else Path.cwd()
raiz_projeto = diretorio_src.parent
caminho_memoria = raiz_projeto / "memoria_curta.json"

def salvar_memoria(pergunta, contexto):
    with open(caminho_memoria, "w", encoding="utf-8") as f:
        json.dump({"pergunta": pergunta,
                   "contexto": contexto},
                   f,
                   ensure_ascii=False)

def carregar_memoria():
    if caminho_memoria.exists():
        with open(caminho_memoria, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# 1. Perguntas ao usuário

def gerar_pergunta(tema):

    docs = busca_hibrida(tema, top_k=3)

    if not docs:
        return f"Desculpe, não encontrei materiais suficientes sobre {tema}"
    
    contexto = "\n\n".join([f"Trecho:\n{d['conteudo']}" for d in docs])

    prompt = (
        f"Você é o JARVIS, e vai gerar perguntas para o usuário.\n"
        f"Baseado ESTRITAMENTE no contexto abaixo, crie UMA pergunta desafiadora e conceitual para testar o conhecimento do usuário sobre: {tema}.\n"
        f"Regras:\n"
        f"1. Faça APENAS a pergunta. NUNCA forneça a resposta na mesma mensagem.\n"
        f"2. Termine a mensagem dizendo: 'Quando estiver pronto, digite a sua resposta para eu avaliar!'\n\n"
        f"Contexto Extraído:\n{contexto}"
    )

    # Ele vai perguntar e avaliar a resposta para ver se foi boa ou não.

    resp = client.chat.completions.create(
        model='Qwen/Qwen2.5-14B-Instruct-AWQ',
        messages=[{"role": "system", "content": prompt}],
        temperature=0.4
    ).choices[0].message.content

    salvar_memoria(resp, contexto)

    return resp

def avaliar_resposta(resposta):

    # Vai receber a resposta do usuário, buscar o contexto correto e avaliar

    memoria = carregar_memoria()
    if not memoria:
        return "Eu não me lembro de ter feito uma pergunta recente. Peça para mim gerar uma nova pergunta."

    pergunta_feita = memoria["pergunta"]
    contexto = memoria["contexto"]

    prompt = (
        f"Você é o JARVIS, e vai corrigir a resposta do usuário.\n"
        f"Você fez a seguinte PERGUNTA ao aluno:\n'{pergunta_feita}'\n\n"
        f"O aluno deu a seguinte RESPOSTA:\n'{resposta}'\n\n"
        f"Sua missão é avaliar a resposta cruzando com o GABARITO (Contexto) abaixo:\n"
        f"1. Diga claramente se ele está CORRETO, ERRADO ou PARCIALMENTE CORRETO.\n"
        f"2. Explique o porquê de forma didática.\n\n"
        f"Gabarito (Contexto da Matéria):\n{contexto}"
    )

    resp = client.chat.completions.create(
        model='Qwen/Qwen2.5-14B-Instruct-AWQ',
        messages=[{"role": "system", "content": prompt}],
        temperature=0.2
    ).choices[0].message.content
    return resp

# 2. gerar exercícios para revisão

def gerar_exercicios(tema):

    docs = busca_hibrida(tema, top_k=3)

    if not docs:
        return f"Não encontrei informações suficientes sobre {tema}."
    
    contexto = "\n\n".join([f"Trecho:\n{d['conteudo']}" for d in docs])

    prompt = (
        f"Você é o JARVIS. O usuário quer revisar o tema '{tema}'.\n"
        f"Baseado no contexto abaixo, gere 3 exercícios para que o usuário memorize e revise.\n"
        f"Formato obrigatório para cada exercício:\n"
        f"Pergunta: [Sua pergunta aqui]\n"
        f"Resposta: [Uma resposta direta de no máximo 2 linhas]\n\n"
        f"Contexto Extraído:\n{contexto}"
    )

    resp = client.chat.completions.create(
        model='Qwen/Qwen2.5-14B-Instruct-AWQ',
        messages=[{"role": "system", "content": prompt}],
        temperature=0.2
    ).choices[0].message.content
    return resp