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
