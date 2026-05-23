import json
from datetime import datetime
from pathlib import Path

# Importação de outras funções criadas
from config import client
from rag_busca_chunks import responder_rag
from agenda import responder_agenda
from lista_de_tarefas import adicionar_tarefa, limpar_tarefas, concluir_tarefa, listar_tarefas

src_projeto = Path(__file__).parent if "__file__" in locals() else Path.cwd()
raiz_projeto = src_projeto.parent

# Define as pastas de origem e destino
caminho_log = raiz_projeto / "jarvis_log.json"

def registrar_log(ferramenta, entrada, saida):

  agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

  with open(caminho_log, "a", encoding="utf-8") as arquivo:
    arquivo.write(f"[{agora}] ==========================\n")
    arquivo.write(f"FERRAMENTA CHAMADA : {ferramenta}\n")
    arquivo.write(f"ENTRADA (Parâmetro): {entrada}\n")
    arquivo.write(f"SAÍDA (Resultado)  :\n{saida}\n")
    arquivo.write("==================================================\n\n")

  print(f"Log registrado com sucesso para a ferramenta: {ferramenta}!")

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
  
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 INICIANDO TESTES DO ORQUESTRADOR JARVIS")
    print("="*50 + "\n")

    # 1. Testando Tarefas
    print(jarvis("Anota aí para eu revisar os códigos em VHDL do projeto amanhã cedo."))
    print("-" * 50)
    
    # 2. Testando Agenda
    print(jarvis("JARVIS, tenho alguma reunião com a Professora Daniela nesta semana?"))
    print("-" * 50)
    
    # 3. Testando o RAG (Conhecimento Técnico)
    print(jarvis("Quais as vantagens de aplicar computação aproximada em processadores RISC-V?"))
    print("\n" + "="*50)
