#!/usr/bin/env python3
"""MergeApp launcher – modern Tkinter UI with PDF utilities, auto‑update, and LGPD handling.
"""
import os
import sys
import json
import urllib.request
import tempfile
import subprocess
import tkinter as tk
from tkinter import messagebox

APP_DATA = os.path.join(os.getenv('APPDATA'), 'MergeApp')
os.makedirs(APP_DATA, exist_ok=True)

# ----- LGPD privacy notice ---------------------------------------------------
def show_privacy_notice():
    if not os.path.isfile(os.path.join(APP_DATA, 'privacy_accepted')):
        if messagebox.askyesno(
            "Política de Privacidade",
            "Este aplicativo processa arquivos PDF. Não armazenamos dados pessoais.\nClique em 'Sim' para aceitar.",
        ):
            open(os.path.join(APP_DATA, 'privacy_accepted'), 'w').close()
        else:
            sys.exit(0)

def delete_user_data():
    """Remove all files stored in APP_DATA (LGPD compliance)."""
    for entry in os.listdir(APP_DATA):
        try:
            os.remove(os.path.join(APP_DATA, entry))
        except Exception:
            pass
    messagebox.showinfo("Dados removidos", "Todos os dados da aplicação foram excluídos.")

# ----- Icon handling --------------------------------------------------------
def set_window_icon(root):
    custom_icon = os.path.join(APP_DATA, 'custom_icon.ico')
    if os.path.isfile(custom_icon):
        root.iconbitmap(custom_icon)

# ----- Auto‑update ----------------------------------------------------------
def check_for_updates():
    repo = "plenoryan/Merge"
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        with urllib.request.urlopen(api_url) as resp:
            data = json.load(resp)
        latest = data.get('tag_name')
        current_path = os.path.join(APP_DATA, 'current_version.txt')
        current = ''
        if os.path.isfile(current_path):
            current = open(current_path).read().strip()
        if latest != current:
            if messagebox.askyesno(
                "Atualização Disponível",
                f"Versão {latest} encontrada. Deseja atualizar?",
            ):
                asset = next(a for a in data['assets'] if a['name'].endswith('.exe'))
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.exe')
                urllib.request.urlretrieve(asset['browser_download_url'], tmp_file.name)
                exe_path = sys.argv[0]
                subprocess.run([sys.executable, '-c', f"import shutil, os; shutil.move(r'{tmp_file.name}', r'{exe_path}')"])
                open(current_path, 'w').write(latest)
                messagebox.showinfo("Atualização", "Aplicativo atualizado. Reinicie para aplicar.")
    except Exception as e:
        print(f"Erro ao verificar atualização: {e}")

# ----- Import PDF utilities -------------------------------------------------
# The PDF utilities are placed in src/pdf_utils.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
# Import the utility functions (names may need adjusting to actual function definitions)
try:
    from pdf_utils.compress_pdf import compress_pdf
except Exception:
    compress_pdf = lambda: messagebox.showinfo('Info', 'compress_pdf not implemented')
try:
    from pdf_utils.add_images_to_pdf import add_images_to_pdf
except Exception:
    add_images_to_pdf = lambda: messagebox.showinfo('Info', 'add_images_to_pdf not implemented')
try:
    from pdf_utils.remove_signature import remove_signature
except Exception:
    remove_signature = lambda: messagebox.showinfo('Info', 'remove_signature not implemented')
try:
    from pdf_utils.verify_pdfa import verify_pdfa
except Exception:
    verify_pdfa = lambda: messagebox.showinfo('Info', 'verify_pdfa not implemented')

def main():
    show_privacy_notice()
    root = tk.Tk()
    root.title("Merge PDFs – Versão 1.2.0")
    set_window_icon(root)
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Compress PDF", command=compress_pdf)
    filemenu.add_command(label="Add Images to PDF", command=add_images_to_pdf)
    filemenu.add_command(label="Remove Signature", command=remove_signature)
    filemenu.add_command(label="Verify PDF/A", command=verify_pdfa)
    filemenu.add_separator()
    filemenu.add_command(label="Delete Data (LGPD)", command=delete_user_data)
    filemenu.add_separator()
    filemenu.add_command(label="Check for Updates", command=check_for_updates)
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)
    root.geometry("400x200")
    tk.Label(root, text="Selecione a ação no menu ‘File’").pack(expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()
