import json
import pytz # Para colocar a data no fuso-horário local
from datetime import date, timedelta, datetime
from pathlib import Path
from config import client

src_projeto = Path(__file__).parent if "__file__" in locals() else Path.cwd()
raiz_projeto = src_projeto.parent

# Define as pastas de origem e destino
caminho_agenda = raiz_projeto / "agenda.json"

def inicializar_agenda():
    if caminho_agenda.exists():
        return

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
                {
            "titulo": "Futebol",
            "tipo": "reuniao",
            "horario": "19:30 - 22:00",
            "recorrencia": "semanal",
            "dia_de_semana": 1 # terça feira
        },
        # Compromissos Únicos (data específica)
        {
            "titulo": "Prova de Banco de Dados",
            "tipo": "prova",
            "horario": "07:15 - 09:15",
            "recorrencia": "unica",
            "data": "26/05/2026"
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
            "data": "29/05/2026"
        }
        {
            "titulo": "Prova de Calculo",
            "tipo": "prova",
            "horario": "13:15 - 15:05",
            "recorrencia": "unica",
            "data": "02/06/2026"
        }
    ]

    with open(caminho_agenda, "w", encoding= "utf-8") as arquivo:
        json.dump(agenda, arquivo, indent=4, ensure_ascii=False)
    print(f"Agenda salva em {caminho_agenda} e pronta para os testes")
  
inicializar_agenda()

def consultar_agenda_melhorada(periodo="hoje"):
  # Vai considerar compromissos recorrentes ao longo das semanas

  with open(caminho_agenda, "r", encoding="utf-8") as arquivo:
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
  """
  Monta o contexto e pede para Gemma-3 formular a resposta falada.
  """
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
    "2. EVENTOS PASSADOS: Verifique a data e o HORÁRIO. Se a data for anterior a hoje, OU se for hoje mas o horário de término já passou da 'Hora Atual', informe claramente que o evento já ocorreu/já acabou.\n"
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

if __name__ == "__main__":
    # Teste 1: Consulta Diária
    print(responder_agenda("O que tenho para hoje?", "hoje"))
    print("-" * 60)

    # Teste 2: Consulta Crítica (Provas)
    print(responder_agenda("Tenho alguma prova amanhã?", "amanha"))
    print("-" * 60)

    # Teste 3: Visão Semanal
    print(responder_agenda("Quais são as minhas aulas esta semana?", "semana"))
