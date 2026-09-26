import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ..utils import load_categories, save_categories
from .styles import HUD_BG, HUD_PANEL, HUD_CYAN, HUD_TEXT, HUD_MUTED, NO_SKIN

class CategoryEditor(ttk.Frame):
    def __init__(self, parent, app=None, **kwargs):
        self.app = app
        super().__init__(parent, **kwargs)
        self.categories = load_categories()
        self._create_widgets()
        self._populate_categories()

    def tr(self, key, *args):
        if self.app and hasattr(self.app, 'tr'):
            return self.app.tr(key, *args)
        # Fallback dictionary for standalone runs/tests
        defaults = {
            "cat_editor_categories": "KATEGORIE",
            "cat_editor_extensions": "ROZSZERZENIA",
            "cat_editor_save": "ZAPISZ ZMIANY",
            "cat_new_cat_title": "Nowa kategoria",
            "cat_new_cat_prompt": "Wprowadź nazwę kategorii (WIELKIE LITERY):",
            "cat_confirm_del_title": "Potwierdź usunięcie",
            "cat_confirm_del_msg": "Czy chcesz usunąć kategorię '{}' i wszystkie jej reguły?",
            "cat_warn_title": "Ostrzeżenie",
            "cat_warn_select": "Wybierz najpierw kategorię.",
            "cat_new_ext_title": "Nowe rozszerzenie",
            "cat_new_ext_prompt": "Wprowadź rozszerzenie (np. .txt):",
            "cat_save_success_title": "Sukces",
            "cat_save_success_msg": "Zapisano kategorie pomyślnie. Niektóre zmiany mogą wymagać ponownego uruchomienia.",
            "cat_save_error_title": "Błąd",
            "cat_save_error_msg": "Nie udało się zapisać kategorii."
        }
        val = defaults.get(key, key)
        if args:
            return val.format(*args)
        return val

    def update_language(self):
        self.cat_frame.config(text=self.tr("cat_editor_categories"))
        self.ext_frame.config(text=self.tr("cat_editor_extensions"))
        self.btn_save.config(text=self.tr("cat_editor_save"))

    def _create_widgets(self):
        # Two-column layout: Categories on the left, Extensions on the right
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # 1. Categories List
        self.cat_frame = ttk.Labelframe(self, text=self.tr("cat_editor_categories"), padding=10)
        self.cat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        if NO_SKIN:
            self.cat_list = tk.Listbox(self.cat_frame, font=("Segoe UI", 9))
        else:
            self.cat_list = tk.Listbox(self.cat_frame, bg=HUD_PANEL, fg=HUD_TEXT, 
                                      selectbackground=HUD_CYAN, selectforeground=HUD_BG,
                                      borderwidth=0, highlightthickness=0, font=("Segoe UI", 9))
        self.cat_list.pack(fill=tk.BOTH, expand=True)
        self.cat_list.bind("<<ListboxSelect>>", self._on_category_select)

        cat_btn_frame = ttk.Frame(self.cat_frame)
        cat_btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(cat_btn_frame, text="+", width=3, command=self._add_category).pack(side=tk.LEFT, padx=2)
        ttk.Button(cat_btn_frame, text="-", width=3, command=self._remove_category).pack(side=tk.LEFT, padx=2)

        # 2. Extensions List
        self.ext_frame = ttk.Labelframe(self, text=self.tr("cat_editor_extensions"), padding=10)
        self.ext_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        if NO_SKIN:
            self.ext_list = tk.Listbox(self.ext_frame, font=("Segoe UI", 9))
        else:
            self.ext_list = tk.Listbox(self.ext_frame, bg=HUD_PANEL, fg=HUD_TEXT,
                                      selectbackground=HUD_CYAN, selectforeground=HUD_BG,
                                      borderwidth=0, highlightthickness=0, font=("Segoe UI", 9))
        self.ext_list.pack(fill=tk.BOTH, expand=True)

        ext_btn_frame = ttk.Frame(self.ext_frame)
        ext_btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(ext_btn_frame, text="+", width=3, command=self._add_extension).pack(side=tk.LEFT, padx=2)
        ttk.Button(ext_btn_frame, text="-", width=3, command=self._remove_extension).pack(side=tk.LEFT, padx=2)

        # 3. Save Button
        self.btn_save = ttk.Button(self, text=self.tr("cat_editor_save"), command=self._save_changes)
        self.btn_save.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")

    def _populate_categories(self):
        self.cat_list.delete(0, tk.END)
        for cat in sorted(self.categories.keys()):
            self.cat_list.insert(tk.END, cat)

    def _on_category_select(self, event):
        selection = self.cat_list.curselection()
        if not selection:
            return
        
        cat_name = self.cat_list.get(selection[0])
        self.ext_list.delete(0, tk.END)
        for ext in sorted(self.categories[cat_name]):
            self.ext_list.insert(tk.END, ext)

    def _add_category(self):
        new_cat = simpledialog.askstring(self.tr("cat_new_cat_title"), self.tr("cat_new_cat_prompt"))
        if new_cat:
            new_cat = new_cat.upper().strip()
            if new_cat and new_cat not in self.categories:
                self.categories[new_cat] = []
                self._populate_categories()
                # Select the new category
                idx = sorted(self.categories.keys()).index(new_cat)
                self.cat_list.selection_clear(0, tk.END)
                self.cat_list.selection_set(idx)
                self._on_category_select(None)

    def _remove_category(self):
        selection = self.cat_list.curselection()
        if not selection:
            return
        
        cat_name = self.cat_list.get(selection[0])
        if messagebox.askyesno(self.tr("cat_confirm_del_title"), self.tr("cat_confirm_del_msg", cat_name)):
            del self.categories[cat_name]
            self._populate_categories()
            self.ext_list.delete(0, tk.END)

    def _add_extension(self):
        selection = self.cat_list.curselection()
        if not selection:
            messagebox.showwarning(self.tr("cat_warn_title"), self.tr("cat_warn_select"))
            return
        
        cat_name = self.cat_list.get(selection[0])
        new_ext = simpledialog.askstring(self.tr("cat_new_ext_title"), self.tr("cat_new_ext_prompt"))
        if new_ext:
            new_ext = new_ext.lower().strip()
            if not new_ext.startswith("."):
                new_ext = "." + new_ext
            
            if new_ext not in self.categories[cat_name]:
                self.categories[cat_name].append(new_ext)
                self._on_category_select(None)

    def _remove_extension(self):
        cat_selection = self.cat_list.curselection()
        ext_selection = self.ext_list.curselection()
        if not cat_selection or not ext_selection:
            return
        
        cat_name = self.cat_list.get(cat_selection[0])
        ext_name = self.ext_list.get(ext_selection[0])
        
        self.categories[cat_name].remove(ext_name)
        self._on_category_select(None)

    def _save_changes(self):
        if save_categories(self.categories):
            messagebox.showinfo(self.tr("cat_save_success_title"), self.tr("cat_save_success_msg"))
        else:
            messagebox.showerror(self.tr("cat_save_error_title"), self.tr("cat_save_error_msg"))
