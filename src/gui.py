import tkinter as tk
import os
import sys
import logging
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime, timedelta
import pystray
from PIL import Image, ImageDraw, ImageTk, ImageFilter, ImageFont
import platform
import ctypes
from .core import Cleaner, UndoManager
from .peek import PeekManager
from .ui.styles import HUD_BG, HUD_PANEL, HUD_CYAN, HUD_RED, HUD_TEXT, HUD_MUTED, HUD_BORDER, setup_hud_styles
from .ui.widgets import GlowButton, PieChart
from .ui.category_editor import CategoryEditor
from .icon_layout import save_icon_positions, restore_icon_positions, get_default_layout_path

def get_asset_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

LOCALIZATION = {
    "pl": {
        "status_active": "Status: Aktywny",
        "desktop": "Pulpit: ",
        "target": "Docelowy: ",
        "change": "Zmień",
        "ready": "Gotowy do działania",
        "scanning": "Status: Skanowanie...",
        "organized": "Pomyślnie uporządkowano {} elementów.",
        "organized_auto": "Automatyczne oczyszczenie: {} elementów.",
        "undo_history_empty": "Brak historii operacji do cofnięcia.",
        "undo_confirm_title": "Cofanie operacji",
        "undo_confirm_msg": "Czy na pewno chcesz cofnąć ostatnie oczyszczanie pulpitu?",
        "undo_restoring": "Przywracanie plików na pulpit...",
        "undo_error_title": "Błędy przywracania",
        "undo_success": "Cofnięto pomyślnie. Przywrócono {} elementów.",
        "btn_settings": "Ustawienia",
        "btn_preview": "Skanuj pulpit",
        "btn_clean": "Oczyszczaj",
        "btn_undo": "Cofnij",
        "items_to_organize": "Elementy do uporządkowania",
        "filter": "Filtr:",
        "settings_title": "Ustawienia programu",
        "tab_general": "OGÓLNE",
        "tab_categories": "KATEGORIE",
        "tab_exclusions": "WYKLUCZENIA",
        "frame_sys_exclusions": "Wykluczenia systemowe",
        "chk_exclude_lnk": "Wyklucz skróty (.lnk)",
        "chk_exclude_ico": "Wyklucz ikony (.ico)",
        "frame_auto": "Automatyzacja i foldery",
        "lbl_auto_freq": "Częstotliwość automatycznego porządkowania:",
        "chk_peek": "Włącz szybki podgląd folderu",
        "chk_dated": "Grupuj w folderach z datą (RRRR-MM-DD)",
        "chk_skip_folders": "Pomiń foldery (nie przenoś podkatalogów)",
        "frame_lang": "Język / Language",
        "lbl_select_lang": "Wybierz język / Select language:",
        "lbl_perm_ex": "Stałe wykluczenia (pliki i foldery):",
        "lbl_new_ex": "Nowe wykluczenie:",
        "btn_add": "Dodaj",
        "btn_remove_selected": "Usuń zaznaczone",
        "btn_close": "Zamknij",
        "status_updating_ex": "Zaktualizowano wykluczenia: {}",
        "status_peek_on": "Podgląd folderu włączony.",
        "status_peek_off": "Podgląd folderu wyłączony.",
        "status_dated": "Katalogi z datą: {}",
        "status_skip_folders": "Pomiń foldery: {}",
        "status_added_ex": "Dodano wykluczenie: {}",
        "status_removed_ex": "Usunięto z wykluczeń: {}",
        "status_interval": "Auto-porządkowanie ustawione na: {}",
        "categories": "Kategorie",
        "all": "Wszystkie",
        "none": "Żadne",
        "choose_target_folder": "Wybierz folder docelowy",
        "status_changed_target": "Zmieniono folder docelowy: {}",
        "status_clean": "Status: Pulpit jest czysty",
        "status_found": "Status: Znaleziono {} elementów do uporządkowania",
        "no_file_categories": "Brak kategorii plików",
        "alert_title": "Wykryto nadmiar plików!",
        "alert_text": "Liczba plików: {}/{} ({}%)",
        "alert_btn": "UPORZĄDKUJ PULPIT",
        "tray_open": "Otwórz program",
        "tray_clean": "Skanuj i Sprzątnij",
        "tray_exit": "Wyjdź",
        "info_title": "Informacja",
        "msg_no_items_selected": "Brak wybranych elementów do oczyszczenia.",
        "confirm_title": "Potwierdzenie",
        "msg_confirm_clean": "Zamierzasz przenieść {} elementów. Kontynuować?",
        "error": "BŁĄD",
        "status_errors": "Zakończono z błędami ({})",
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
        "cat_save_error_msg": "Nie udało się zapisać kategorii.",
        "folder": "Folder",
        "file": "Plik",
        "exclude_perm_menu": "Wyklucz '{}' na stałe",
        "status_excluded_perm": "Wykluczono na stałe: {}",
        "select_dest_folder": "Wybierz folder docelowy",
        "status_dest_changed": "Zmieniono folder docelowy: {}",
        "status_scanning": "Status: Skanowanie...",
        "status_desktop_clean": "Status: Pulpit jest czysty",
        "status_items_found": "Status: Znaleziono {} elementów do uporządkowania",
        "status_cleaning": "Oczyszczanie pulpitu...",
        "status_auto_cleaning": "Automatyczne oczyszczanie...",
        "error_prefix": "BŁĄD",
        "status_clean_errors": "Zakończono z błędami ({})",
        "status_clean_success": "Pomyślnie uporządkowano {} elementów.",
        "status_auto_clean_success": "Automatyczne oczyszczenie: {} elementów.",
        "status_no_undo_history": "Brak historii operacji do cofnięcia.",
        "undo_title": "Cofanie operacji",
        "msg_confirm_undo": "Czy na pewno chcesz cofnąć ostatnie oczyszczanie pulpitu?",
        "status_undoing": "Przywracanie plików na pulpit...",
        "undo_errors_title": "Błędy przywracania",
        "btn_save_layout": "Zapisz układ",
        "btn_restore_layout": "Przywróć układ",
        "status_layout_saved": "Zapisano pozycje {} ikon.",
        "status_layout_restored": "Przywrócono pozycje {} ikon.",
        "status_layout_error": "Błąd układu ikon: {}",
        "status_undo_success": "Cofnięto pomyślnie. Przywrócono {} elementów.",
        "save_layout_title": "Zapisz układ ikon jako",
        "restore_layout_title": "Przywróć układ ikon z pliku"
    },
    "en": {
        "status_active": "Status: Active",
        "desktop": "Desktop: ",
        "target": "Target: ",
        "change": "Change",
        "ready": "Ready to scan",
        "scanning": "Status: Scanning...",
        "organized": "Successfully organized {} elements.",
        "organized_auto": "Automatic cleanup: {} elements.",
        "undo_history_empty": "No operations in history to undo.",
        "undo_confirm_title": "Undo Operation",
        "undo_confirm_msg": "Are you sure you want to undo the last desktop cleanup?",
        "undo_restoring": "Restoring files to desktop...",
        "undo_error_title": "Restore Errors",
        "undo_success": "Undo successful. Restored {} elements.",
        "btn_settings": "Settings",
        "btn_preview": "Scan desktop",
        "btn_clean": "Clean",
        "btn_undo": "Undo",
        "items_to_organize": "Items to organize",
        "filter": "Filter:",
        "settings_title": "Program Settings",
        "tab_general": "GENERAL",
        "tab_categories": "CATEGORIES",
        "tab_exclusions": "EXCLUSIONS",
        "frame_sys_exclusions": "System Exclusions",
        "chk_exclude_lnk": "Exclude shortcuts (.lnk)",
        "chk_exclude_ico": "Exclude icons (.ico)",
        "frame_auto": "Automation & Folders",
        "lbl_auto_freq": "Automatic cleanup frequency:",
        "chk_peek": "Enable quick folder preview",
        "chk_dated": "Group in dated folders (YYYY-MM-DD)",
        "chk_skip_folders": "Skip folders (do not move subdirectories)",
        "frame_lang": "Language / Język",
        "lbl_select_lang": "Select language / Wybierz język:",
        "lbl_perm_ex": "Permanent exclusions (files and folders):",
        "lbl_new_ex": "New exclusion:",
        "btn_add": "Add",
        "btn_remove_selected": "Remove Selected",
        "btn_close": "Close",
        "status_updating_ex": "Updated exclusions: {}",
        "status_peek_on": "Folder preview enabled.",
        "status_peek_off": "Folder preview disabled.",
        "status_dated": "Dated folders: {}",
        "status_skip_folders": "Skip folders: {}",
        "status_added_ex": "Added exclusion: {}",
        "status_removed_ex": "Removed from exclusions: {}",
        "status_interval": "Auto-clean set to: {}",
        "categories": "Categories",
        "all": "All",
        "none": "None",
        "choose_target_folder": "Choose target folder",
        "status_changed_target": "Changed target folder: {}",
        "status_clean": "Status: Desktop is clean",
        "status_found": "Status: Found {} items to organize",
        "no_file_categories": "No file categories",
        "alert_title": "Excessive files detected!",
        "alert_text": "File count: {}/{} ({}%)",
        "alert_btn": "CLEAN DESKTOP",
        "tray_open": "Open application",
        "tray_clean": "Scan & Clean",
        "tray_exit": "Exit",
        "info_title": "Information",
        "msg_no_items_selected": "No items selected to clean.",
        "confirm_title": "Confirmation",
        "msg_confirm_clean": "You are about to move {} items. Continue?",
        "error": "ERROR",
        "status_errors": "Completed with errors ({})",
        "cat_editor_categories": "CATEGORIES",
        "cat_editor_extensions": "EXTENSIONS",
        "cat_editor_save": "SAVE CHANGES",
        "cat_new_cat_title": "New Category",
        "cat_new_cat_prompt": "Enter category name (UPPERCASE):",
        "cat_confirm_del_title": "Confirm Deletion",
        "cat_confirm_del_msg": "Do you want to delete category '{}' and all its rules?",
        "cat_warn_title": "Warning",
        "cat_warn_select": "Please select a category first.",
        "cat_new_ext_title": "New Extension",
        "cat_new_ext_prompt": "Enter extension (e.g. .txt):",
        "cat_save_success_title": "Success",
        "cat_save_success_msg": "Categories saved successfully. Some changes may require restarting.",
        "cat_save_error_title": "Error",
        "cat_save_error_msg": "Failed to save categories.",
        "folder": "Folder",
        "file": "File",
        "exclude_perm_menu": "Exclude '{}' permanently",
        "status_excluded_perm": "Permanently excluded: {}",
        "select_dest_folder": "Select destination folder",
        "status_dest_changed": "Changed target folder: {}",
        "status_scanning": "Status: Scanning...",
        "status_desktop_clean": "Status: Desktop is clean",
        "status_items_found": "Status: Found {} items to organize",
        "status_cleaning": "Cleaning desktop...",
        "status_auto_cleaning": "Automatic cleanup...",
        "error_prefix": "ERROR",
        "status_clean_errors": "Completed with errors ({})",
        "status_clean_success": "Successfully organized {} elements.",
        "status_auto_clean_success": "Automatic cleanup: {} elements.",
        "status_no_undo_history": "No operations in history to undo.",
        "undo_title": "Undo Operation",
        "msg_confirm_undo": "Are you sure you want to undo the last desktop cleanup?",
        "status_undoing": "Restoring files to desktop...",
        "undo_errors_title": "Restore Errors",
        "btn_save_layout": "Save Layout",
        "btn_restore_layout": "Restore Layout",
        "status_layout_saved": "Saved positions of {} icons.",
        "status_layout_restored": "Restored positions of {} icons.",
        "status_layout_error": "Icon layout error: {}",
        "status_undo_success": "Undo successful. Restored {} elements.",
        "save_layout_title": "Save icon layout as",
        "restore_layout_title": "Restore icon layout from file"
    }
}

class DesktopCleanerApp(tk.Tk):
    def __init__(self, no_skin=False):
        super().__init__()
        self.no_skin = no_skin
        if "pytest" not in sys.modules:
            import tracemalloc
            if not tracemalloc.is_tracing():
                tracemalloc.start()
            
        logging.info("Initializing Sweeply HUD...")
        self.title("Sweeply" if no_skin else "Sweeply | VirtuArch")
        self.geometry("860x650")
        self.configure(bg=HUD_BG)
        
        # Set taskbar and window icon
        if platform.system() == 'Windows':
            try:
                myappid = 'sweeply.desktopcleaner.hud.1.0b'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception as e:
                logging.error(f"Error setting AppUserModelID: {e}")
        try:
            icon_path = get_asset_path(os.path.join("images", "sweply_circle.webp"))
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                # Crop to bounding box to remove empty padding and enlarge icon appearance
                bbox = icon_img.getbbox()
                if bbox:
                    icon_img = icon_img.crop(bbox)
                # Create standard sizes
                sizes = [16, 32, 48, 256]
                self.app_icons = []
                for size in sizes:
                    resized = icon_img.resize((size, size), Image.Resampling.LANCZOS)
                    self.app_icons.append(ImageTk.PhotoImage(resized))
                self.iconphoto(True, *self.app_icons)
        except Exception as e:
            logging.error(f"Error setting app icon: {e}")
        
        # Logic
        self.cleaner = Cleaner()
        self.undo_manager = UndoManager()
        self.btn_imgs = {}

        # Styles
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self._setup_hud_styles()
        
        # Settings State
        self.var_exclude_lnk = tk.BooleanVar(value=True)
        self.var_exclude_ico = tk.BooleanVar(value=True)
        self.var_auto_interval = tk.StringVar(value=self.cleaner.config.get("auto_interval", "Off"))
        self.var_enable_peek = tk.BooleanVar(value=False)
        self.var_dated_folders = tk.BooleanVar(value=self.cleaner.config.get("dated_folders", False))
        self.var_skip_folders = tk.BooleanVar(value=self.cleaner.config.get("skip_folders", False))
        self.category_vars = {}
        self.peek_manager = PeekManager(self)
        self.logo_img = None
        self.tray_icon = None
        
        self.last_auto_clean = datetime.now()
        last_clean_str = self.cleaner.config.get("last_auto_clean")
        if last_clean_str:
            try:
                self.last_auto_clean = datetime.fromisoformat(last_clean_str)
            except:
                pass
        self.scan_results = [] # Stores (name, size, type, category)
        self.item_selection_vars = {} # Maps item name -> tk.BooleanVar

        # Widget Attributes (Declared here for linter safety)
        self.main_container = tk.Frame(self) # Temporary or just declare
        self.lbl_path = tk.Label(self)
        self.lbl_dest = tk.Label(self)
        self.notebook = ttk.Notebook(self)
        self.frame_files = ttk.Frame(self)
        self.tree_files = ttk.Treeview(self)
        self.frame_folders = ttk.Frame(self)
        self.tree_folders = ttk.Treeview(self)
        self.btn_preview = GlowButton(self, "")
        self.btn_clean = GlowButton(self, "")
        self.btn_undo = GlowButton(self, "")
        self.btn_settings = GlowButton(self, "")
        self.progress = ttk.Progressbar(self)
        self.lbl_status = tk.Label(self)
        self.header_layer = tk.Frame(self)
        self.console = tk.Text(self)
        self.logo_label = tk.Label(self)

        self.geometry("0x0+10000+10000")
        self.show_splash_screen()

    def tr(self, key, *args):
        lang = self.cleaner.config.get("lang", "pl")
        txt = LOCALIZATION.get(lang, LOCALIZATION["pl"]).get(key, key)
        if args:
            return txt.format(*args)
        return txt

    def load_button_images(self):
        self.btn_imgs.clear()
        lang = self.cleaner.config.get("lang", "pl")
        if lang == "en":
            scan_file = "scan.webp"
            clean_file = "clean.webp"
            undo_file = "cancel.webp"
            settings_file = "settings.webp"
            save_file = "save.webp"
            restore_file = "restore_layout.webp"
        else:
            scan_file = "skanuj.webp"
            clean_file = "oczyszczaj.webp"
            undo_file = "cofnij.webp"
            settings_file = "ustawienia.webp"
            save_file = "zapisz_układ_ikon.webp"
            restore_file = "przywróc_układ_ikon.webp"

        buttons_config = {
            "preview": (scan_file, 46),
            "clean": (clean_file, 46),
            "undo": (undo_file, 46),
            "settings": (settings_file, 46),
            "save_layout": (save_file, 46),
            "restore_layout": (restore_file, 46),
        }
        
        for key, (filename, tgt_h) in buttons_config.items():
            p = get_asset_path(os.path.join("images", filename))
            if not os.path.exists(p):
                p = get_asset_path(filename)
            if os.path.exists(p):
                try:
                    img = Image.open(p)
                    w, h = img.size
                    tgt_w = int(w * (tgt_h / h))
                    img_scaled = img.resize((tgt_w, tgt_h), Image.Resampling.LANCZOS)
                    self.btn_imgs[key] = ImageTk.PhotoImage(img_scaled)
                except Exception as e:
                    logging.error(f"Error loading button image {filename}: {e}")
        
    def _setup_hud_styles(self):
        setup_hud_styles(self.style)
        
        # Progressbar
        self.style.configure("TProgressbar", thickness=15, troughcolor=HUD_PANEL, background=HUD_CYAN)
        self.style.configure("Status.TLabel", font=("Segoe UI", 10), foreground=HUD_MUTED)

    def _create_widgets(self):
        self.minsize(700, 600)

        # ── Main container ───────────────
        self.main_container = tk.Frame(self, bg=HUD_BG)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # ── 1. Header ─────────────────────────────────────────────────────
        banner_path = get_asset_path(os.path.join("images", "TopBaner.webp"))
        
        # Load logo for taskbar icon regardless of banner
        self.logo_img = None
        for candidate in [
            get_asset_path(os.path.join("images", "sweply_circle.webp")),
            get_asset_path(os.path.join("images", "sweepy_ligh400x400.webp")),
            get_asset_path(os.path.join("images", "sweepy_ligh.webp")),
            get_asset_path("logo_transparent.webp"),
        ]:
            if os.path.exists(candidate):
                try:
                    img = Image.open(candidate).convert("RGBA")
                    if not candidate.lower().endswith(".webp"):
                        orig_w, orig_h = img.size
                        side = min(orig_w, orig_h)
                        img = img.crop(((orig_w - side) // 2, (orig_h - side) // 2,
                                        (orig_w + side) // 2, (orig_h + side) // 2))
                        mask = Image.new("L", (side, side), 0)
                        ImageDraw.Draw(mask).ellipse([0, 0, side - 1, side - 1], fill=255)
                        img.putalpha(mask)
                    img = img.resize((160, 160), Image.Resampling.LANCZOS)
                    self.logo_img = ImageTk.PhotoImage(img)
                    self.iconphoto(True, self.logo_img)
                except Exception as e:
                    logging.error(f"Error loading taskbar logo: {e}")
                break

        if not self.no_skin and os.path.exists(banner_path):
            # Premium Banner Header Flow
            header_frame = tk.Frame(self.main_container, bg=HUD_BG)
            header_frame.pack(fill=tk.X, side=tk.TOP)
            self.header_layer = header_frame

            # Generate the high-fidelity cyberpunk switch images programmatically
            self.switch_pl_img = self._draw_cyber_switch("pl")
            self.switch_eng_img = self._draw_cyber_switch("en")

            # Fixed header height of 220px matches modern wide banners perfectly
            self.header_canvas = tk.Canvas(header_frame, bg=HUD_BG, bd=0, highlightthickness=0, height=220)
            self.header_canvas.pack(fill=tk.X, expand=True)

            # Background image placeholder on canvas
            self.canvas_bg_image = self.header_canvas.create_image(0, 0, anchor=tk.NW)

            # Create a single canvas image element for the switch
            curr_lang = self.cleaner.config.get("lang", "pl")
            initial_img = self.switch_eng_img if curr_lang == "en" else self.switch_pl_img
            self.canvas_switch_image = self.header_canvas.create_image(0, 0, image=initial_img, anchor=tk.CENTER)

            # Generate the Buy Me a Coffee button images
            self.bmc_normal_img = self._draw_bmc_button(hover=False)
            self.bmc_hover_img = self._draw_bmc_button(hover=True)
            self.canvas_bmc_button = self.header_canvas.create_image(0, 0, image=self.bmc_normal_img, anchor=tk.CENTER)

            # Click and hover bindings for Buy Me a Coffee
            def on_bmc_click(event):
                import webbrowser
                try:
                    webbrowser.open("https://www.buymeacoffee.com/morbidnoizl")
                except Exception as e:
                    logging.error(f"Error opening Buy Me a Coffee link: {e}")
                    
            def on_bmc_enter(event):
                self.header_canvas.itemconfig(self.canvas_bmc_button, image=self.bmc_hover_img)
                self.header_canvas.config(cursor="hand2")
                
            def on_bmc_leave(event):
                self.header_canvas.itemconfig(self.canvas_bmc_button, image=self.bmc_normal_img)
                self.header_canvas.config(cursor="")
                
            self.header_canvas.tag_bind(self.canvas_bmc_button, "<Button-1>", on_bmc_click)
            self.header_canvas.tag_bind(self.canvas_bmc_button, "<Enter>", on_bmc_enter)
            self.header_canvas.tag_bind(self.canvas_bmc_button, "<Leave>", on_bmc_leave)

            # Bind click and hover actions to the switch
            def on_switch_click(event):
                w = self.header_canvas.winfo_width()
                cx = w * 0.5
                click_x = event.x
                
                # Check coordinates (switch image is 200px wide, center at cx)
                if click_x < cx - 30:
                    # Clicked PL flag or label (left side)
                    new_lang = "pl"
                elif click_x > cx + 30:
                    # Clicked UK flag or label (right side)
                    new_lang = "en"
                else:
                    # Clicked switch in the middle (toggles current language)
                    curr = self.cleaner.config.get("lang", "pl")
                    new_lang = "en" if curr == "pl" else "pl"
                
                if self.cleaner.config.get("lang", "pl") != new_lang:
                    self.cleaner.config["lang"] = new_lang
                    self.cleaner._save_config()
                    self.update_language()

            self.header_canvas.tag_bind(self.canvas_switch_image, "<Button-1>", on_switch_click)
            self.header_canvas.tag_bind(self.canvas_switch_image, "<Enter>", lambda e: self.header_canvas.config(cursor="hand2"))
            self.header_canvas.tag_bind(self.canvas_switch_image, "<Leave>", lambda e: self.header_canvas.config(cursor=""))

            # Container frame for text overlay - styled to blend with banner center panel
            self.info_frame = tk.Frame(self.header_canvas, bg="#111a21")
            
            # Position variables matching the center frame coordinates on the canvas
            self.canvas_info_window = self.header_canvas.create_window(0, 0, anchor=tk.W, window=self.info_frame)

            self.lbl_version = tk.Label(self.info_frame, text="Version 1.0b", 
                                        font=("Segoe UI Semibold", 8), fg=HUD_CYAN, bg="#111a21")
            self.lbl_version.pack(anchor=tk.W)

            self.lbl_active_status = tk.Label(self.info_frame, text=self.tr("status_active"), 
                                              font=("Segoe UI Semibold", 11), fg=HUD_TEXT, bg="#111a21")
            self.lbl_active_status.pack(anchor=tk.W, pady=(1, 0))

            self.lbl_path = tk.Label(self.info_frame, text=f"{self.tr('desktop')}{self.cleaner.desktop_path}",
                                     font=("Segoe UI", 9), fg=HUD_MUTED, bg="#111a21")
            self.lbl_path.pack(anchor=tk.W, pady=(1, 0))

            dest_row = tk.Frame(self.info_frame, bg="#111a21")
            dest_row.pack(anchor=tk.W)

            self.lbl_dest = tk.Label(dest_row, text=f"{self.tr('target')}{self.cleaner.clean_folder_path}",
                                     font=("Segoe UI", 9), fg=HUD_MUTED, bg="#111a21")
            self.lbl_dest.pack(side=tk.LEFT)

            self.btn_change_dest = tk.Button(dest_row, text=self.tr("change"), font=("Segoe UI Semibold", 8), fg=HUD_CYAN,
                                             bg="#111a21", borderwidth=0, activebackground="#111a21",
                                             activeforeground=HUD_CYAN, cursor="hand2",
                                             command=self.on_change_destination)
            self.btn_change_dest.pack(side=tk.LEFT, padx=4)

            # Bind resize event to dynamically scale top banner
            self.header_canvas.bind("<Configure>", self.on_header_resize)
        else:
            # Classic Fallback Header Flow
            header_frame = tk.Frame(self.main_container, bg=HUD_BG, pady=14, padx=20)
            header_frame.pack(fill=tk.X, side=tk.TOP)
            self.header_layer = header_frame

            if self.logo_img:
                tk.Label(header_frame, image=self.logo_img, bg=HUD_BG).pack(side=tk.LEFT, padx=(0, 16))
            else:
                tk.Label(header_frame, text="Sweeply", font=("Segoe UI Semibold", 16) if not self.no_skin else ("Segoe UI", 16, "bold"),
                         fg=HUD_CYAN if not self.no_skin else "SystemWindowText", bg=HUD_BG).pack(side=tk.LEFT)

            robot_icon_path = get_asset_path(os.path.join("images", "robbo1.webp"))
            if os.path.exists(robot_icon_path):
                try:
                    _ri = Image.open(robot_icon_path).convert("RGBA")
                    _ri = _ri.resize((200, 200), Image.Resampling.LANCZOS)
                    self.robot_icon_img = ImageTk.PhotoImage(_ri)
                    tk.Label(header_frame, image=self.robot_icon_img, bg=HUD_BG).pack(side=tk.RIGHT, padx=(0, 16))
                except Exception as e:
                    logging.error(f"Error loading robot icon: {e}")

            self.info_frame = tk.Frame(header_frame, bg=HUD_BG)
            self.info_frame.pack(side=tk.LEFT, padx=28)

            self.lbl_active_status = tk.Label(self.info_frame, text=self.tr("status_active"), 
                                              font=("Segoe UI Semibold", 10) if not self.no_skin else ("Segoe UI", 10),
                                              fg=HUD_TEXT, bg=HUD_BG)
            self.lbl_active_status.pack(anchor=tk.W)

            self.lbl_path = tk.Label(self.info_frame, text=f"{self.tr('desktop')}{self.cleaner.desktop_path}",
                                     font=("Segoe UI", 9), fg=HUD_MUTED, bg=HUD_BG)
            self.lbl_path.pack(anchor=tk.W, pady=(2, 0))

            dest_row = tk.Frame(self.info_frame, bg=HUD_BG)
            dest_row.pack(anchor=tk.W)

            self.lbl_dest = tk.Label(dest_row, text=f"{self.tr('target')}{self.cleaner.clean_folder_path}",
                                     font=("Segoe UI", 9), fg=HUD_MUTED, bg=HUD_BG)
            self.lbl_dest.pack(side=tk.LEFT)

            self.btn_change_dest = tk.Button(dest_row, text=self.tr("change"), font=("Segoe UI Semibold", 8) if not self.no_skin else ("Segoe UI", 8),
                                             fg=HUD_CYAN if not self.no_skin else "SystemWindowText",
                                             bg=HUD_BG, borderwidth=0, activebackground=HUD_BG,
                                             activeforeground=HUD_CYAN, cursor="hand2",
                                             command=self.on_change_destination)
            self.btn_change_dest.pack(side=tk.LEFT, padx=4)

        # ── Thin separator line ───────────────────────────────────────────
        if not self.no_skin:
            tk.Frame(self.main_container, bg=HUD_BORDER, height=1).pack(fill=tk.X)

        # ── 2. Bottom bar (packed BEFORE content so expand doesn't eat it) ──
        self.lbl_status = tk.Label(self.main_container, text=self.tr("ready"),
                                   font=("Segoe UI", 9), fg=HUD_MUTED, bg=HUD_BG,
                                   anchor=tk.W, padx=20, pady=5)
        self.lbl_status.pack(fill=tk.X, side=tk.BOTTOM)

        if not self.no_skin:
            tk.Frame(self.main_container, bg=HUD_BORDER, height=1).pack(fill=tk.X, side=tk.BOTTOM)

        self.progress = ttk.Progressbar(self.main_container, orient=tk.HORIZONTAL,
                                        length=100, mode="determinate")
        self.progress.pack(fill=tk.X, padx=20, pady=(0, 2), side=tk.BOTTOM)

        # ── Control buttons bar ───────────────────────────────────────────
        ctrl = tk.Frame(self.main_container, bg=HUD_BG, pady=10, padx=20)
        ctrl.pack(fill=tk.X, side=tk.BOTTOM)

        if self.no_skin:
            btn_style_classic = dict(font=("Segoe UI", 9))
            self.btn_preview = tk.Button(ctrl, text=self.tr("btn_preview"),
                                         command=self.on_preview, **btn_style_classic)
            self.btn_preview.pack(side=tk.LEFT, padx=(0, 6))

            self.btn_clean = tk.Button(ctrl, text=self.tr("btn_clean"),
                                       command=self.on_clean, **btn_style_classic)
            self.btn_clean.pack(side=tk.LEFT, padx=(0, 6))

            self.btn_undo = tk.Button(ctrl, text=self.tr("btn_undo"),
                                      state=tk.DISABLED,
                                      command=self.on_undo, **btn_style_classic)
            self.btn_undo.pack(side=tk.LEFT)

            self.btn_settings = tk.Button(ctrl, text=self.tr("btn_settings"),
                                          command=self.on_settings, **btn_style_classic)
            self.btn_settings.pack(side=tk.RIGHT)
        else:
            btn_style = dict(font=("Segoe UI Semibold", 9), relief="flat", cursor="hand2",
                             bd=0, padx=16, pady=8, activeforeground="#FFFFFF")

            # Preview Button
            if "preview" in self.btn_imgs:
                self.btn_preview = tk.Button(ctrl, image=self.btn_imgs["preview"], bg=HUD_BG, bd=0, 
                                             activebackground=HUD_BG, highlightthickness=0, cursor="hand2",
                                             command=self.on_preview)
            else:
                self.btn_preview = tk.Button(ctrl, text=self.tr("btn_preview"), bg=HUD_PANEL, fg=HUD_TEXT,
                                             activebackground=HUD_CYAN, command=self.on_preview, **btn_style)
            self.btn_preview.pack(side=tk.LEFT, padx=(0, 6))

            # Clean Button
            if "clean" in self.btn_imgs:
                self.btn_clean = tk.Button(ctrl, image=self.btn_imgs["clean"], bg=HUD_BG, bd=0, 
                                           activebackground=HUD_BG, highlightthickness=0, cursor="hand2",
                                           command=self.on_clean)
            else:
                self.btn_clean = tk.Button(ctrl, text=self.tr("btn_clean"), bg=HUD_CYAN, fg="#FFFFFF",
                                           activebackground=HUD_CYAN, command=self.on_clean, **btn_style)
            self.btn_clean.pack(side=tk.LEFT, padx=(0, 6))

            # Undo Button
            if "undo" in self.btn_imgs:
                self.btn_undo = tk.Button(ctrl, image=self.btn_imgs["undo"], bg=HUD_BG, bd=0, 
                                          activebackground=HUD_BG, highlightthickness=0, cursor="hand2",
                                          state=tk.DISABLED, command=self.on_undo)
            else:
                self.btn_undo = tk.Button(ctrl, text=self.tr("btn_undo"), bg=HUD_PANEL, fg=HUD_MUTED,
                                          activebackground=HUD_PANEL, state=tk.DISABLED, command=self.on_undo, **btn_style)
            self.btn_undo.pack(side=tk.LEFT)

            # Settings Button
            if "settings" in self.btn_imgs:
                self.btn_settings = tk.Button(ctrl, image=self.btn_imgs["settings"], bg=HUD_BG, bd=0,
                                              activebackground=HUD_BG, highlightthickness=0, cursor="hand2",
                                              command=self.on_settings)
            else:
                self.btn_settings = tk.Button(ctrl, text=self.tr("btn_settings"), bg=HUD_PANEL, fg=HUD_TEXT,
                                              activebackground=HUD_PANEL, command=self.on_settings, **btn_style)
            self.btn_settings.pack(side=tk.RIGHT, padx=(6, 0))

            # Save / Restore Layout Buttons (right side, before settings)
            if "restore_layout" in self.btn_imgs:
                self.btn_restore_layout = tk.Button(ctrl, image=self.btn_imgs["restore_layout"], bg=HUD_BG, bd=0, 
                                                    activebackground=HUD_BG, highlightthickness=0, cursor="hand2",
                                                    command=self.on_restore_layout)
            else:
                self.btn_restore_layout = tk.Button(ctrl, text=self.tr("btn_restore_layout"), bg=HUD_PANEL, fg=HUD_TEXT,
                                                    activebackground=HUD_PANEL, command=self.on_restore_layout, **btn_style)
            self.btn_restore_layout.pack(side=tk.RIGHT, padx=(6, 0))

            if "save_layout" in self.btn_imgs:
                self.btn_save_layout = tk.Button(ctrl, image=self.btn_imgs["save_layout"], bg=HUD_BG, bd=0, 
                                                 activebackground=HUD_BG, highlightthickness=0, cursor="hand2",
                                                 command=self.on_save_layout)
            else:
                self.btn_save_layout = tk.Button(ctrl, text=self.tr("btn_save_layout"), bg=HUD_PANEL, fg=HUD_TEXT,
                                                 activebackground=HUD_PANEL, command=self.on_save_layout, **btn_style)
            self.btn_save_layout.pack(side=tk.RIGHT, padx=(6, 0))

        # No separator above the button bar — blends flush with window background

        # ── 3. Content area (packed LAST — takes all remaining space) ─────
        pcb_path = os.path.join("images", "pcb2.webp")
        pcb_exists = os.path.exists(pcb_path)

        if not self.no_skin and pcb_exists:
            self.content_canvas = tk.Canvas(self.main_container, bg=HUD_BG, bd=0, highlightthickness=0)
            self.content_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
            self.content_bg_image = self.content_canvas.create_image(0, 0, anchor=tk.NW)
            content_parent = self.content_canvas
            # Bind resize event to dynamically scale PCB background
            self.content_canvas.bind("<Configure>", self.on_content_resize)
        else:
            content_layout = tk.Frame(self.main_container, bg=HUD_BG)
            content_layout.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
            content_parent = content_layout

        # Left card — file list
        if self.no_skin:
            left_card = tk.Frame(content_parent)
        else:
            left_card = tk.Frame(content_parent, bg=HUD_PANEL,
                                 highlightthickness=1, highlightbackground=HUD_BORDER)
        
        if not self.no_skin and pcb_exists:
            left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 6), pady=10)
        else:
            left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        if self.no_skin:
            ch = tk.Frame(left_card, pady=8)
        else:
            ch = tk.Frame(left_card, bg=HUD_PANEL, pady=8)
        ch.pack(fill=tk.X, padx=12)
        
        self.lbl_items_header = tk.Label(ch, text=self.tr("items_to_organize"), font=("Segoe UI Semibold", 9) if not self.no_skin else ("Segoe UI", 9),
                 fg=HUD_MUTED, bg=HUD_PANEL)
        self.lbl_items_header.pack(side=tk.LEFT)

        # Search
        if self.no_skin:
            sf = tk.Frame(ch)
        else:
            sf = tk.Frame(ch, bg=HUD_PANEL)
        sf.pack(side=tk.RIGHT)
        
        self.lbl_filter = tk.Label(sf, text=self.tr("filter"), font=("Segoe UI", 9), fg=HUD_MUTED, bg=HUD_PANEL)
        self.lbl_filter.pack(side=tk.LEFT, padx=(0, 4))
        
        self.var_search = tk.StringVar()
        self.var_search.trace_add("write", self.on_search_changed)
        if self.no_skin:
            self.ent_search = tk.Entry(sf, textvariable=self.var_search, font=("Segoe UI", 9), width=18)
        else:
            self.ent_search = tk.Entry(sf, textvariable=self.var_search,
                                       bg=HUD_PANEL, fg=HUD_TEXT,
                                       insertbackground=HUD_CYAN, font=("Segoe UI", 9),
                                       borderwidth=0, highlightthickness=1,
                                       highlightbackground=HUD_BORDER, highlightcolor=HUD_CYAN, width=18)
        self.ent_search.pack(side=tk.LEFT)

        if not self.no_skin:
            tk.Frame(left_card, bg=HUD_BORDER, height=1).pack(fill=tk.X)

        console_scroll = ttk.Scrollbar(left_card, orient=tk.VERTICAL)
        console_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        if self.no_skin:
            self.console = tk.Text(left_card, wrap=tk.WORD,
                                   font=("Segoe UI", 10),
                                   padx=14, pady=10, state=tk.DISABLED, spacing1=3, spacing3=3,
                                   yscrollcommand=console_scroll.set)
        else:
            self.console = tk.Text(left_card, wrap=tk.WORD, bg=HUD_PANEL, fg=HUD_TEXT,
                                   font=("Segoe UI", 10), borderwidth=0, highlightthickness=0,
                                   padx=14, pady=10, state=tk.DISABLED, spacing1=3, spacing3=3,
                                   yscrollcommand=console_scroll.set)
        self.console.pack(fill=tk.BOTH, expand=True)
        console_scroll.config(command=self.console.yview)

        # Right card — pie chart + categories
        if self.no_skin:
            right_card = tk.Frame(content_parent, width=250)
        else:
            right_card = tk.Frame(content_parent, bg=HUD_PANEL, width=250,
                                  highlightthickness=1, highlightbackground=HUD_BORDER)
        
        if not self.no_skin and pcb_exists:
            right_card.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 10), pady=10)
        else:
            right_card.pack(side=tk.RIGHT, fill=tk.Y)
        right_card.pack_propagate(False)

        self.pie_chart = PieChart(right_card, width=220, height=220, bg=HUD_PANEL)
        self.pie_chart.pack(pady=(14, 8), padx=14)

        if not self.no_skin:
            tk.Frame(right_card, bg=HUD_BORDER, height=1).pack(fill=tk.X, padx=10)

        self.cat_filter_frame = tk.Frame(right_card, bg=HUD_PANEL)
        self.cat_filter_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        self.lbl_categories_title = tk.Label(self.cat_filter_frame, text=self.tr("categories"), font=("Segoe UI Semibold", 8) if not self.no_skin else ("Segoe UI", 8),
                 fg=HUD_MUTED, bg=HUD_PANEL)
        self.lbl_categories_title.pack(anchor=tk.W, pady=(2, 4))

        toggles = tk.Frame(self.cat_filter_frame, bg=HUD_PANEL)
        toggles.pack(fill=tk.X)
        if self.no_skin:
            self.btn_select_all = tk.Button(toggles, text=self.tr("all"), font=("Segoe UI", 8),
                       command=self.select_all_categories)
            self.btn_select_all.pack(side=tk.LEFT, padx=(0, 8))
            self.btn_select_none = tk.Button(toggles, text=self.tr("none"), font=("Segoe UI", 8),
                       command=self.select_none_categories)
            self.btn_select_none.pack(side=tk.LEFT)
        else:
            self.btn_select_all = tk.Button(toggles, text=self.tr("all"), font=("Segoe UI", 8), fg=HUD_CYAN, bg=HUD_PANEL,
                       borderwidth=0, activebackground=HUD_PANEL, activeforeground=HUD_CYAN,
                       cursor="hand2", command=self.select_all_categories)
            self.btn_select_all.pack(side=tk.LEFT, padx=(0, 8))
            self.btn_select_none = tk.Button(toggles, text=self.tr("none"), font=("Segoe UI", 8), fg=HUD_MUTED, bg=HUD_PANEL,
                       borderwidth=0, activebackground=HUD_PANEL, activeforeground=HUD_CYAN,
                       cursor="hand2", command=self.select_none_categories)
            self.btn_select_none.pack(side=tk.LEFT)

        self.checkbox_container = tk.Frame(self.cat_filter_frame, bg=HUD_PANEL)
        self.checkbox_container.pack(fill=tk.BOTH, expand=True, pady=4)



    def log_console(self, message, is_error=False):
        """Clean diagnostic logging to file list console."""
        now = datetime.now()
        timestamp = f"[{now.hour:02d}:{now.minute:02d}:{now.second:02d}] "
        color = HUD_RED if is_error else HUD_TEXT
        
        self.console.config(state=tk.NORMAL)
        
        # Insert timestamp in muted color
        t_start = self.console.index(tk.INSERT)
        self.console.insert(tk.END, timestamp)
        t_end = self.console.index(tk.INSERT)
        
        # Tag timestamp as muted
        tag_t = f"t_{time.time()}"
        self.console.tag_add(tag_t, t_start, t_end)
        self.console.tag_config(tag_t, foreground=HUD_MUTED)
        
        # Insert message
        msg_start = self.console.index(tk.INSERT)
        self.console.insert(tk.END, f"{message}\n")
        msg_end = self.console.index(tk.INSERT)
        
        # Tag message
        tag_msg = f"msg_{time.time()}"
        self.console.tag_add(tag_msg, msg_start, msg_end)
        self.console.tag_config(tag_msg, foreground=color)
        
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)
        self.update_idletasks()

    def on_change_destination(self):
        from tkinter import filedialog
        new_path = filedialog.askdirectory(
            initialdir=self.cleaner.clean_folder_path,
            title=self.tr("choose_target_folder")
        )
        if new_path:
            self.cleaner.clean_folder_path = os.path.normpath(new_path)
            # Persist so next launch restores this choice
            self.cleaner.config["clean_folder_path"] = self.cleaner.clean_folder_path
            self.cleaner._save_config()
            self.lbl_dest.config(text=f"{self.tr('target')}{self.cleaner.clean_folder_path}")
            self.log_status(self.tr("status_dest_changed", self.cleaner.clean_folder_path))

    def _draw_cyber_switch(self, lang):
        w, h = 440, 152
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        
        # Glow layer behind the track
        glow_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        track_l, track_t, track_r, track_b = 70, 16, 370, 136
        glow_draw.rounded_rectangle([track_l - 4, track_t - 4, track_r + 4, track_b + 4], radius=66, fill=(0, 100, 255, 60))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(14))
        img = Image.alpha_composite(img, glow_layer)
        draw = ImageDraw.Draw(img)

        # 1. Flags (Poland and UK) next to the switch (glowing, rounded, high-fidelity)
        def draw_glowing_flag(flag_type):
            flag_w, flag_h = 56, 38
            flag_img = Image.new('RGBA', (flag_w, flag_h), (0, 0, 0, 0))
            
            content_img = Image.new('RGBA', (flag_w, flag_h), (0, 0, 0, 0))
            content_draw = ImageDraw.Draw(content_img)
            
            if flag_type == 'pl':
                content_draw.rectangle([0, 0, flag_w, flag_h//2], fill=(255, 255, 255, 255))
                content_draw.rectangle([0, flag_h//2, flag_w, flag_h], fill=(225, 28, 48, 255))
            else: # UK Flag
                content_draw.rectangle([0, 0, flag_w, flag_h], fill=(1, 33, 105, 255))
                # Diagonal white lines
                content_draw.line([-2, -2, flag_w+2, flag_h+2], fill=(255, 255, 255), width=5)
                content_draw.line([-2, flag_h+2, flag_w+2, -2], fill=(255, 255, 255), width=5)
                # Diagonal red lines
                content_draw.line([-2, -2, flag_w+2, flag_h+2], fill=(200, 16, 46), width=2)
                content_draw.line([-2, flag_h+2, flag_w+2, -2], fill=(200, 16, 46), width=2)
                # White cross
                content_draw.rectangle([flag_w//2 - 5, 0, flag_w//2 + 5, flag_h], fill=(255, 255, 255))
                content_draw.rectangle([0, flag_h//2 - 5, flag_w, flag_h//2 + 5], fill=(255, 255, 255))
                # Red cross
                content_draw.rectangle([flag_w//2 - 3, 0, flag_w//2 + 3, flag_h], fill=(200, 16, 46))
                content_draw.rectangle([0, flag_h//2 - 3, flag_w, flag_h//2 + 3], fill=(200, 16, 46))
                
            # Apply rounded corner mask to the flag content
            mask = Image.new('L', (flag_w, flag_h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([0, 0, flag_w, flag_h], radius=6, fill=255)
            
            flag_img.paste(content_img, (0, 0), mask)
            
            # Glow layer behind the flag
            glow_layer = Image.new('RGBA', (flag_w + 8, flag_h + 8), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)
            glow_draw.rounded_rectangle([2, 2, flag_w + 5, flag_h + 5], radius=8, outline=(0, 130, 255, 120), width=2)
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(2))
            
            final_flag = Image.new('RGBA', (flag_w + 8, flag_h + 8), (0, 0, 0, 0))
            final_flag.paste(glow_layer, (0, 0))
            final_flag.paste(flag_img, (4, 4), flag_img)
            
            # Specular highlight
            specular = Image.new('RGBA', (flag_w, flag_h), (0, 0, 0, 0))
            specular_draw = ImageDraw.Draw(specular)
            specular_draw.ellipse([-flag_w//2, -flag_h//2, flag_w*1.5, flag_h//2], fill=(255, 255, 255, 40))
            
            final_flag.paste(specular, (4, 4), mask)
            return final_flag

        pl_glowing = draw_glowing_flag('pl')
        uk_glowing = draw_glowing_flag('uk')
        img.paste(pl_glowing, (35 - 32, 76 - 23), pl_glowing)
        img.paste(uk_glowing, (405 - 32, 76 - 23), uk_glowing)

        # 2. Track background (very dark blue/black, glowing thin border)
        draw.rounded_rectangle([track_l, track_t, track_r, track_b], radius=60, fill=(10, 24, 40, 220), outline=(0, 130, 255, 200), width=2)

        # 3. Track dashed center line
        for x in range(120, 321, 16):
            draw.rectangle([x - 4, 76 - 1, x + 4, 76 + 1], fill=(0, 130, 255, 80))

        # 4. Text labels inside track
        try:
            font_txt = ImageFont.truetype('C:\\Windows\\Fonts\\segoeuib.ttf', 24)
        except:
            font_txt = ImageFont.load_default()

        if lang == 'pl':
            text_x = 280
            text_str = 'ENG'
            text_glow_color = (0, 130, 255, 180)
            text_fg_color = (0, 180, 255, 255)
        else:
            text_x = 160
            text_str = 'PL'
            text_glow_color = (0, 130, 255, 180)
            text_fg_color = (0, 180, 255, 255)

        # Render text shadow
        glow_text_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        glow_text_draw = ImageDraw.Draw(glow_text_layer)
        glow_text_draw.text((text_x, 76), text_str, font=font_txt, fill=text_glow_color, anchor='mm')
        glow_text_layer = glow_text_layer.filter(ImageFilter.GaussianBlur(5))
        img = Image.alpha_composite(img, glow_text_layer)
        draw = ImageDraw.Draw(img)
        
        draw.text((text_x, 76), text_str, font=font_txt, fill=text_fg_color, anchor='mm')

        # 5. 3D Glassmorphism Thumb
        thumb_x = track_l + 6 + 54 if lang == 'pl' else track_r - 6 - 54
        thumb_y = 76
        r = 54

        import math
        thumb_img = Image.new('RGBA', (r*2, r*2), (0, 0, 0, 0))
        pixels = thumb_img.load()
        
        # Draw 3D glass sphere mathematically
        for y in range(r*2):
            for x in range(r*2):
                nx = (x - r) / r
                ny = (y - r) / r
                dist_sq = nx*nx + ny*ny
                if dist_sq <= 1.0:
                    nz = math.sqrt(1.0 - dist_sq)
                    
                    # 1. Base dark blue sphere color
                    # Darker at the edges (nz is small)
                    edge_darkening = nz
                    r_base = int(10 * edge_darkening)
                    g_base = int(35 * edge_darkening)
                    b_base = int(90 * edge_darkening)
                    
                    # 2. Cyan core glow (center of the sphere)
                    core_glow = math.pow(1.0 - dist_sq, 1.5)
                    r_base += int(0 * core_glow)
                    g_base += int(180 * core_glow)
                    b_base += int(255 * core_glow)
                    
                    # 3. Soft bottom-right refraction (backlight refraction)
                    refr_dx = nx - 0.3
                    refr_dy = ny - 0.3
                    refr_dist = math.sqrt(refr_dx*refr_dx + refr_dy*refr_dy)
                    refraction = math.exp(- (refr_dist * refr_dist) / (2 * 0.45 * 0.45))
                    r_base += int(80 * refraction)
                    g_base += int(150 * refraction)
                    b_base += int(220 * refraction)
                    
                    # 4. Sharp top-left specular highlight
                    spec_dx = nx + 0.35
                    spec_dy = ny + 0.35
                    spec_dist = math.sqrt(spec_dx*spec_dx + spec_dy*spec_dy)
                    specular = math.exp(- (spec_dist * spec_dist) / (2 * 0.14 * 0.14))
                    
                    # 5. Secondary highlight for extra realism
                    spec2_dx = nx + 0.15
                    spec2_dy = ny + 0.45
                    spec2_dist = math.sqrt(spec2_dx*spec2_dx + spec2_dy*spec2_dy)
                    specular2 = math.exp(- (spec2_dist * spec2_dist) / (2 * 0.08 * 0.08)) * 0.6
                    
                    total_spec = specular + specular2
                    
                    r_final = min(255, max(0, r_base + int(255 * total_spec)))
                    g_final = min(255, max(0, g_base + int(255 * total_spec)))
                    b_final = min(255, max(0, b_base + int(255 * total_spec)))
                    
                    # Subtle outer glass glow edge
                    alpha = 255
                    if dist_sq > 0.95:
                        # Anti-alias edge
                        alpha = int(255 * (1.0 - dist_sq) / 0.05)
                        
                    pixels[x, y] = (r_final, g_final, b_final, alpha)

        # 5e. Outer glow ring around the thumb
        thumb_draw = ImageDraw.Draw(thumb_img)
        thumb_draw.ellipse([0, 0, r*2 - 1, r*2 - 1], outline=(0, 200, 255, 255), width=2)

        # Paste the thumb onto the image
        img.paste(thumb_img, (thumb_x - r, thumb_y - r), thumb_img)

        # Downscale with Lanczos for beautiful anti-aliased edges
        final_img = img.resize((150, 52), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(final_img)

    def _draw_bmc_button(self, hover=False):
        # Create a 160x42 image with transparent background
        width, height = 160, 42
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Buy Me a Coffee Brand Colors
        bg_color = (255, 221, 0, 255)
        text_color = (0, 0, 0, 255)
        
        # Cyberpunk ambient gold glow underneath
        for offset in range(3, 0, -1):
            alpha = int(45 / offset) if hover else int(22 / offset)
            draw.rounded_rectangle(
                [offset, offset, width - offset, height - offset],
                radius=10,
                fill=None,
                outline=(255, 221, 0, alpha),
                width=offset
            )
            
        # Draw main button body with custom border (white when hovered, black otherwise)
        draw.rounded_rectangle(
            [4, 4, width - 4, height - 4],
            radius=8,
            fill=bg_color,
            outline=(0, 0, 0, 255) if not hover else (255, 255, 255, 255),
            width=2
        )
        
        # Draw coffee cup icon programmatically (x=16 to 34, y=12 to 28)
        # Cup body: rounded bottom rectangle
        draw.rounded_rectangle(
            [16, 17, 30, 27],
            radius=3,
            fill=(0, 0, 0, 255),
            outline=None
        )
        # Cup handle
        draw.arc([27, 19, 34, 25], start=-90, end=90, fill=(0, 0, 0, 255), width=2)
        # Plate/Saucer
        draw.line([13, 29, 33, 29], fill=(0, 0, 0, 255), width=2)
        # Steam lines (three little wavy lines above the cup)
        draw.line([18, 14, 19, 11], fill=(0, 0, 0, 255), width=1)
        draw.line([22, 13, 23, 10], fill=(0, 0, 0, 255), width=1)
        draw.line([26, 14, 27, 11], fill=(0, 0, 0, 255), width=1)
        
        # Load bold, clean sans-serif font
        font = None
        for font_name in ["segoeuib.ttf", "segoeui.ttf", "arialbd.ttf", "arial.ttf"]:
            try:
                font = ImageFont.truetype(font_name, 11)
                break
            except:
                continue
        if font is None:
            font = ImageFont.load_default()
                
        # Draw text "Buy me a coffee" next to the cup
        draw.text((40, 14), "Buy me a coffee", fill=text_color, font=font)
        
        return ImageTk.PhotoImage(img)

    def on_header_resize(self, event):
        w = event.width
        h = event.height
        if w < 10 or h < 10:
            return
        try:
            banner_path = get_asset_path(os.path.join("images", "TopBaner.webp"))
            img = Image.open(banner_path)
            orig_w, orig_h = img.size
            
            # Left and right slices are 550px wide in the original 2016x512 image.
            # Scale them proportionally to match current canvas height (h)
            scale = h / orig_h
            logo_w = int(550 * scale)
            
            if logo_w * 2 >= w:
                # If window is too narrow, fallback to simple scaling
                img_scaled = img.resize((w, h), Image.Resampling.LANCZOS)
                self.header_banner_img = ImageTk.PhotoImage(img_scaled)
                self.header_canvas.itemconfig(self.canvas_bg_image, image=self.header_banner_img)
                x_start = int(w * 0.45)
            else:
                # Slice: left logo, right robot, stretchable middle panel
                left = img.crop((0, 0, 550, orig_h)).resize((logo_w, h), Image.Resampling.LANCZOS)
                right = img.crop((orig_w - 550, 0, orig_w, orig_h)).resize((logo_w, h), Image.Resampling.LANCZOS)
                mid = img.crop((550, 0, orig_w - 550, orig_h)).resize((w - 2 * logo_w, h), Image.Resampling.LANCZOS)
                
                # Combine the pieces
                stitched = Image.new("RGB", (w, h))
                stitched.paste(left, (0, 0))
                stitched.paste(mid, (logo_w, 0))
                stitched.paste(right, (w - logo_w, 0))
                
                self.header_banner_img = ImageTk.PhotoImage(stitched)
                self.header_canvas.itemconfig(self.canvas_bg_image, image=self.header_banner_img)
                x_start = logo_w + 55 # Align text slightly left (by ~4mm / 15px) after the logo circle
            
            y_center = int(h * 0.5)
            self.header_canvas.coords(self.canvas_info_window, x_start, y_center)
            
            # Position the language switch in the center top:
            y_pos = int(h * 0.5)
            self.header_canvas.coords(self.canvas_switch_image, int(w * 0.5), y_pos)
            
            # Position the Buy Me a Coffee button under the robot's head:
            if hasattr(self, "canvas_bmc_button") and self.canvas_bmc_button is not None:
                self.header_canvas.coords(self.canvas_bmc_button, int(w - logo_w * 0.5), int(h - 30))
        except Exception as e:
            logging.error(f"Error resizing top banner: {e}")

    def on_content_resize(self, event):
        w = event.width
        h = event.height
        if w < 10 or h < 10:
            return
        try:
            pcb_path = get_asset_path(os.path.join("images", "pcb2.webp"))
            img = Image.open(pcb_path)
            img_scaled = img.resize((w, h), Image.Resampling.LANCZOS)
            self.content_bg_img = ImageTk.PhotoImage(img_scaled)
            self.content_canvas.itemconfig(self.content_bg_image, image=self.content_bg_img)
        except Exception as e:
            logging.error(f"Error resizing content PCB background: {e}")

    def on_save_layout(self):
        """Save current desktop icon positions to a user-selected file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title=self.tr("save_layout_title")
        )
        if not file_path:
            return  # User cancelled
            
        def _worker():
            try:
                layout = save_icon_positions(file_path)
                self.after(0, lambda: self.log_status(
                    self.tr("status_layout_saved", len(layout))
                ))
            except Exception as e:
                logging.error(f"Save layout error: {e}")
                self.after(0, lambda err=e: self.log_status(
                    self.tr("status_layout_error", str(err))
                ))
        threading.Thread(target=_worker, daemon=True).start()

    def on_restore_layout(self):
        """Restore desktop icon positions from a user-selected file."""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title=self.tr("restore_layout_title")
        )
        if not file_path:
            return  # User cancelled

        def _worker():
            try:
                count = restore_icon_positions(file_path)
                self.after(0, lambda: self.log_status(
                    self.tr("status_layout_restored", count)
                ))
            except Exception as e:
                logging.error(f"Restore layout error: {e}")
                self.after(0, lambda err=e: self.log_status(
                    self.tr("status_layout_error", str(err))
                ))
        threading.Thread(target=_worker, daemon=True).start()

    def log_status(self, message):
        self.lbl_status.config(text=message)
        self.log_console(message)
        self.update_idletasks()

    def on_preview(self):
        logging.info("Starting Desktop Scan...")
        self.log_status("Status: Skanowanie...")
        self.scan_results = [] # Stores (name, size, type, category)
        self.item_selection_vars.clear()
        
        # Files
        files = self.cleaner.scan_desktop()
        for name, size in files:
            ext = os.path.splitext(name)[1]
            from .utils import get_category
            self.scan_results.append((name, size, "FILE", get_category(ext)))
        
        # Folders
        folders = self.cleaner.scan_desktop_folders()
        for name, size in folders:
            self.scan_results.append((name, size, "DIR", "FOLDER"))

        total_items = len(self.scan_results)
        if total_items == 0:
            self.log_status("Status: Pulpit jest czysty")
            self.pie_chart.set_data({})
        else:
            self.log_status(f"Status: Znaleziono {total_items} elementów do uporządkowania")
        
        self.update_category_checkboxes()
        self.filter_console()

    def on_search_changed(self, *args):
        """Debounces search query typing before filtering console."""
        if hasattr(self, '_search_debounce_id') and self._search_debounce_id is not None:
            self.after_cancel(self._search_debounce_id)
        
        self._search_debounce_id = self.after(250, self._trigger_filter)

    def _trigger_filter(self):
        self._search_debounce_id = None
        self.filter_console()

    def update_pie_chart_from_selections(self):
        """Calculates size of items that are selected by both category and individual checkbox."""
        query = self.var_search.get().lower()
        chart_data = {}
        for name, size, kind, cat in self.scan_results:
            if kind == "FILE" and not self.category_vars.get(cat, tk.BooleanVar(value=True)).get():
                continue
            if not self.item_selection_vars.get(name, tk.BooleanVar(value=True)).get():
                continue
            if not query or query in name.lower() or query in kind.lower() or query in cat.lower():
                chart_data[cat] = chart_data.get(cat, 0) + size
        self.pie_chart.set_data(chart_data)

    def insert_item_row(self, name, size_str, kind, cat):
        """Inserts an interactive file/folder checkbox row into the console text area."""
        self.console.config(state=tk.NORMAL)
        
        if name not in self.item_selection_vars:
            self.item_selection_vars[name] = tk.BooleanVar(value=True)
            
        var = self.item_selection_vars[name]
        
        def on_toggle():
            self.update_pie_chart_from_selections()
            
        if self.no_skin:
            chk = tk.Checkbutton(
                self.console, 
                variable=var, 
                command=on_toggle
            )
        else:
            chk = tk.Checkbutton(
                self.console, 
                variable=var, 
                bg=HUD_PANEL, 
                activebackground=HUD_PANEL,
                selectcolor=HUD_PANEL, 
                bd=0, 
                highlightthickness=0, 
                command=on_toggle
            )
        
        self.console.window_create(tk.END, window=chk)
        
        # Insert timestamp in muted color
        now = datetime.now()
        timestamp = f" [{now.hour:02d}:{now.minute:02d}:{now.second:02d}] "
        t_start = self.console.index(tk.INSERT)
        self.console.insert(tk.END, timestamp)
        t_end = self.console.index(tk.INSERT)
        tag_t = f"t_{time.time()}_{name.replace(' ', '_')}"
        self.console.tag_add(tag_t, t_start, t_end)
        self.console.tag_config(tag_t, foreground=HUD_MUTED)
        
        # Insert entry text: name in dark, metadata in muted
        kind_name = self.tr("folder") if kind in ("DIR", "FOLDER") else self.tr("file")
        name_start = self.console.index(tk.INSERT)
        self.console.insert(tk.END, f"  {name}")
        name_end = self.console.index(tk.INSERT)
        tag_name = f"name_{time.time()}_{name.replace(' ', '_')}"
        self.console.tag_add(tag_name, name_start, name_end)
        if self.no_skin:
            self.console.tag_config(tag_name, font=("Segoe UI Semibold", 10))
        else:
            self.console.tag_config(tag_name, foreground=HUD_TEXT, font=("Segoe UI Semibold", 10))

        meta_start = self.console.index(tk.INSERT)
        self.console.insert(tk.END, f"  ·  {kind_name}  ·  {cat}  ·  {size_str}\n")
        meta_end = self.console.index(tk.INSERT)
        tag_meta = f"meta_{time.time()}_{name.replace(' ', '_')}"
        self.console.tag_add(tag_meta, meta_start, meta_end)
        if self.no_skin:
            self.console.tag_config(tag_meta, font=("Segoe UI", 9))
        else:
            self.console.tag_config(tag_meta, foreground=HUD_MUTED, font=("Segoe UI", 9))

        # Whole row tag for context menu exclusion
        tag_row = f"row_{time.time()}_{name.replace(' ', '_')}"
        self.console.tag_add(tag_row, t_start, meta_end)
        
        def show_context_menu(event, item_name=name):
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label=self.tr("exclude_perm_menu", item_name), command=lambda: self.exclude_item_permanently(item_name))
            menu.post(event.x_root, event.y_root)
            
        self.console.tag_bind(tag_row, "<Button-2>", show_context_menu)
        self.console.tag_bind(tag_row, "<Button-3>", show_context_menu)

        self.console.config(state=tk.DISABLED)

    def exclude_item_permanently(self, name):
        if "ignored_items" not in self.cleaner.config:
            self.cleaner.config["ignored_items"] = []
        if name not in self.cleaner.config["ignored_items"]:
            self.cleaner.config["ignored_items"].append(name)
            self.cleaner._save_config()
            
        self.cleaner.ignore_files.add(name.lower())
        self.log_status(self.tr("status_excluded_perm", name))
        self.on_preview() # Refresh the list immediately!

    def filter_console(self):
        """Filters the display based on search variable and updates chart."""
        query = self.var_search.get().lower()
        
        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.console.config(state=tk.DISABLED)
        
        for name, size, kind, cat in self.scan_results:
            if kind == "FILE" and not self.category_vars.get(cat, tk.BooleanVar(value=True)).get():
                continue
            if not query or query in name.lower() or query in kind.lower() or query in cat.lower():
                size_kb = size / 1024
                size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
                self.insert_item_row(name, size_str, kind, cat)
        
        self.update_pie_chart_from_selections()
        self.console.see(tk.END)

    def update_category_checkboxes(self):
        # Clear container
        for widget in self.checkbox_container.winfo_children():
            widget.destroy()
            
        # Get unique categories of files in scan results
        found_categories = sorted(list({item[3] for item in self.scan_results if item[2] == "FILE"}))
        
        if not found_categories:
            if self.no_skin:
                lbl = tk.Label(self.checkbox_container, text=self.tr("no_file_categories"), font=("Segoe UI", 9))
            else:
                lbl = tk.Label(self.checkbox_container, text=self.tr("no_file_categories"), font=("Segoe UI", 9), fg=HUD_MUTED, bg=HUD_PANEL)
            lbl.pack(pady=10)
            return
            
        # Create checkboxes
        columns = 2
        for idx, cat in enumerate(found_categories):
            if cat not in self.category_vars:
                self.category_vars[cat] = tk.BooleanVar(value=True)
                
            var = self.category_vars[cat]
            if self.no_skin:
                chk = tk.Checkbutton(self.checkbox_container, text=cat, variable=var, font=("Segoe UI", 9), command=self.filter_console)
            else:
                chk = tk.Checkbutton(self.checkbox_container, text=cat, variable=var, bg=HUD_PANEL, fg=HUD_TEXT,
                                     selectcolor=HUD_PANEL, activebackground=HUD_PANEL,
                                     activeforeground=HUD_CYAN, font=("Segoe UI", 9),
                                     bd=0, highlightthickness=0, command=self.filter_console)
            row = idx // columns
            col = idx % columns
            chk.grid(row=row, column=col, sticky="w", padx=5, pady=2)

    def select_all_categories(self):
        for var in self.category_vars.values():
            var.set(True)
        self.filter_console()

    def select_none_categories(self):
        for var in self.category_vars.values():
            var.set(False)
        self.filter_console()

    def on_clean(self, auto=False):
        """
        Main clean logic. 
        If auto=True, we rely on Preview's default [x] selection (we must run preview logic internally first).
        """
        
        if auto:
             # Auto-clean needs to find files first
             files = self.cleaner.scan_desktop()
             folders = self.cleaner.scan_desktop_folders()
             
             # Default: Move everything found but respect target category selections if defined
             from .utils import get_category
             files_to_process = [
                 f[0] for f in files 
                 if self.category_vars.get(get_category(os.path.splitext(f[0])[1]), tk.BooleanVar(value=True)).get()
             ]
             folders_to_process = [f[0] for f in folders]
             
             if not files_to_process and not folders_to_process:
                 return # Silence

        else:
            # GUI Manual Mode
            if not self.scan_results:
                 self.on_preview()
                 
            files_to_process = [
                item[0] for item in self.scan_results 
                if item[2] == "FILE" and self.category_vars.get(item[3], tk.BooleanVar(value=True)).get() and self.item_selection_vars.get(item[0], tk.BooleanVar(value=True)).get()
            ]
            folders_to_process = [
                item[0] for item in self.scan_results 
                if item[2] == "DIR" and self.item_selection_vars.get(item[0], tk.BooleanVar(value=True)).get()
            ]

        total_count = len(files_to_process) + len(folders_to_process)

        if total_count == 0:
            logging.info("Clean aborted: No items selected.")
            if not auto: messagebox.showinfo(self.tr("info_title"), self.tr("msg_no_items_selected"))
            return

        # Confirm only for manual
        if not auto:
            confirm = True
            if total_count > 10:
                confirm = messagebox.askyesno(self.tr("confirm_title"), self.tr("msg_confirm_clean", total_count))
            if not confirm:
                logging.info("Clean aborted by user confirmation.")
                return

        logging.info(f"Executing clean on {total_count} items...")
        self.log_status(self.tr("status_cleaning") if not auto else self.tr("status_auto_cleaning"))
        if not auto:
            self.progress["maximum"] = total_count
            self.progress["value"] = 0
            self.progress.start(10)
            self.update()
        
        moves_batch = []
        errors_batch = []
        
        # 2. Files
        if files_to_process:
             f_moved, f_errors = self.cleaner.organize_files(files_to_process, dry_run=False)
             moves_batch.extend(f_moved)
             errors_batch.extend(f_errors)

        # 3. Folders
        if folders_to_process:
             d_moved, d_errors = self.cleaner.organize_folders(folders_to_process, dry_run=False)
             moves_batch.extend(d_moved)
             errors_batch.extend(d_errors)

        # 4. History
        if moves_batch:
             self.undo_manager.push_history(moves_batch)
        
        if not auto:
            self.progress.stop()
            self.progress["value"] = 100
            self.on_preview()
            
            if errors_batch:
                for err in errors_batch: self.log_console(f"{self.tr('error_prefix')}: {err}", is_error=True)
                self.log_status(self.tr("status_clean_errors", len(errors_batch)))
            else:
                self.log_status(self.tr("status_clean_success", total_count))
            
            self.btn_undo.config(state=tk.NORMAL if self.undo_manager.has_history() else tk.DISABLED)
        else:
             self.log_status(self.tr("status_auto_clean_success", len(moves_batch)))


    def on_undo(self):
        if not self.undo_manager.has_history():
            self.log_status(self.tr("status_no_undo_history"))
            return
            
        if not messagebox.askyesno(self.tr("undo_title"), self.tr("msg_confirm_undo")):
            return

        self.log_status(self.tr("status_undoing"))
        success, errors = self.undo_manager.undo_last()
        
        if errors:
             messagebox.showwarning(self.tr("undo_errors_title"), "\n".join(errors))
        
        self.log_status(self.tr("status_undo_success", success))
        self.btn_undo.config(state=tk.NORMAL if self.undo_manager.has_history() else tk.DISABLED)
        
        self.on_preview() # Refresh

    def on_settings(self):
        root = tk.Toplevel(self)
        root.title(self.tr("settings_title"))
        root.geometry("450x570")
        root.configure(bg=HUD_BG)
        root.transient(self) 
        
        # Main Tab Control
        settings_tabs = ttk.Notebook(root)
        settings_tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 1. GENERAL TAB
        tab_general = ttk.Frame(settings_tabs, padding=20)
        settings_tabs.add(tab_general, text=self.tr("tab_general"))

        # Exclusions Frame
        ex_frame = ttk.Labelframe(tab_general, text=self.tr("frame_sys_exclusions"), padding=15)
        ex_frame.pack(fill=tk.X, pady=5)
        
        chk_lnk = ttk.Checkbutton(ex_frame, text=self.tr("chk_exclude_lnk"), variable=self.var_exclude_lnk, command=self.apply_exclusions)
        chk_lnk.pack(anchor=tk.W, pady=5)
        
        chk_ico = ttk.Checkbutton(ex_frame, text=self.tr("chk_exclude_ico"), variable=self.var_exclude_ico, command=self.apply_exclusions)
        chk_ico.pack(anchor=tk.W, pady=5)
        
        # Auto-Clean Frame
        au_frame = ttk.Labelframe(tab_general, text=self.tr("frame_auto"), padding=15)
        au_frame.pack(fill=tk.X, pady=15)
        
        lbl_auto = ttk.Label(au_frame, text=self.tr("lbl_auto_freq"))
        lbl_auto.pack(anchor=tk.W)
        combo_interval = ttk.Combobox(au_frame, textvariable=self.var_auto_interval, state="readonly", 
                                      values=["Off", "5m", "15m", "30m", "1h", "6h", "12h", "24h"])
        combo_interval.pack(fill=tk.X, pady=10)
        
        def on_interval_selected(event):
            self.cleaner.config["auto_interval"] = self.var_auto_interval.get()
            self.cleaner._save_config()
            self.log_status(self.tr("status_interval", self.var_auto_interval.get()))
            
        combo_interval.bind("<<ComboboxSelected>>", on_interval_selected)
        
        ttk.Separator(au_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        chk_peek = ttk.Checkbutton(au_frame, text=self.tr("chk_peek"), variable=self.var_enable_peek, command=self.apply_peek_settings)
        chk_peek.pack(anchor=tk.W, pady=5)

        chk_dated = ttk.Checkbutton(au_frame, text=self.tr("chk_dated"), variable=self.var_dated_folders, command=self.apply_dated_folders_settings)
        chk_dated.pack(anchor=tk.W, pady=5)

        chk_skip_folders = ttk.Checkbutton(au_frame, text=self.tr("chk_skip_folders"), variable=self.var_skip_folders, command=self.apply_skip_folders_settings)
        chk_skip_folders.pack(anchor=tk.W, pady=5)

        # Language Frame
        lang_frame = ttk.Labelframe(tab_general, text=self.tr("frame_lang"), padding=15)
        lang_frame.pack(fill=tk.X, pady=5)
        
        lbl_lang_lbl = ttk.Label(lang_frame, text=self.tr("lbl_select_lang"))
        lbl_lang_lbl.pack(anchor=tk.W)
        
        self.var_lang_choice = tk.StringVar(value=self.cleaner.config.get("lang", "pl"))
        combo_lang = ttk.Combobox(lang_frame, textvariable=self.var_lang_choice, state="readonly", values=["pl", "en"])
        combo_lang.pack(fill=tk.X, pady=10)
        
        # 2. CATEGORIES TAB
        tab_categories = ttk.Frame(settings_tabs, padding=20)
        settings_tabs.add(tab_categories, text=self.tr("tab_categories"))
        
        cat_editor = CategoryEditor(tab_categories, self)
        cat_editor.pack(fill=tk.BOTH, expand=True)

        # 3. EXCLUSIONS TAB
        tab_exclusions = ttk.Frame(settings_tabs, padding=20)
        settings_tabs.add(tab_exclusions, text=self.tr("tab_exclusions"))

        lbl_ex = ttk.Label(tab_exclusions, text=self.tr("lbl_perm_ex"), font=("Segoe UI Semibold", 9))
        lbl_ex.pack(anchor=tk.W, pady=(0, 5))
        
        list_frame = ttk.Frame(tab_exclusions)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        if self.no_skin:
            self.permanent_ex_list = tk.Listbox(list_frame, font=("Segoe UI", 9))
        else:
            self.permanent_ex_list = tk.Listbox(list_frame, bg=HUD_PANEL, fg=HUD_TEXT,
                                               selectbackground=HUD_CYAN, selectforeground=HUD_BG,
                                               borderwidth=0, highlightthickness=0, font=("Segoe UI", 9))
        self.permanent_ex_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.permanent_ex_list.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.permanent_ex_list.config(yscrollcommand=scroll.set)
        
        # Populate
        ignored_list = self.cleaner.config.get("ignored_items", [])
        for item in sorted(ignored_list):
            self.permanent_ex_list.insert(tk.END, item)
            
        # Add exclusion input row
        add_frame = ttk.Frame(tab_exclusions)
        add_frame.pack(fill=tk.X, pady=(5, 5))
        
        lbl_new_ex_lbl = ttk.Label(add_frame, text=self.tr("lbl_new_ex"))
        lbl_new_ex_lbl.pack(side=tk.LEFT, padx=(0, 5))
        ent_add = ttk.Entry(add_frame)
        ent_add.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        def add_new_exclusion():
            val = ent_add.get().strip()
            if not val:
                return
            ignored_list = self.cleaner.config.setdefault("ignored_items", [])
            if val not in ignored_list:
                ignored_list.append(val)
                self.cleaner.config["ignored_items"] = ignored_list
                self.cleaner._save_config()
                
                # Update memory ignore list
                self.cleaner.ignore_files.add(val.lower())
                
                # Re-populate Listbox
                self.permanent_ex_list.insert(tk.END, val)
                ent_add.delete(0, tk.END)
                self.log_status(self.tr("status_added_ex", val))
                self.on_preview() # Refresh main list
                
        btn_add = ttk.Button(add_frame, text=self.tr("btn_add"), command=add_new_exclusion)
        btn_add.pack(side=tk.RIGHT)
            
        btn_frame = ttk.Frame(tab_exclusions)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        def remove_selected_exclusion():
            selection = self.permanent_ex_list.curselection()
            if not selection:
                return
            item_name = self.permanent_ex_list.get(selection[0])
            if item_name in self.cleaner.config.get("ignored_items", []):
                self.cleaner.config["ignored_items"].remove(item_name)
                self.cleaner._save_config()
                # Remove from active memory ignored files
                if item_name.lower() in self.cleaner.ignore_files:
                    self.cleaner.ignore_files.remove(item_name.lower())
                # Re-populate
                self.permanent_ex_list.delete(selection[0])
                self.log_status(self.tr("status_removed_ex", item_name))
                self.on_preview() # Refresh main list
                
        btn_remove = ttk.Button(btn_frame, text=self.tr("btn_remove_selected"), command=remove_selected_exclusion)
        btn_remove.pack(side=tk.LEFT)

        # Footer
        footer_frame = tk.Frame(root, bg=HUD_BG)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        btn_close = ttk.Button(footer_frame, text=self.tr("btn_close"), command=root.destroy)
        btn_close.pack()

        def on_lang_selected(event):
            new_lang = self.var_lang_choice.get()
            self.cleaner.config["lang"] = new_lang
            self.cleaner._save_config()
            
            root.title(self.tr("settings_title"))
            settings_tabs.tab(tab_general, text=self.tr("tab_general"))
            settings_tabs.tab(tab_categories, text=self.tr("tab_categories"))
            settings_tabs.tab(tab_exclusions, text=self.tr("tab_exclusions"))
            
            ex_frame.config(text=self.tr("frame_sys_exclusions"))
            chk_lnk.config(text=self.tr("chk_exclude_lnk"))
            chk_ico.config(text=self.tr("chk_exclude_ico"))
            
            au_frame.config(text=self.tr("frame_auto"))
            lbl_auto.config(text=self.tr("lbl_auto_freq"))
            chk_peek.config(text=self.tr("chk_peek"))
            chk_dated.config(text=self.tr("chk_dated"))
            chk_skip_folders.config(text=self.tr("chk_skip_folders"))
            
            lang_frame.config(text=self.tr("frame_lang"))
            lbl_lang_lbl.config(text=self.tr("lbl_select_lang"))
            
            lbl_ex.config(text=self.tr("lbl_perm_ex"))
            lbl_new_ex_lbl.config(text=self.tr("lbl_new_ex"))
            btn_add.config(text=self.tr("btn_add"))
            btn_remove.config(text=self.tr("btn_remove_selected"))
            btn_close.config(text=self.tr("btn_close"))
            
            cat_editor.update_language(self)
            self.update_language()
            
        combo_lang.bind("<<ComboboxSelected>>", on_lang_selected)

    def update_language(self):
        self.load_button_images()
        self.lbl_active_status.config(text=self.tr("status_active"))
        self.lbl_path.config(text=f"{self.tr('desktop')}{self.cleaner.desktop_path}")
        self.lbl_dest.config(text=f"{self.tr('target')}{self.cleaner.clean_folder_path}")
        self.lbl_status.config(text=self.tr("ready"))
        self.btn_change_dest.config(text=self.tr("change"))
        self.lbl_items_header.config(text=self.tr("items_to_organize"))
        self.lbl_filter.config(text=self.tr("filter"))
        self.lbl_categories_title.config(text=self.tr("categories"))
        self.btn_select_all.config(text=self.tr("all"))
        self.btn_select_none.config(text=self.tr("none"))

        if not self.no_skin and hasattr(self, "header_canvas"):
            lang = self.cleaner.config.get("lang", "pl")
            active_img = self.switch_eng_img if lang == "en" else self.switch_pl_img
            self.header_canvas.itemconfig(self.canvas_switch_image, image=active_img)

        if self.no_skin:
            self.btn_preview.config(text=self.tr("btn_preview"))
            self.btn_clean.config(text=self.tr("btn_clean"))
            self.btn_undo.config(text=self.tr("btn_undo"))
            self.btn_settings.config(text=self.tr("btn_settings"))
            self.btn_save_layout.config(text=self.tr("btn_save_layout"))
            self.btn_restore_layout.config(text=self.tr("btn_restore_layout"))
        else:
            # Update Preview Button
            if "preview" in self.btn_imgs:
                self.btn_preview.config(image=self.btn_imgs["preview"], text="")
            else:
                self.btn_preview.config(image="", text=self.tr("btn_preview"))

            # Update Clean Button
            if "clean" in self.btn_imgs:
                self.btn_clean.config(image=self.btn_imgs["clean"], text="")
            else:
                self.btn_clean.config(image="", text=self.tr("btn_clean"))

            # Update Undo Button
            if "undo" in self.btn_imgs:
                self.btn_undo.config(image=self.btn_imgs["undo"], text="")
            else:
                self.btn_undo.config(image="", text=self.tr("btn_undo"))

            # Update Settings Button
            if "settings" in self.btn_imgs:
                self.btn_settings.config(image=self.btn_imgs["settings"], text="",
                                         bg=HUD_BG, activebackground=HUD_BG, highlightthickness=0)
            else:
                self.btn_settings.config(image="", text=self.tr("btn_settings"),
                                         bg=HUD_PANEL, activebackground=HUD_PANEL)

            # Update Save Layout Button
            if "save_layout" in self.btn_imgs:
                self.btn_save_layout.config(image=self.btn_imgs["save_layout"], text="",
                                            bg=HUD_BG, activebackground=HUD_BG, highlightthickness=0)
            else:
                self.btn_save_layout.config(image="", text=self.tr("btn_save_layout"),
                                            bg=HUD_PANEL, activebackground=HUD_PANEL)

            # Update Restore Layout Button
            if "restore_layout" in self.btn_imgs:
                self.btn_restore_layout.config(image=self.btn_imgs["restore_layout"], text="",
                                               bg=HUD_BG, activebackground=HUD_BG, highlightthickness=0)
            else:
                self.btn_restore_layout.config(image="", text=self.tr("btn_restore_layout"),
                                               bg=HUD_PANEL, activebackground=HUD_PANEL)

        # Refresh console to update translations (Plik/Folder)
        self.filter_console()

    def apply_exclusions(self):
        exclusions = []
        if self.var_exclude_lnk.get():
            exclusions.append(".lnk")
        if self.var_exclude_ico.get():
            exclusions.append(".ico")
        
        self.cleaner.set_exclusions(exclusions)
        self.log_status(self.tr("status_updating_ex", exclusions))
        
    def apply_peek_settings(self):
        if self.var_enable_peek.get():
            self.peek_manager.start()
            self.log_status(self.tr("status_peek_on"))
        else:
            self.peek_manager.stop()
            self.log_status(self.tr("status_peek_off"))


    def apply_dated_folders_settings(self):
        enabled = self.var_dated_folders.get()
        self.cleaner.set_dated_folders(enabled)
        status = "WŁĄCZONE" if (self.cleaner.config.get("lang", "pl") == "pl") else "ENABLED"
        if not enabled:
            status = "WYŁĄCZONE" if (self.cleaner.config.get("lang", "pl") == "pl") else "DISABLED"
        self.log_status(self.tr("status_dated", status))

    def apply_skip_folders_settings(self):
        enabled = self.var_skip_folders.get()
        self.cleaner.set_skip_folders(enabled)
        status = "WŁĄCZONE" if (self.cleaner.config.get("lang", "pl") == "pl") else "ENABLED"
        if not enabled:
            status = "WYŁĄCZONE" if (self.cleaner.config.get("lang", "pl") == "pl") else "DISABLED"
        self.log_status(self.tr("status_skip_folders", status))

    def check_capacity_loop(self):
        """Monitors desktop load every 5 minutes."""
        try:
            curr, maxi, percent = self.cleaner.get_current_load()
            if percent > 80 and not self.alert_active:
                self.show_tactical_alert(curr, maxi)
            elif percent <= 80:
                self.alert_active = False
        except Exception:
            pass # Suppress errors to keep the loop running
        self.after(300000, self.check_capacity_loop) # 5 min

    def show_tactical_alert(self, count, limit):
        self.alert_active = True
        alert = tk.Toplevel(self)
        alert.overrideredirect(True)
        alert.attributes("-topmost", True)
        
        # Bottom-right positioning
        sw = alert.winfo_screenwidth()
        sh = alert.winfo_screenheight()
        w, h = 300, 120
        alert.geometry(f"{w}x{h}+{sw-w-20}+{sh-h-60}")
        
        container = tk.Frame(alert, bg=HUD_BG, highlightthickness=1, highlightbackground="#CCCCCC")
        container.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(container, text=self.tr("alert_title"), font=("Segoe UI Semibold", 10), fg=HUD_RED, bg=HUD_BG).pack(pady=(10, 5))
        tk.Label(container, text=self.tr("alert_text", count, limit, int(count/limit*100)), font=("Segoe UI", 9), fg=HUD_TEXT, bg=HUD_BG).pack()
        
        btn_frame = tk.Frame(container, bg=HUD_BG)
        btn_frame.pack(pady=10)
        
        def on_alert_clean():
            self.deiconify()
            self.on_clean(auto=False)
            alert.destroy()
            
        if self.no_skin:
            btn = tk.Button(btn_frame, text=self.tr("alert_btn"), command=on_alert_clean)
        else:
            btn = GlowButton(btn_frame, text=self.tr("alert_btn"), command=on_alert_clean, width=180, height=35, color=HUD_CYAN)
        btn.pack()
        
        # Auto-dismiss after 30s
        def _dismiss():
            try: alert.destroy()
            except: pass
        alert.after(30000, _dismiss)

    def dump_memory_stats(self):
        """Diagnose memory consumption to a log file."""
        import sys
        if "pytest" in sys.modules:
            return
        import tracemalloc
        if not tracemalloc.is_tracing():
            return
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        # Write top memory allocations to workspace file
        log_path = os.path.join(os.path.dirname(__file__), "..", "memory_audit.log")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"--- MEMORY SNAPSHOT --- {datetime.now()}\n")
                for index, stat in enumerate(top_stats[:15]):
                    f.write(f"#{index+1}: {stat.count} blocks, {stat.size / 1024:.1f} KiB\n")
                    f.write(f"  {stat.traceback.format()[0].strip()}\n")
        except Exception as e:
            print(f"Error dumping memory stats: {e}")

    def check_schedule(self):
        """Runs every 30 seconds to check if we should auto-clean."""
        interval_str = self.var_auto_interval.get()
        
        if interval_str != "Off":
            minutes = 0
            if interval_str == "5m": minutes = 5
            elif interval_str == "15m": minutes = 15
            elif interval_str == "30m": minutes = 30
            elif interval_str == "1h": minutes = 60
            elif interval_str == "6h": minutes = 360
            elif interval_str == "12h": minutes = 720
            elif interval_str == "24h": minutes = 1440
            
            if minutes > 0:
                elapsed = datetime.now() - self.last_auto_clean
                if elapsed >= timedelta(minutes=minutes):
                    try:
                        self.on_clean(auto=True)
                        self.last_auto_clean = datetime.now()
                        self.cleaner.config["last_auto_clean"] = self.last_auto_clean.isoformat()
                        self.cleaner._save_config()
                    except Exception as e:
                        logging.error(f"Auto-clean error: {e}")
        
        # Performance/memory leak audit: dump memory stats
        self.dump_memory_stats()
        self.after(30000, self.check_schedule) # Loop every 30 seconds

    def on_minimize(self, event=None):
        if event and event.widget == self:
            if self.state() == "iconic":
                self.withdraw()  # Hide from taskbar
                if not self.tray_icon:
                    threading.Thread(target=self.create_tray_icon, daemon=True).start()

    def create_tray_icon(self):
        if hasattr(self, "cached_tray_image") and self.cached_tray_image is not None:
            image = self.cached_tray_image
        else:
            # Load sweepy_ligh400x400.webp as the tray icon with circular crop
            tray_loaded = False
            for candidate in [
                get_asset_path(os.path.join("images", "sweepy_ligh400x400.webp")),
                get_asset_path(os.path.join("images", "sweepy_ligh.webp")),
            ]:
                if os.path.exists(candidate):
                    try:
                        raw = Image.open(candidate).convert("RGBA")
                        w, h = raw.size
                        side = min(w, h)
                        raw = raw.crop(((w - side) // 2, (h - side) // 2,
                                        (w + side) // 2, (h + side) // 2))
                        # Circular mask
                        mask = Image.new("L", (side, side), 0)
                        ImageDraw.Draw(mask).ellipse([0, 0, side - 1, side - 1], fill=255)
                        raw.putalpha(mask)
                        image = raw.resize((64, 64), Image.Resampling.LANCZOS)
                        tray_loaded = True
                        break
                    except Exception as e:
                        logging.error(f"Tray icon load failed ({candidate}): {e}")
            if not tray_loaded:
                # Fallback: simple blue circle with broom
                image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
                d = ImageDraw.Draw(image)
                d.ellipse([4, 4, 60, 60], fill=(0, 103, 192, 255))
                d.line([(32, 38), (32, 18)], fill=(255, 255, 255, 255), width=4)
                d.polygon([(24, 38), (40, 38), (44, 46), (20, 46)], fill=(255, 255, 255, 255))
            self.cached_tray_image = image

        menu = pystray.Menu(
            pystray.MenuItem('Otwórz program', self.show_window),
            pystray.MenuItem('Skanuj i Sprzątnij', self.on_tray_clean),
            pystray.MenuItem('Wyjdź', self.quit_app)
        )

        self.tray_icon = pystray.Icon("Sweeply", image, "Sweeply", menu)
        self.tray_icon.run()

    def on_tray_clean(self, icon=None, item=None):
        self.show_window()
        self.after(500, lambda: self.on_clean())

    def on_close_window(self):
        # Always minimize to system tray on "X" button close
        self.withdraw() # Hide window
        if not self.tray_icon: # Start tray thread if not running
             threading.Thread(target=self.create_tray_icon, daemon=True).start()

    def show_window(self, icon=None, item=None):
        self.after(0, lambda: [self.deiconify(), self.lift(), self.focus_force()])
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def quit_app(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()

    def start_main_app(self):
        # Center main window
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        main_w, main_h = 860, 650
        x = (screen_w - main_w) // 2
        y = (screen_h - main_h) // 2
        self.geometry(f"{main_w}x{main_h}+{x}+{y}")
        
        self._create_widgets()
        self.update_language()
        
        # Make window fully opaque (disable transparency)
        try:
            self.attributes("-alpha", 1.0)
        except:
            pass
            
        # Apply defaults immediately
        self.apply_exclusions()
        
        # Handle Close -> Minimize logic
        self.protocol("WM_DELETE_WINDOW", self.on_close_window)
        self.bind("<Unmap>", self.on_minimize)
        
        # Start Scheduler & Capacity Monitor
        self.alert_active = False
        self.check_schedule()
        self.check_capacity_loop()
        
        self.deiconify()
        self.focus_force()
        self.lift()
        self.attributes("-topmost", True)
        self.after(1000, lambda: self.attributes("-topmost", False))

    def show_splash_screen(self):
        splash_path = get_asset_path("splash3.webp")
        if not os.path.exists(splash_path):
            splash_path = get_asset_path("best2.webp")
        if not os.path.exists(splash_path):
            splash_path = get_asset_path(os.path.join("images", "sweepy_ligh.webp"))
        if not os.path.exists(splash_path):
            logo_cand = get_asset_path("logo_transparent.webp")
            if os.path.exists(logo_cand):
                splash_path = logo_cand
            else:
                self.start_main_app()
                return

        try:
            # Create a separate, transient TopLevel window for the splash screen
            splash = tk.Toplevel(self)
            splash.overrideredirect(True) # Borderless splash
            splash.configure(bg=HUD_BG)
            
            img_raw = Image.open(splash_path)
            orig_w, orig_h = img_raw.size
            # Nice size for splash screen width: 500
            target_w = 500
            target_h = int(orig_h * (target_w / orig_w))
            
            img_scaled = img_raw.resize((target_w, target_h), Image.Resampling.LANCZOS)
            self.splash_img = ImageTk.PhotoImage(img_scaled)
            
            # Centering
            screen_w = splash.winfo_screenwidth()
            screen_h = splash.winfo_screenheight()
            x = (screen_w - target_w) // 2
            y = (screen_h - target_h) // 2
            splash.geometry(f"{target_w}x{target_h}+{x}+{y}")
            
            # Canvas to hold image and overlay transparent logs
            canvas = tk.Canvas(splash, width=target_w, height=target_h, bd=0, highlightthickness=0, bg=HUD_BG)
            canvas.pack(fill=tk.BOTH, expand=True)
            canvas.create_image(0, 0, anchor=tk.NW, image=self.splash_img)
            
            # Keep splash on top
            splash.attributes("-topmost", True)
            splash.update()
            
            timeout = 2500 if "pytest" not in sys.modules else 0
            
            # Keep track of active log lines
            self.splash_lines = []
            
            # Dynamic coordinate mapping inside the gray box area
            # Box area is approx y: 690-925, x: 60-900 on 961x965 original
            y_start = int(target_h * (690 / 965))
            y_end = int(target_h * (925 / 965))
            x_start = int(target_w * (60 / 961))
            time_offset = int(target_w * (150 / 961))
            
            # Compute line spacing based on height of the gray box
            max_lines = 7
            line_height = (y_end - y_start) // max_lines
            
            log_steps = [
                (0, "[SYSTEM] Inicjalizacja rdzenia Sweeply..."),
                (350, "[CONFIG] Wczytywanie konfiguracji systemowej..."),
                (700, f"[HARDWARE] Wykryto pulpit: {self.cleaner.desktop_path}"),
                (1050, f"[STATUS] Załadowano {len(self.cleaner.ignore_files)} reguł wykluczeń."),
                (1400, "[HUD] Inicjalizacja silnika graficznego z Fluent Design..."),
                (1750, "[SCHEDULER] Synchronizacja harmonogramu zadań..."),
                (2100, "[READY] Sweeply gotowy. Uruchamianie interfejsu..."),
            ]
            
            def add_log(msg):
                try:
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    self.splash_lines.append((timestamp, msg))
                    if len(self.splash_lines) > max_lines:
                        self.splash_lines.pop(0)
                    
                    # Redraw log lines transparently on Canvas
                    canvas.delete("log_text")
                    for idx, (t_stamp, text) in enumerate(self.splash_lines):
                        y_pos = y_start + idx * line_height + 4
                        # Draw timestamp
                        canvas.create_text(x_start, y_pos, text=t_stamp, fill=HUD_CYAN,
                                           font=("Consolas", 8, "bold"), anchor=tk.NW, tags="log_text")
                        # Draw message
                        canvas.create_text(x_start + time_offset, y_pos, text=text, fill=HUD_TEXT,
                                           font=("Consolas", 8), anchor=tk.NW, tags="log_text")
                    canvas.update()
                except:
                    pass
            
            for delay, msg in log_steps:
                if timeout == 0:
                    add_log(msg)
                else:
                    self.after(delay, lambda m=msg: add_log(m))
            
            # Transition to main window
            def close_splash():
                try:
                    splash.destroy()
                except:
                    pass
                self.start_main_app()
                
            self.after(timeout, close_splash)
            
        except Exception as e:
            logging.error(f"Failed to display splash screen: {e}")
            self.start_main_app()
