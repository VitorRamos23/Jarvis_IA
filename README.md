# JARVIS Acadêmico

Projeto desenvolvido para a disciplina de Inteligência Artificial.  
O JARVIS Acadêmico é um assistente virtual capaz de responder perguntas sobre materiais em PDF, consultar agenda e gerenciar tarefas pelo Telegram.

## Funcionalidades

- Conversão de PDFs para Markdown
- Busca em materiais acadêmicos usando RAG
- Busca léxica com BM25
- Busca semântica com FAISS e Sentence Transformers
- Consulta de agenda acadêmica
- Gerenciamento de tarefas
- Integração com bot do Telegram
- Registro de ações em arquivo de log

## Tecnologias Utilizadas

- Python
- FAISS
- BM25
- Sentence Transformers
- Telegram Bot API
- OpenAI SDK
- Google Colab
- Gemini AI (auxílio no desenvolvimento)

## Estrutura do Projeto

```text
Jarvis_IA-main/
│
├── Data/                 # PDFs usados como base de conhecimento
├── Markdown/             # Arquivos convertidos de PDF para Markdown
├── src/
│   ├── agenda.py
│   ├── bot_telegram.py
│   ├── config.py
│   ├── conversao.py
│   ├── criacao_de_pasta.py
│   ├── lista_de_tarefas.py
│   ├── rag_busca_chunks.py
│   └── tool_calling.py
│
├── .env
├── README.md
```

# COMO EXECUTAR - Linux

##Pré-requisito 
```bash
  apt install python3.12-venv
```
## Passo 1 — Criar o ambiente virtual

```bash
python3 -m venv venv
```

## Passo 2 — Ativar o ambiente virtual

```bash
source venv/bin/activate
```

## Passo 3 — Instalar as dependências

```bash
pip install openai python-dotenv
pip install -U docling transformers sentence-transformers
pip install -qU rank_bm25 faiss-cpu
pip install -qU python-telegram-bot nest_asyncio
pip install pytz
```

## Passo 4 — Executar o projeto

```bash
python3 src/conversao.py
python3 src/bot_telegram.py
```


## Passo 5 Acessar o bot no Telegram

http://t.me/jarvis_ufms_ia_bot

O comando de inicialização é 
```bash
/start
```
---
# Link
Caso queira acessar pelo Google Colab, segue o link para o notebook:

https://colab.research.google.com/drive/1iLglylzi4_hBEwvGvhZZKwTrwgMizIL3?usp=sharing
