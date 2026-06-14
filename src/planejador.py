import pytz
from datetime import datetime
from config import client

from agenda import consultar_agenda_melhorada
from lista_de_tarefas import carregar_tarefas
from rag_busca_chunks import busca_hibrida

def plano_de_estudos(pergunta):

    # 1. Análise da agenda
    agenda_semana = consultar_agenda_melhorada("semana")
    dias_semana = ["Segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]

    if not agenda_semana:
        contexto_agenda = "A agenda está livre nesta semana."
    else:
        contexto_agenda = ""
        for i in agenda_semana:
            data_str = i.get('data','')
            if data_str:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                nome_dia = dias_semana[data_obj.weekday()]
                contexto_agenda += f"- [{data_str}] ({nome_dia}) {i['titulo'].upper()} às {i['horario']}.\n"
        
    # 2. Coleta de tarefas pendentes
    tarefas = carregar_tarefas()
    tarefas_pendentes = [t for t in tarefas if not t["concluida"]]

    if not tarefas_pendentes:
        contexto_tarefas = "Não há tarefas pendentes no momento."
    else:
        contexto_tarefas = "\n".join([f"- [ID: {t['id']}] {t['corpo']}" for t in tarefas_pendentes])

    # 3. Coleta do material de estudos

    busca = busca_hibrida(pergunta, top_k=3)

    if not busca:
        contexto_materiais = "Nenhum material de estudo foi encontrado."
    else:
        contexto_materiais = "\n\n".join([f"Fonte ({d['fonte']}):\n{d['conteudo']}" for d in busca])

    # 4. Prompt

    fuso_local = pytz.timezone('America/Campo_Grande')
    agora = datetime.now(fuso_local)

    prompt_sistema = (
        "Você é o JARVIS, um assistente acadêmico avançado. O usuário pediu ajuda para planejar os estudos ou priorizar tarefas.\n"
        "Sua missão é cruzar os horários ocupados da Agenda, as Tarefas pendentes e os Materiais de Estudo (se relevantes) para montar um roteiro lógico, realista e direto ao ponto.\n\n"
        "Regras ESTRITAS:\n"
        "1. Seja estratégico: se a agenda estiver cheia hoje, sugira focar apenas na tarefa mais crítica.\n"
        "2. Se o usuário pedir um plano para uma prova, use os 'Materiais Extraídos' para sugerir tópicos concretos de estudo.\n"
        "3. NÃO seja prolixo. Use bullet points e horários sugeridos se achar pertinente.\n\n"
        f"Data e Hora Atual: {agora.strftime('%d/%m/%Y')} às {agora.strftime('%H:%M')} ({dias_semana[agora.weekday()]})\n\n"
        f"AGENDA DA SEMANA:\n{contexto_agenda}\n\n"
        f"TAREFAS PENDENTES:\n{contexto_tarefas}\n\n"
        f"MATERIAIS EXTRAÍDOS DO BANCO DE DADOS:\n{contexto_materiais}"
    )

    messages = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": pergunta}
    ]

    try:
        resposta = client.chat.completions.create(
            model='Qwen/Qwen2.5-14B-Instruct-AWQ',
            messages=messages,
            temperature=0.3,
        ).choices[0].message.content
        return resposta
    except Exception as e:
        return f"Erro ao gerar plano de estudos: {e}"