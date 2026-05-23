# -*- coding: utf-8 -*-
# Importa a biblioteca da OpenIA e o dados do usuário conectado ao google
import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path


src_projeto = Path(__file__).parent if "__file__" in locals() else Path.cwd()
raiz_projeto = src_projeto.parent

caminho_env = raiz_projeto / ".env"

load_dotenv(dotenv_path=caminho_env)

chave_api = os.getenv("API_KEY_LIA")

if not chave_api:
  raise ValueError("Chave  API não encontrada! Verifique o arquivo .env.")

# Configura o cliente usando os dados dispostos pelo professor
client = OpenAI(base_url='https://llm.liaufms.org/v1/gemma-3-12b-it', api_key='Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A')

# Executa um teste para obter resposta do JARVIS
if __name__ == "__main__":
  try:
    resp = client.chat.completions.create(
      model='google/gemma-3-12b-it',
      messages=[{'role': 'user', 'content': 'Hi'}],
    )

    print("Sucesso! Resposta do JARVIS:")
    print(resp.choices[0].message.content)

  except Exception as e:
    print(f"Erro na conexão: {e}")
