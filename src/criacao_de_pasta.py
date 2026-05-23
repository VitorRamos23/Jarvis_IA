from pathlib import Path

src_projeto = Path(file).parent if "file" in locals() else Path.cwd()

raiz_projeto = src_projeto.parent

#Aponta para as pastas 'Data' e 'Markdown' dentro do seu projeto
pasta_pdf = raiz_projeto / "Data"
pasta_md = raiz_projeto / "Markdown"

#Cria as pastas caso elas não existam (exist_ok=True impede erros se já existirem)
pasta_pdf.mkdir(parents=True, exist_ok=True)
pasta_md.mkdir(parents=True, exist_ok=True)

print(f"Diretório de PDFs (Origem): {pasta_pdf.resolve()}")
print(f"Diretório de Markdown (Destino): {pasta_md.resolve()}")
