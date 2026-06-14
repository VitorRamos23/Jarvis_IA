from docling.document_converter import DocumentConverter
from pathlib import Path

src_projeto = Path(__file__).parent if "__file__" in locals() else Path.cwd()
raiz_projeto = src_projeto.parent

# Define as pastas de origem e destino
pasta_pdf = raiz_projeto / "Data"
pasta_md = raiz_projeto / "Markdown"

pasta_pdf.mkdir(parents=True, exist_ok=True)
pasta_md.mkdir(parents=True, exist_ok=True)


print(f"Iniciando conversão em lote...\nOrigem: {pasta_pdf}\nDestino: {pasta_md}\n")
converter = DocumentConverter()
contador = 0
pulados = 0 # Contador para caso o arquivo já exista

# Conversão dos PDFs
for arquivo_pdf in pasta_pdf.glob("*.pdf"):

    print(f"Iniciado a conversão")

    caminhos_saida = pasta_md / arquivo_pdf.with_suffix(".md").name

    if caminhos_saida.exists():
        print(f"O arquivo {caminhos_saida.name} já existe. Pulando...")
        pulados += 1
        continue

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

print(f"\nConversão concluída! {contador} arquivos Markdown gerados e salvos na pasta Markdown.")
print(f"- {pulados} arquivos já existentes foram ignorados.")
