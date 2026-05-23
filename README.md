Pips

# 1. Cria a bolha (isso vai fazer a pasta venv aparecer aí na sua imagem)
python3 -m venv venv

# 2. Entra na bolha (ativa o ambiente)
source venv/bin/activate

# 3. Instala as bibliotecas de vez
pip install openai python-dotenv

# OpenIA
!pip install openai python-dotenv

# Transformando PDF em MD
!pip -q install -U docling transformers sentence-transformers


# Criando as Chunks
!pip install -qU rank_bm25 faiss-cpu sentence-transformers

# Bot telegram
!pip install -qU python-telegram-bot nest_asyncio
