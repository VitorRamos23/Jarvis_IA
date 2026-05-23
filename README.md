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
└── Jarvis_IA_Traduzido.ipynb


# COMO EXECUTAR

# Passo 1 - Acessando o Ambiente Virtual

Para acessar o Ambiente virtual é necessario 
### 1. Cria a bolha (isso vai fazer a pasta venv aparecer aí na sua imagem)
python3 -m venv venv

### 2. Entra na bolha (ativa o ambiente)
source venv/bin/activate



# Passo 2 — Instalar as dependências

Execute as células de instalação no topo do notebook, uma por vez:

```bash
pip install openai python-dotenv
pip install -U docling transformers sentence-transformers
pip install -qU rank_bm25 faiss-cpu
pip install -qU python-telegram-bot nest_asyncio
pip install pytz
```

python3 conversao.py
# Passo 3 — Ativar o bot no Telegram 
