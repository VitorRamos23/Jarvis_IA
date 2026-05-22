# -*- coding: utf-8 -*-

!pip -q install -U docling transformers sentence-transformers

from docling.document_converter import DocumentConverter
from pathlib import Path


# Define as pastas de origem e destino
pasta_pdf = Path('/content/drive/MyDrive/Jarvis/Data')
pasta_md = Path('/content/drive/MyDrive/Jarvis/Markdown')

pasta_md.mkdir(parents=True, exist_ok=True)

print(f"Iniciando conversão em lote...\nOrigem: {pasta_pdf}\nDestino: {pasta_md}\n")
converter = DocumentConverter()
contador = 0

# Conversão dos PDFs
for arquivo_pdf in pasta_pdf.glob("*.pdf"):
    print(f"Processando: {arquivo_pdf.name}...")

    try:
        # Conversão do pdf para markdown
        resultado = converter.convert(arquivo_pdf)
        texto_markdown = resultado.document.export_to_markdown()

        # Define a saída como .md
        caminho_saida = pasta_md / arquivo_pdf.with_suffix(".md").name

        # Salva o arquivo
        caminho_saida.write_text(texto_markdown, encoding="utf-8")

        print(f"Salvo como: {caminho_saida.name}")
        contador += 1

    except Exception as e:
        print(f"Erro ao converter {arquivo_pdf.name}: {e}")

print(f"\nConversão concluída! {contador} arquivos Markdown gerados e salvos no Drive.")

def chunking_fixo(texto, tamanho=500):
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        chunks.append(texto[inicio:fim])
        inicio = fim
    return chunks

def chunking_janela(texto, tamanho=500, sobreposicao=100):
    if sobreposicao >= tamanho:
        raise ValueError(f"sobreposicao ({sobreposicao}) deve ser menor que tamanho ({tamanho})")
    chunks = []
    passo = tamanho - sobreposicao
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        chunks.append(texto[inicio:fim])
        inicio += passo
    return chunks

def chunking_paragrafo(texto, min_chars=100):
    paragrafos = [p.strip() for p in texto.split("\n\n")]
    return [p for p in paragrafos if len(p) >= min_chars]

# ── NOVA CAMADA: GERENCIADOR DE BIBLIOTECA ────────────────────────────────────

def carregar_e_processar_biblioteca(pasta_origem, estrategia="janela"):
    """
    Lê todos os arquivos .md da pasta e aplica a estratégia escolhida.
    """
    todos_os_chunks = []

    print(f"Processando biblioteca em: {pasta_md}")

    for arquivo_md in pasta_md.glob("*.md"):
        texto_raw = arquivo_md.read_text(encoding="utf-8")

        # Seleciona a estratégia que será implementada nas chunks
        if estrategia == "fixo":
            brutos = chunking_fixo(texto_raw)
        elif estrategia == "janela":
            brutos = chunking_janela(texto_raw)
        else:
            brutos = chunking_paragrafo(texto_raw)

        # Responsável por definir qual a fonte dos dados selecionados
        for i, trecho in enumerate(brutos):
            if trecho.strip():
                todos_os_chunks.append({
                    "id": f"{arquivo_md.stem}_{i:03d}",
                    "fonte": arquivo_md.name,
                    "conteudo": trecho.strip()
                })

    print(f"Sucesso! {len(todos_os_chunks)} chunks carregadas.")
    return todos_os_chunks
