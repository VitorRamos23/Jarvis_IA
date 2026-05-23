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
- Rag fornecido pelo professor no AVA
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
│   ├── terminal.py
│   └── tool_calling.py
│
├── .env
├── README.md
```

# COMO EXECUTAR - Linux

## Pré-requisito

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

## Passo 4 — Converter Arquivos pdf para md

```bash
python3 src/conversao.py

```


## Passo 5 Executando o Jarvis

### Passo 5.1 Ativando e utilizando o Jarvis no Telegram

O telegram deve estar baixado ou na sua maquina ou no seu celular

```bash
python3 src/bot_telegram.py
```
### link para o bot no Telegram

http://t.me/jarvis_ufms_ia_bot

O comando de inicialização é 
```bash
/start
```
### Passo 5.2 Ativiando e utilizando o Jarvis no Terminal

```bash
python3 src/terminal.py
```

---
# Link
Caso queira acessar pelo Google Colab, segue o link para o notebook:

https://colab.research.google.com/drive/1iLglylzi4_hBEwvGvhZZKwTrwgMizIL3?usp=sharing

# Ocorrencias e Soluções

Uma das duvidas que tivemos foi para criação de Chunks, onde consideramos as formas: janela, fixa e por paragrafo. Foi escolhida a de janela pois dependendo do artigo poderiamos ter paragrafos de 10 linhas ou paragrafos de 3 linhas, isso seria uma mudança muito grande o que nos fez optar por utilizar a janela que é a mais eficiente dos 3 metodos.
Sobre a Busca Lexica e Semantica escolhemos utilizar a Hibrida pois ela completaria melhor o que nosso trabalho necessitava.
As outras funções ficaram no codigo mas para o experimento foi utilizado somente a Janela e a hibrida.
Para a Agenda nossa primeira ideia foi fazer uma agenda estatica onde ela receberia o dia, uma data seu tipo, o horario e o titulo. No entando, para compromissos recorrentes que ocorressem toda semana ela era ineficiente, na nova agenda devidimos ela em duas formas, uma para compromissos unicos e outra para compromissos corriqueiros.
Para a Lista de Tarefas colocamos as funções adicionar, listar, concluir e limpar, sem grandes problemas.
No toolcalling ele é o mestre que chama todos os outros.
Para execução do Jarvis utilizamos tanto o botfather do Telegram quanto o próprio terminal do usúario, nossa ideia inicial era utilizarmos somente o bot do Telegram mas como tivemos problemas pois era necessario instalar o telegram para utiliza-lo, optamos por também deixar disponivel a versão para o terminal.
Toda nossa implementação foi realizada no google colab, no entanto como era necessario que o Jarvis fosse acessado localmente tivemos alguns problemas com o acesso as pastas pois ela estava acessando no Drive. A dvisão do codigo em diferentes arquivos presentes na pasta src foi um desafio também.

