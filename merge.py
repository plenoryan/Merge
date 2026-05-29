#!/usr/bin/env python3
"""Merge PDFs — interface simples (Tkinter) + pypdf (PdfWriter.append).
Melhorias:
- Drag & drop (quando tkinterdnd2 está disponível).
- Opções (engrenagem) para salvar último diretório, alterar diretório padrão e nome de saída.
- Cursor 'move' ao arrastar itens da lista.
- Compatível com PyInstaller (resource_path).
"""
from __future__ import annotations
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import platform
from typing import List, Iterable
import json
import re
import os

try:
    from pypdf import PdfWriter
except Exception as exc:
    raise RuntimeError("pypdf não encontrado. Instale com: pip install pypdf") from exc

# --- Optional drag & drop support via tkinterdnd2 ---
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES  # type: ignore
    _DND_AVAILABLE = True
except Exception:
    TkinterDnD = None
    DND_FILES = None
    _DND_AVAILABLE = False

CONFIG_PATH = Path.home() / ".merge_pdf_config.json"


def resource_path(name: str) -> Path:
    """Retorna caminho absoluto para recursos, compatível com PyInstaller."""
    if getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS) / name
    try:
        return Path(__file__).resolve().parent / name
    except NameError:
        return Path(".") / name


def _expand_dir_to_pdfs(dirpath: Path) -> List[Path]:
    """Retorna lista de arquivos .pdf dentro do diretório (não-recursivo), ordenados por nome."""
    out = []
    try:
        for p in sorted(dirpath.iterdir(), key=lambda q: q.name.lower()):
            if p.is_file() and p.suffix.lower() == ".pdf":
                out.append(p.resolve())
    except Exception:
        pass
    return out


def resolve_pdfs(paths: Iterable[str]) -> List[Path]:
    """
    Filtra e resolve apenas arquivos .pdf existentes, mantendo ordem e sem duplicatas.
    Aceita tanto arquivos quanto diretórios (diretórios serão expandidos para *.pdf).
    """
    seen = set()
    out: List[Path] = []
    for p in paths:
        if not p:
            continue
        try:
            path = Path(p).expanduser().resolve()
        except Exception:
            continue
        if path.is_dir():
            for f in _expand_dir_to_pdfs(path):
                if str(f) not in seen:
                    seen.add(str(f))
                    out.append(f)
        else:
            if path.suffix.lower() == ".pdf" and path.exists():
                if str(path) not in seen:
                    seen.add(str(path))
                    out.append(path)
    return out


def open_folder(path: Path) -> None:
    """Abre o diretório em que o arquivo está (Windows/Linux/macOS)."""
    try:
        if platform.system() == "Windows":
            subprocess.run(["explorer", str(path)], check=False)
        elif platform.system() == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception:
        try:
            import webbrowser
            webbrowser.open(str(path))
        except Exception:
            pass


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(cfg: dict) -> None:
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def _parse_dnd_files(s: str) -> List[str]:
    """
    Recebe a string de dados do evento DND (muitas vezes algo como:
    "{C:\\path\\file1.pdf} {C:\\path\\file2.pdf}" ou "/home/user/file.pdf")
    e retorna lista de paths aceitáveis.
    """
    if not s:
        return []
    # procura por coisas entre chaves { ... }
    parts = re.findall(r'\{([^}]*)\}', s)
    if parts:
        return parts
    # senão divide por espaços (caminhos sem espaço também)
    return re.findall(r'[^ \t\n]+', s)


# Choose base class based on dnd availability
BaseTk = TkinterDnD.Tk if _DND_AVAILABLE else tk.Tk


class MergeApp(BaseTk):
    SORTS = {
        "Manual": None,
        "Nome (A → Z)": lambda p: p.name.lower(),
        "Nome (Z → A)": lambda p: p.name.lower(),
        "Data (antigo → novo)": lambda p: p.stat().st_mtime if p.exists() else -1,
        "Data (novo → antigo)": lambda p: p.stat().st_mtime if p.exists() else -1,
    }

    def __init__(self, initial: Iterable[str] = ()):
        super().__init__()
        self.title("Mesclar PDFs")
        self.geometry("760x480")
        self.minsize(520, 320)

        ico = resource_path("icone.ico")
        if ico.exists():
            try:
                self.iconbitmap(str(ico))
            except Exception:
                pass

        # Configurações persistentes
        self.config_data = load_config()
        # defaults
        self.config_data.setdefault("save_last_dir", True)
        self.config_data.setdefault("default_output_dir", str(Path.cwd()))
        self.config_data.setdefault("default_filename", "arquivo mesclado.pdf")
        self.config_data.setdefault("last_dir", str(Path.cwd()))

        self.files: List[Path] = resolve_pdfs(initial)
        self.sort_var = tk.StringVar(value="Manual")
        self.output_var = tk.StringVar()
        if self.files:
            self._set_default_output(Path(self.config_data.get("last_dir", self.config_data["default_output_dir"])))
        else:
            self._set_default_output(Path(self.config_data.get("default_output_dir", ".")))

        self._drag_index: int | None = None
        self._build_ui()
        self._refresh_listbox()

        # DND binding (se disponível)
        if _DND_AVAILABLE:
            try:
                # registrar drop tanto na listbox quanto na janela principal
                self.lb.drop_target_register(DND_FILES)
                self.lb.dnd_bind('<<Drop>>', self._on_drop)
                # também permitir drop na janela inteira
                self.drop_target_register(DND_FILES)
                self.dnd_bind('<<Drop>>', self._on_drop)
            except Exception:
                pass

    def _build_ui(self) -> None:
        frm = ttk.Frame(self, padding=8)
        frm.pack(fill="both", expand=True)

        top = ttk.Frame(frm)
        top.pack(fill="x", pady=(0, 6))
        ttk.Label(top, text="Arquivos (arrume a ordem):").pack(side="left")

        # gear button
        gear = ttk.Button(top, text="⚙", width=3, command=self.open_settings)
        gear.pack(side="left", padx=(6, 0))

        sort_frame = ttk.Frame(top)
        sort_frame.pack(side="right")
        ttk.Label(sort_frame, text="Ordenar por:").pack(side="left", padx=(0, 6))
        cb = ttk.Combobox(
            sort_frame, textvariable=self.sort_var, state="readonly",
            values=list(self.SORTS.keys()), width=36
        )
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", lambda e: self.apply_sort())

        box = ttk.Frame(frm)
        box.pack(fill="both", expand=True)

        self.lb = tk.Listbox(box, selectmode=tk.EXTENDED, activestyle="none", exportselection=False)
        self.lb.pack(side="left", fill="both", expand=True)
        scr = ttk.Scrollbar(box, orient="vertical", command=self.lb.yview)
        scr.pack(side="left", fill="y")
        self.lb.config(yscrollcommand=scr.set)

        #hint_frame = ttk.Frame(box)
        #hint_frame.pack(side="left", fill="y", padx=(6, 0))
        #ttk.Label(hint_frame, text="Dicas:\n- Duplo-clique: abrir pasta\n- Arraste arquivos do SO (se suportado)\n- Arraste dentro da lista para reordenar", justify="left").pack()

        # bindings drag single-item and double-click
        self.lb.bind("<Button-1>", self._on_btn1)
        self.lb.bind("<B1-Motion>", self._on_motion)
        self.lb.bind("<ButtonRelease-1>", self._on_release)
        self.lb.bind("<Double-Button-1>", lambda e: self.open_location())

        btns = ttk.Frame(box)
        btns.pack(side="left", fill="y", padx=(6, 0))
        btns_cfg = [
            ("Adicionar...", self.add_files),
            ("Remover", self.remove_selected),
            ("Subir", self.move_up),
            ("Descer", self.move_down),
            ("Limpar tudo", self.clear_all),
            ("Ordenar agora", self.apply_sort),
        ]
        for t, cmd in btns_cfg:
            ttk.Button(btns, text=t, command=cmd).pack(fill="x", pady=(0, 6))

        bottom = ttk.Frame(frm)
        bottom.pack(fill="x", pady=(8, 0))
        ttk.Label(bottom, text="Arquivo de saída:").pack(side="left")
        ttk.Entry(bottom, textvariable=self.output_var).pack(side="left", fill="x", expand=True, padx=(6, 6))
        ttk.Button(bottom, text="Procurar...", command=self.choose_output).pack(side="left")

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(8, 10), padx=8)
        ttk.Button(actions, text="Mesclar (Salvar)", command=self.merge_and_save).pack(side="right")
        ttk.Button(actions, text="Fechar", command=self.quit).pack(side="right", padx=(0, 6))

    def _set_default_output(self, folder: Path) -> None:
        name = self.config_data.get("default_filename", "arquivo mesclado.pdf")
        default_dir = folder if folder else Path(self.config_data.get("default_output_dir", "."))
        self.output_var.set(str(default_dir / name))

    def _refresh_listbox(self) -> None:
        self.lb.delete(0, tk.END)
        for p in self.files:
            self.lb.insert(tk.END, p.name)

    def add_files(self) -> None:
        initialdir = self.config_data.get("last_dir") if self.config_data.get("save_last_dir") else self.config_data.get("default_output_dir")
        chosen = filedialog.askopenfilenames(title="Adicionar PDFs", filetypes=[("PDF", "*.pdf")], initialdir=initialdir or None)
        new = resolve_pdfs(chosen)
        added = False
        for p in new:
            if p not in self.files:
                self.files.append(p)
                added = True
        if added:
            # salvar ultimo dir
            if chosen:
                try:
                    if self.config_data.get("save_last_dir") and chosen:
                        self.config_data["last_dir"] = str(Path(chosen[0]).parent)
                        save_config(self.config_data)
                except Exception:
                    pass
            if not self.output_var.get().strip():
                self._set_default_output(self.files[0].parent)
        self.apply_sort()
        self._refresh_listbox()

    def remove_selected(self) -> None:
        for i in reversed(self.lb.curselection()):
            del self.files[i]
        self._refresh_listbox()

    def move_up(self) -> None:
        sels = list(self.lb.curselection())
        if not sels:
            return
        for i in sels:
            if i > 0:
                self.files[i - 1], self.files[i] = self.files[i], self.files[i - 1]
        self._refresh_listbox()
        self._restore_selection([max(0, s - 1) for s in sels])

    def move_down(self) -> None:
        sels = list(self.lb.curselection())
        if not sels:
            return
        for i in reversed(sels):
            if i < len(self.files) - 1:
                self.files[i + 1], self.files[i] = self.files[i], self.files[i + 1]
        self._refresh_listbox()
        self._restore_selection([min(len(self.files) - 1, s + 1) for s in sels])

    def clear_all(self) -> None:
        if messagebox.askyesno("Confirmar", "Remover todos os arquivos?"):
            self.files.clear()
            self._refresh_listbox()

    def choose_output(self) -> None:
        initialdir = self.config_data.get("last_dir") if self.config_data.get("save_last_dir") else self.config_data.get("default_output_dir")
        out = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile=self.config_data.get("default_filename"), initialdir=initialdir or None)
        if out:
            self.output_var.set(out)
            # salvar ultimo dir se configurado
            try:
                if self.config_data.get("save_last_dir"):
                    self.config_data["last_dir"] = str(Path(out).parent)
                    save_config(self.config_data)
            except Exception:
                pass

    def open_location(self) -> None:
        sel = self.lb.curselection()
        if not sel:
            return
        p = self.files[sel[0]]
        if p.exists():
            open_folder(p.parent)

    def merge_and_save(self) -> None:
        if not self.files:
            messagebox.showwarning("Aviso", "Nenhum arquivo para mesclar.")
            return
        out = Path(self.output_var.get().strip() or (Path(self.config_data.get("last_dir", ".")) / self.config_data.get("default_filename", "arquivo mesclado.pdf")))
        try:
            writer = PdfWriter()
            for f in self.files:
                writer.append(str(f))
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open("wb") as fh:
                writer.write(fh)
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao mesclar:\n{exc}")
            return

        messagebox.showinfo("Concluído", f"PDF gerado:\n{out}")
        # salvar ultimo dir se configurado
        try:
            if self.config_data.get("save_last_dir"):
                self.config_data["last_dir"] = str(out.parent)
                save_config(self.config_data)
        except Exception:
            pass
        open_folder(out.parent)

    def apply_sort(self) -> None:
        key_name = self.sort_var.get()
        key = self.SORTS.get(key_name)
        if key is None:
            self._refresh_listbox()
            return
        reverse = "Z → A" in key_name or "novo" in key_name.lower()
        self.files.sort(key=key, reverse=reverse)
        self._refresh_listbox()

    # ---- drag handlers (single item reorder) ----
    def _on_btn1(self, event) -> None:
        idx = self.lb.nearest(event.y)
        if 0 <= idx < len(self.files):
            self._drag_index = idx
            self.lb.selection_clear(0, tk.END)
            self.lb.select_set(idx)
            # mudar cursor para indicar movimento
            try:
                self.lb.config(cursor="fleur")
            except Exception:
                pass

    def _on_motion(self, event) -> None:
        if self._drag_index is None:
            return
        to_idx = self.lb.nearest(event.y)
        fr = self._drag_index
        if to_idx != fr and 0 <= to_idx < len(self.files):
            item = self.files.pop(fr)
            self.files.insert(to_idx, item)
            self._drag_index = to_idx
            self._refresh_listbox()
            self.lb.selection_clear(0, tk.END)
            self.lb.select_set(to_idx)
            self.sort_var.set("Manual")
            try:
                self.lb.config(cursor="fleur")
            except Exception:
                pass

    def _on_release(self, event) -> None:
        # restaurar cursor e indice
        self._drag_index = None
        try:
            self.lb.config(cursor="")
        except Exception:
            pass

    def _restore_selection(self, indices: List[int]) -> None:
        self.lb.selection_clear(0, tk.END)
        for i in indices:
            if 0 <= i < len(self.files):
                self.lb.select_set(i)
        self.sort_var.set("Manual")

    # ---- DND drop handler (quando disponível) ----
    def _on_drop(self, event) -> None:
        # event.data contém os paths arrastados
        try:
            raw = getattr(event, "data", "")
            paths = _parse_dnd_files(raw)
            new = resolve_pdfs(paths)
            added = False
            for p in new:
                if p not in self.files:
                    self.files.append(p)
                    added = True
            if added:
                # atualizar last_dir se configurado
                try:
                    if paths and self.config_data.get("save_last_dir"):
                        self.config_data["last_dir"] = str(Path(paths[0]).parent)
                        save_config(self.config_data)
                except Exception:
                    pass
                if not self.output_var.get().strip() and self.files:
                    self._set_default_output(self.files[0].parent)
                self.apply_sort()
                self._refresh_listbox()
        except Exception:
            pass

    # ---- Settings UI ----
    def open_settings(self) -> None:
        win = tk.Toplevel(self)
        win.title("Configurações")
        win.transient(self)
        win.grab_set()
        win.geometry("520x180")
    
        def on_save():
            try:
                self.config_data["save_last_dir"] = bool(save_last_var.get())
                self.config_data["default_output_dir"] = default_dir_var.get().strip() or str(Path.cwd())
                self.config_data["default_filename"] = default_name_var.get().strip() or "arquivo mesclado.pdf"
                save_config(self.config_data)
                # atualizar saída atual se estiver vazia
                if not self.output_var.get().strip() and self.files:
                    self._set_default_output(Path(self.config_data.get("last_dir", self.config_data["default_output_dir"])))
                win.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar configurações:\n{e}")

        save_last_var = tk.IntVar(value=1 if self.config_data.get("save_last_dir") else 0)
        default_dir_var = tk.StringVar(value=self.config_data.get("default_output_dir", str(Path.cwd())))
        default_name_var = tk.StringVar(value=self.config_data.get("default_filename", "arquivo mesclado.pdf"))

        frm = ttk.Frame(win, padding=12)
        frm.pack(fill="both", expand=True)

        chk = ttk.Checkbutton(frm, text="Salvar último diretório usado", variable=save_last_var)
        chk.pack(anchor="w", pady=(0, 8))

        row = ttk.Frame(frm)
        row.pack(fill="x", pady=(0, 6))
        ttk.Label(row, text="Diretório padrão de saída:").pack(side="left")
        ttk.Entry(row, textvariable=default_dir_var).pack(side="left", fill="x", expand=True, padx=(6, 6))
        ttk.Button(row, text="Procurar", command=lambda: default_dir_var.set(filedialog.askdirectory(initialdir=default_dir_var.get() or None) or default_dir_var.get())).pack(side="left")

        row2 = ttk.Frame(frm)
        row2.pack(fill="x", pady=(0, 6))
        ttk.Label(row2, text="Nome padrão do arquivo:").pack(side="left")
        ttk.Entry(row2, textvariable=default_name_var).pack(side="left", fill="x", expand=True, padx=(6, 6))

        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=(8, 0))
        ttk.Button(btns, text="Salvar", command=on_save).pack(side="right", padx=(0, 6))
        ttk.Button(btns, text="Cancelar", command=win.destroy).pack(side="right")

        win.wait_window()

# --- main entrypoint ---
def main(argv: Iterable[str] = ()) -> None:
    init = resolve_pdfs(argv or sys.argv[1:])
    app = MergeApp(init)
    app.mainloop()


if __name__ == "__main__":
    main()
