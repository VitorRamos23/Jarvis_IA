# -*- coding: utf-8 -*-

from google.colab import drive
drive.mount('/content/drive')

# Crie uma pasta no seu Drive para salvar os artigos usados do projeto
import os
os.makedirs('/content/drive/MyDrive/Jarvis/Data', exist_ok=True)

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

import os

ARQUIVO_TAREFAS = "tarefas.json"

if not os.path.exists(ARQUIVO_TAREFAS):
    with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as arquivo:
        json.dump([], arquivo, indent=4, ensure_ascii=False)

def carregar_tarefas():
  with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as arquivo:
    return json.load(arquivo)

def salvar_tarefas(tarefas):
  with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as arquivo:
    json.dump(tarefas, arquivo, indent= 4, ensure_ascii=False)

def adicionar_tarefa(corpo):
  tarefas = carregar_tarefas()

  novo_id = 1 if not tarefas else max(t["id"] for t in tarefas) + 1

  nova_tarefa = {

      "id": novo_id,
      "corpo": corpo,
      "concluida": False
  }
  tarefas.append(nova_tarefa)
  salvar_tarefas(tarefas)
  return f"A tarefa [{novo_id}] {corpo} foi adicionada com sucesso"

def listar_tarefas():
  tarefas = carregar_tarefas()
  if not tarefas:
    return "Não há tarefas registradas."

  resposta = "Sua lista de tarefas:\n"
  for i in tarefas:
    status = "Concluída" if i["concluida"] else "Pendente"
    resposta += f"[ID: {i['id']}] {i['corpo']} [{status}]\n"
  return resposta

def concluir_tarefa(id):
  tarefas = carregar_tarefas()
  for i in tarefas:
    if i["id"] == int(id):
      if i["concluida"]:
        return f"A tarefa {id} já está concluída."
      i["concluida"] = True
      salvar_tarefas(tarefas)
      return f"A tarefa [{id}] {i['corpo']} foi marcada como concluída."
  return f"Não foi encontrada uma tarefa com o ID {id}."

def limpar_tarefas():
  # Cria uma lista vazia por cima da antiga
  salvar_tarefas([])
  return "A lista de tarefas foi limpa."

print("JARVIS já pode buscar tarefas!")

# o import do json já foi executado nas linhas acima.
# Não é necessário nesta parte

def gerenciar_tarefas_JARVIS(comando):

  prompt = """
  O usuário enviou um comando para gerenciar tarefas.
  Sua única função é classificar a intenção e extrair o parâmetro.

  Regras de Mapeamento:
  - Se o usuário quer criar/anotar algo -> acao: "adicionar", parametro: "corpo"
  - Se o usuário quer ver as tarefas/o que tem para hoje -> acao: "listar", parametro: ""
  - Se o usuário quer marcar uma tarefa como concluída/terminada/finalizada -> acao: "concluir", parametro: "somente o número do ID da tarefa"
  - Se o usuário quer apagar tudo/limpar a lista/ deletar todas as tarefas -> acao: "limpar", parametro: ""

  Responda EXCLUSIVAMENTE com um objeto JSON válido. Não escreva mais nada.
  Exemplo 1: {"acao": "adicionar", "parametro": "Estudar KNN para a prova"}
  Exemplo 2: {"acao": "listar", "parametro": ""}
  Exemplo 3: {"acao": "concluir", "parametro": "2"}
  Exemplo 4: {"acao": "limpar", "parametro": ""}
  """

  mensagens = [
    {"role": "system", "content": prompt},
    {"role": "user", "content": comando}
  ]

  try:
    # A API do modelo é chamada
    resposta = client.chat.completions.create(
        model='google/gemma-3-12b-it',
        messages=mensagens,
        temperature=0, # 0 Para ser o mais objetivo possível
        timeout=15.0
    ).choices[0].message.content

    # Limpeza de segurança (caso o modelo coloque o JSON dentro de blocos de código markdown)
    json_limpo = resposta.replace("```json", "").replace("```", "").strip()
    dados_json = json.loads(json_limpo)

    acao = dados_json.get("acao")
    parametro = dados_json.get("parametro")

    # Aciona o que a IA decidiu
    if acao == "adicionar":
      return adicionar_tarefa(parametro)
    elif acao == "listar":
      return listar_tarefas()
    elif acao == "concluir":
      return concluir_tarefa(parametro)
    elif acao == "limpar":
        return limpar_tarefas()
    else:
      return "Desculpe, não entendi o que você quer fazer."

  except Exception as e:
    return f"Ocorreu um erro: {e}"
print("JARVIS está conectado às tarefas!")

print(gerenciar_tarefas_JARVIS("JARVIS, pode deletar todas as tarefas da minha lista."))
print("-" * 50)

print(gerenciar_tarefas_JARVIS("Me mostra as tarefas agora."))
print("-" * 50)

# Teste 1: Adicionar (Note que a frase é natural, não é um comando de programação)
print(gerenciar_tarefas_JARVIS("JARVIS, anota aí pra eu terminar o relatório de circuitos aproximados mais tarde."))
print("-" * 50)

print(gerenciar_tarefas_JARVIS("Preciso de adicionar uma tarefa para verificar os ficheiros VHDL."))
print("-" * 50)

# Teste 2: Listar
print(gerenciar_tarefas_JARVIS("Mostra-me a minha lista de tarefas, por favor."))
print("-" * 50)

# Teste 3: Concluir (Use o ID que ele gerou no Teste 1)
print(gerenciar_tarefas_JARVIS("Já finalizei a tarefa número 3!"))
print("-" * 50)

print(gerenciar_tarefas_JARVIS("Já finalizei a tarefa número 2!"))
print("-" * 50)

# Verificando se a lista atualizou
print(gerenciar_tarefas_JARVIS("Como está a lista agora?"))

LOG = "jarvis_log.txt"

def registrar_log(ferramenta, entrada, saida):

  agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

  with open(LOG, "a", encoding="utf-8") as arquivo:
    arquivo.write(f"[{agora}] ==========================\n")
    arquivo.write(f"FERRAMENTA CHAMADA : {ferramenta}\n")
    arquivo.write(f"ENTRADA (Parâmetro): {entrada}\n")
    arquivo.write(f"SAÍDA (Resultado)  :\n{saida}\n")
    arquivo.write("==================================================\n\n")

  print(f"*Log registrado com sucesso para a ferramenta: {ferramenta}!*")

print("Sistema de registrado ativado")

def jarvis(comando):
  """
  Esta função chama todas as ferramentas criadas para o funcionamento
  do JARVIS
  """
  prompt = """
  Olá JARVIS. Analise o pedido do usuário e decida qual ferramenta utilizar.
  Você possui EXATAMENTE 6 ferramentas:

  1. "buscar_material_rag": Para perguntas técnicas, conceitos ou dúvidas sobre os PDFs arquivados.
    - parametro: a pergunta EXATA do usuário.
  2. "consultar_agenda": Para verificar compromissos, aulas ou provas.
    - parametro: APENAS a palavra "hoje", "amanha", "semana" ou "proxima_semana". (Se o usuário disser 'que vem', use 'proxima_semana').
  3. "adicionar_tarefa": Para anotar, lembrar ou criar uma nova tarefa.
    - parametro: a descrição da tarefa.
  4. "listar_tarefas": Para ver a lista de tarefas.
    - parametro: "nenhum"
  5. "concluir_tarefa": Para finalizar/marcar uma tarefa como concluída.
    - parametro: APENAS o número do ID da tarefa (exemplo: "2").
  6. "limpar_tarefas": Para apagar, deletar ou limpar toda a lista de tarefas.
    - parametro: "nenhum"

  Responda EXCLUSIVAMENTE com um objeto JSON válido. Não escreva mais nada:
  {"ferramenta": "nome_da_ferramenta", "parametro": "valor"}
  """

  mensagens = [
    {"role": "system", "content": prompt},
    {"role": "user", "content": comando}
  ]

  try:
    resposta = client.chat.completions.create(
        model='google/gemma-3-12b-it',
        messages=mensagens,
        temperature=0, # 0 Para ser o mais objetivo possível
        timeout=15.0
    ).choices[0].message.content

    # Remove as crases de formatação do Markdown
    json_limpo = resposta.replace("```json", "").replace("```", "").strip()

    # Remove barras invertidas que o LLM possa ter alucinado
    json_limpo = json_limpo.replace("\\", "")

    dados_json = json.loads(json_limpo)

    ferramenta = dados_json.get("ferramenta")
    parametro = dados_json.get("parametro")

    if ferramenta == "buscar_material_rag":
      # O (, _) garante que pegue só o texto
      resultado_final, _ = responder_rag(parametro, metodo="hibrido", k=10)

    elif ferramenta == "consultar_agenda":
      # Colocando a função responder_agenda garante respostas melhores
      resultado_final = responder_agenda(comando, parametro)

    elif ferramenta == "adicionar_tarefa":
      resultado_final = adicionar_tarefa(parametro)

    elif ferramenta == "listar_tarefas":
      resultado_final = listar_tarefas()

    elif ferramenta == "concluir_tarefa":
      resultado_final = concluir_tarefa(parametro)

    elif ferramenta == "limpar_tarefas":
      resultado_final = limpar_tarefas()

    else:
      resultado_final = "Desculpe, não entendi o que você quer fazer."

    # Registra a ação no LOG
    registrar_log(ferramenta, parametro, str(resultado_final))

    return resultado_final

  except Exception as e:
    erro_msg = f"Erro no JARVIS: {str(e)}"
    registrar_log("FALHA_SISTEMA", comando, erro_msg)
    return erro_msg

# Teste de Roteamento de Agente (A IA decide sozinha para onde ir!)

print(jarvis("Quais são as vantagens de usar circuitos aproximados?")) # Vai para o RAG
print("-" * 60)

print(jarvis("Tenho aula de quê amanhã?")) # Vai para a Agenda
print("-" * 60)

print(jarvis("Adiciona uma tarefa para rever a matéria de VHDL.")) # Vai para Adicionar Tarefa
print("-" * 60)

print(jarvis("Mostra as minhas tarefas aí.")) # Vai para Listar Tarefas
print("-" * 60)

import time

print("="*60)
print("🔌 JARVIS ONLINE - Sistema Integrado de Assistência Acadêmica")
print("Digite 'sair' para desligar o sistema.")
print("="*60)

while True:
    try:
        # Recebe o comando do usuário
        entrada_usuario = input("\n👤 Você: ")

        # Condição de parada
        if entrada_usuario.lower() in ['sair', 'exit', 'desligar']:
            print("🤖 JARVIS: Encerrando sistemas. Bom trabalho!")
            break

        if not entrada_usuario.strip():
            continue

        print("🤖 JARVIS: Processando...")

        # Chama o Agente Master
        resposta = jarvis(entrada_usuario)

        # Imprime a resposta formatada
        print(f"\n>> {resposta}")
        time.sleep(0.5) # Pausa dramática para parecer mais natural

    except KeyboardInterrupt:
        # Se você apertar o botão de parar (Stop) do Colab
        print("\n🤖 JARVIS: Execução interrompida à força. Desligando.")
        break

import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

nest_asyncio.apply()

#Talvez precise mudar
BOT_TOKEN = "8639629066:AAGHC1AVMacQdUnwTvt5JTF0hIJJJdh8JYU"

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    boas_vindas = "JARVIS ONLINE. Olá meu Homem de Ferro. Como posso ajudar?"
    await update.message.reply_text(boas_vindas)

async def processar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem_usuario = update.message.text

    mensagem_espera = await update.message.reply_text("JARVIS: Processando...")

    try:
      resposta_jarvis = jarvis(mensagem_usuario)
      await mensagem_espera.edit_text(resposta_jarvis)

    except Exception as e:
      await mensagem_espera.edit_text(f"Erro no sistema: {e}")

print("Iniciando conexão com o Telegram...")
app = ApplicationBuilder().token(BOT_TOKEN).build()

print("Registrando comandos...")
app.add_handler(CommandHandler("start", comando_start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_mensagem))

print("JARVIS está online no Telegram!")
app.run_polling()
