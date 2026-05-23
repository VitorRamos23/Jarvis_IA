import json
import pytz # Para colocar a data no fuso-horário local
from datetime import date, timedelta, datetime
# _*_coding: utf-8_*_

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

#Por meio da pergunta vai pegar os dados que correspondem
def responder_agenda(pergunta, periodo):
  compromissos = consultar_agenda_melhorada(periodo)

  # IA com problemas, alucinando com os dias da semana
  dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]

  if not compromissos:
    contexto_agenda = "Não existem compromissos agendados para este período."
  else:
    contexto_agenda = ""
    for c in compromissos:
      data_str = c.get('data','')
      if data_str:
        data_obj = datetime.strptime(data_str, "%d/%m/%Y")
        nome_dia = dias_semana[data_obj.weekday()]

        contexto_agenda += f"- [{data_str}] ({nome_dia}) {c['titulo'].upper()} ({c['tipo']}) às {c['horario']}.\n"
      else:
        contexto_agenda += f"- [Data Indisponível] {c['titulo'].upper()} ({c['tipo']}) às {c['horario']}.\n"

  fuso_local = pytz.timezone('America/Campo_Grande')
  hoje_atual = datetime.now(fuso_local)

  prompt_sistema = (
    "Você é o JARVIS. Responda à pergunta do usuário de forma natural, direta e amigável."
    "Regras ESTRITAS:\n"
    "1. NUNCA use frases robóticas como 'Baseado na agenda...' ou 'Você perguntou sobre...'. Vá direto ao ponto.\n"
    "2. Se uma data no contexto for anterior ao dia de hoje, informe que o evento já ocorreu.\n"
    "3. Se não houver compromissos, diga simplesmente que a agenda está livre.\n\n"
    "4. NÃO TENTE ADIVINHAR OS DIAS DA SEMANA. Use EXATAMENTE os dias que estão entre parênteses no contexto abaixo.\n\n"
    f"Hoje é: {hoje_atual.strftime('%d/%m/%Y')} ({dias_semana[hoje_atual.weekday()]})\n\n"
    f"Dados da agenda extraídos:\n{contexto_agenda}"
  )

  mensagens = [
    {"role": "system", "content": prompt_sistema},
    {"role": "user", "content": pergunta}
  ]

  resposta = client.chat.completions.create(
      model='google/gemma-3-12b-it',
      messages=mensagens,
      temperature=0.2,
  )

  return resposta.choices[0].message.content
