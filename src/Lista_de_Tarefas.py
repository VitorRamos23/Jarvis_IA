# -*- coding: utf-8 -*-
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
