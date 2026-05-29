import sys
from pathlib import Path
from tkinter import Tk, filedialog, messagebox
from pypdf import PdfReader, PdfWriter

def separar_pdf(arquivo_pdf: Path, pasta_saida: Path):
    pasta_saida.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(str(arquivo_pdf))
    for i, pagina in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(pagina)
        filename = pasta_saida / f"pagina_{i}.pdf"
        with open(filename, "wb") as f:
            writer.write(f)
    print(f"PDF separado em {len(reader.pages)} páginas.")

def main():
    if len(sys.argv) < 2:
        print("Use: separar_pdf.exe <arquivo_pdf_ou_diretorio>")
        return

    root = Tk()
    root.withdraw()  # oculta a janela principal

    caminho_ori = Path(sys.argv[1])

    # Se é diretório, pedido para selecionar um arquivo pdf dentro
    if caminho_ori.is_dir():
        arquivos_pdf = list(caminho_ori.glob("*.pdf"))
        if not arquivos_pdf:
            messagebox.showerror("Erro", "Diretório não contém PDFs.")
            return
        arquivo_pdf = arquivos_pdf[0]  # ou outra lógica para escolher
    else:
        arquivo_pdf = caminho_ori

    pasta_saida = filedialog.askdirectory(title="Selecione pasta para salvar páginas")
    if not pasta_saida:
        messagebox.showinfo("Cancelado", "Nenhuma pasta selecionada.")
        return

    try:
        separar_pdf(arquivo_pdf, Path(pasta_saida))
        messagebox.showinfo("Concluído", f"PDF separado em {len(PdfReader(str(arquivo_pdf)).pages)} páginas.\nPasta: {pasta_saida}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao separar PDF:\n{e}")

if __name__ == "__main__":
    main()
