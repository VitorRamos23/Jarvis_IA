# -*- coding: utf-8 -*-



# Importa a biblioteca da OpenIA e o dados do usuário conectado ao google
from openai import OpenAI
from google.colab import userdata

# Configura o cliente usando os dados dispostos pelo professor
client = OpenAI(base_url='https://llm.liaufms.org/v1/gemma-3-12b-it', api_key='Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A')

# Executa um teste para obter resposta do JARVIS
try:
  resp = client.chat.completions.create(
      model='google/gemma-3-12b-it',
      messages=[{'role': 'user', 'content': 'Hi'}],
  )

  print("Sucesso! Resposta do JARVIS:")
  print(resp.choices[0].message.content)

except Exception as e:
  print(f"Erro na conexão: {e}")

