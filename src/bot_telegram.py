import os
from dotenv import load_dotenv
from pathlib import Path
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from tool_calling import jarvis

src_projeto = Path(__file__).parent if "__file__" in locals() else Path.cwd()
raiz_projeto = src_projeto.parent

caminho_env = raiz_projeto / ".env"
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not BOT_TOKEN:
   raise ValueError ("Token do Telegram não encontrado! Verifique o arquivo .env.")


#Funções do Bot

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    boas_vindas = "JARVIS ONLINE. Olá meu Homem de Ferro. Como posso ajudar?"
    await update.message.reply_text(boas_vindas)

async def processar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem_usuario = update.message.text

    mensagem_espera = await update.message.reply_text("JARVIS: Processando...")

    try:
      resposta_jarvis = jarvis(mensagem_usuario)
      await mensagem_espera.edit_text(resposta_jarvis)

    except Exception as e:
      await mensagem_espera.edit_text(f"Erro no sistema: {e}")

print("Iniciando conexão com o Telegram...")
app = ApplicationBuilder().token(BOT_TOKEN).build()

print("Registrando comandos...")
app.add_handler(CommandHandler("start", comando_start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_mensagem))

print("JARVIS está online no Telegram!")
app.run_polling()
