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

### Sugestões de Perguntas

```bash
Tenho aula essa semana?
Tenho Prova esta semana?
Quando foi criada a IA?
Qual a base de IA?
```

---
# Link
Caso queira acessar pelo Google Colab, segue o link para o notebook:

https://colab.research.google.com/drive/1iLglylzi4_hBEwvGvhZZKwTrwgMizIL3?usp=sharing

# Ocorrências e Soluções

Durante o desenvolvimento do projeto surgiram diversas dúvidas e desafios relacionados à implementação do JARVIS Acadêmico.

Uma das principais dúvidas ocorreu na criação dos *chunks* para o sistema RAG. Foram consideradas três abordagens: por tamanho fixo, por parágrafo e por janela deslizante. A abordagem por parágrafo acabou sendo descartada, pois alguns artigos possuíam parágrafos muito extensos enquanto outros apresentavam parágrafos extremamente curtos, gerando uma grande inconsistência nos dados processados. Por esse motivo, optamos pelo método de janela deslizante (*sliding window*), que apresentou resultados mais eficientes e equilibrados para o projeto. Apesar disso, as demais implementações permaneceram disponíveis no código para testes futuros.

Outro ponto importante foi a escolha entre busca léxica, busca semântica ou busca híbrida. Decidimos utilizar a busca híbrida, combinando BM25 com embeddings semânticos, pois essa abordagem atendia melhor às necessidades do projeto, trazendo resultados mais relevantes nas consultas realizadas pelo usuário.

Na implementação da agenda acadêmica, nossa ideia inicial consistia em uma agenda estática, contendo apenas dia, data, horário, tipo e título do compromisso. Entretanto, percebemos que esse modelo era ineficiente para compromissos recorrentes, como atividades semanais. Para solucionar esse problema, dividimos a agenda em duas categorias: compromissos únicos e compromissos recorrentes, tornando o sistema mais flexível e funcional.

Já na lista de tarefas, implementamos as funções de adicionar, listar, concluir e limpar tarefas. Essa parte do projeto foi desenvolvida sem grandes dificuldades.

O módulo de *tool calling* foi desenvolvido como o núcleo central do sistema, sendo responsável por coordenar e chamar todas as demais funcionalidades do JARVIS.

Para a execução do projeto, utilizamos tanto o BotFather do Telegram quanto a execução diretamente pelo terminal do usuário. Inicialmente, nossa ideia era disponibilizar apenas a versão integrada ao Telegram. No entanto, percebemos que seria necessário instalar o aplicativo do Telegram para utilizar o sistema, então decidimos também manter uma versão executável via terminal, ampliando as possibilidades de uso.

Toda a implementação foi realizada inicialmente no Google Colab. Porém, como o JARVIS precisava ser executado localmente, encontramos dificuldades relacionadas ao acesso aos arquivos e diretórios, já que parte do sistema estava integrada ao Google Drive. Outro desafio enfrentado foi a divisão do código em múltiplos arquivos dentro da pasta `src`, exigindo uma melhor organização e comunicação entre os módulos do projeto.

