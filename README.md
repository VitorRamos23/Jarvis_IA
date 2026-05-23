### Passo 1 - Acessando o Ambiente Virtual

Para acessar o Ambiente virtual é necessario 
### 1. Cria a bolha (isso vai fazer a pasta venv aparecer aí na sua imagem)
python3 -m venv venv

### 2. Entra na bolha (ativa o ambiente)
source venv/bin/activate



### Passo 2 — Instalar as dependências

Execute as células de instalação no topo do notebook, uma por vez:

```bash
pip install openai python-dotenv
pip install -U docling transformers sentence-transformers
pip install -qU rank_bm25 faiss-cpu
pip install -qU python-telegram-bot nest_asyncio
pip install pytz
```

---

### Passo 3 — Montar o Google Drive

Execute a célula abaixo e autorize o acesso quando solicitado:

```python
from google.colab import drive
drive.mount('/content/drive')
```

Após montar, crie a pasta onde os PDFs ficarão:

```python
import os
os.makedirs('/content/drive/MyDrive/Jarvis/Data', exist_ok=True)
```

---

### Passo 4 — Adicionar os PDFs

Acesse o seu **Google Drive → Jarvis → Data** e faça upload dos arquivos PDF que o JARVIS usará como base de conhecimento.

O projeto já vem com PDFs de exemplo na pasta `Data/` do repositório.

---

### Passo 5 — Converter os PDFs em Markdown

Execute a célula **"Transformando PDF em MD"** no notebook.

O script lê cada `.pdf` da pasta `Data/`, converte para texto e salva como `.md` na pasta `Markdown/`. Isso pode levar alguns minutos dependendo do tamanho dos arquivos.

Saída esperada:
```
Iniciando conversão em lote...
Processando: i5.pdf ... OK
Processando: ia1.pdf ... OK
...
```

---

### Passo 6 — Construir os índices de busca

Execute a célula **"Criando as Chunks"** no notebook.

Ela divide os textos em trechos menores (chunks) e constrói dois índices de busca:

- **BM25** — encontra trechos por palavras-chave
- **FAISS** — encontra trechos por similaridade de significado

Saída esperada:
```
JARVIS Atualizado! BM25 e FAISS prontos para busca híbrida.
```

---

### Passo 7 — Configurar o cliente do LLM

Localize a célula com a configuração do modelo e insira a chave fornecida pelo professor:

```python
from openai import OpenAI
from google.colab import userdata

client = OpenAI(
    base_url='https://llm.liaufms.org/v1/gemma-3-12b-it',
    api_key=userdata.get('CHAVE_API')  # salve sua chave em Colab > Secrets
)
```

> Para salvar a chave com segurança: no Colab, acesse o ícone de 🔑 **Secrets** no menu lateral, crie uma entrada chamada `CHAVE_API` e cole a chave lá.

---

### Passo 8 — Testar o JARVIS

Execute as células de teste no notebook para confirmar que tudo está funcionando:

```python
# Perguntar sobre os PDFs
print(jarvis("O que é computação aproximada?"))

# Consultar a agenda
print(jarvis("O que tenho para hoje?"))
print(jarvis("Tenho alguma prova essa semana?"))

# Gerenciar tarefas
print(jarvis("Anota: estudar KNN para a prova"))
print(jarvis("Quais são minhas tarefas?"))
print(jarvis("Concluir tarefa 1"))
```

---

### Passo 9 — Ativar o bot no Telegram (opcional)

**9.1** Abra o arquivo `src/bot_telegram.py` e substitua o token:

```python
BOT_TOKEN = "SEU_TOKEN_AQUI"  # token gerado pelo @BotFather
```

**9.2** Execute a última célula do notebook que inicializa o bot:

```python
app.run_polling()
```

**9.3** Abra o Telegram, procure o seu bot pelo nome e envie `/start`.

A partir daí, basta conversar normalmente — o JARVIS responde perguntas, consulta a agenda e gerencia suas tarefas direto pelo chat.

---

## Como o JARVIS decide o que fazer

Toda mensagem passa pelo `Tool_Calling.py`, que envia o texto ao LLM. O modelo lê o pedido e retorna qual das 6 ações executar:

| Ação | Quando é usada |
|---|---|
| `buscar_material_rag` | Perguntas sobre os PDFs indexados |
| `consultar_agenda` | Compromissos de hoje, amanhã ou na semana |
| `adicionar_tarefa` | Anotar algo novo na lista |
| `listar_tarefas` | Ver todas as tarefas |
| `concluir_tarefa` | Marcar uma tarefa como feita |
| `limpar_tarefas` | Apagar toda a lista |

Cada ação executada é salva automaticamente no arquivo `jarvis_log.txt`.
