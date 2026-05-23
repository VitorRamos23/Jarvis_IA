import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
# _*_coding: utf-8_*_

nest_asyncio.apply()

#Talvez precise mudar
BOT_TOKEN = "8639629066:AAGHC1AVMacQdUnwTvt5JTF0hIJJJdh8JYU"

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
