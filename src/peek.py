import tkinter as tk
from tkinter import ttk
import os
import threading
import time
import ctypes
import winreg
from ctypes import windll, byref, c_int, c_void_p, c_bool
from datetime import datetime

import uiautomation as auto
from PIL import Image, ImageTk
import win32gui
import win32ui
import win32con
import win32api
import pythoncom

# Windows Dark Mode Constants
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2

class IconExtractor:
    def __init__(self):
        self._icon_cache = {} # path -> ImageTk
        # Standard icon size
        self.large = False 

    def get_icon(self, path):
        ext = os.path.splitext(path)[1].lower()
        
        # Cache key: extension for files (except .lnk/.exe), full path for folders/.lnk/.exe
        if os.path.isdir(path):
            key = "FOLDER"
        elif ext in ['.lnk', '.exe', '.ico']:
            key = path
        else:
            key = ext

        if key in self._icon_cache:
            return self._icon_cache[key]
        
        icon = self._extract_shell_icon(path)
        if icon:
            self._icon_cache[key] = icon
            return icon
        return None

    def _extract_shell_icon(self, path):
        try:
            # SHGetFileInfo is the standard way to get shell icons
            # We use win32gui.ExtractIconEx for simplicity if available, or just shell
            
            # Use SHGetFileInfo to get the icon index and handle
            # Flags: SHGFI_ICON | SHGFI_SMALLICON (or LARGE) | SHGFI_USEFILEATTRIBUTES (if file doesn't exist yet, but here it does)
            
            # However, for Python simplicty without advanced struct mapping, we can try ExtractIconEx for exe/dll/ico
            # For general files, PyWin32's win32gui.ExtractIconEx is limited.
            
            # Better approach for Tkinter:
            # Use ExtractIconEx for .exe/.dll/.ico
            # For others, we might need a fallback or a more complex ctypes call.
            # Let's try the robust ctypes SHGetFileInfo approach which works for EVERYTHING (folders, lnk, files).
            
            # Codes:
            SHGFI_ICON = 0x000000100
            SHGFI_SMALLICON = 0x000000001
            SHGFI_LARGEICON = 0x000000000 # Actually 0
            SHGFI_TYPENAME = 0x000000400
            SHGFI_USEFILEATTRIBUTES = 0x000000010
            
            class SHFILEINFO(ctypes.Structure):
                _fields_ = [
                    ("hIcon", ctypes.c_void_p),
                    ("iIcon", ctypes.c_int),
                    ("dwAttributes", ctypes.c_uint),
                    ("szDisplayName", ctypes.c_char * 260),
                    ("szTypeName", ctypes.c_char * 80)
                ]
            
            shfileinfo = SHFILEINFO()
            
            # Determine flags
            flags = SHGFI_ICON | SHGFI_SMALLICON
            
            # Call SHGetFileInfo
            # We need to pass the absolute path
            path_bytes = path.encode('mbcs') # Windows standard encoding
            
            # Using ctypes directly for SHGetFileInfo
            shell32 = ctypes.windll.shell32
            res = shell32.SHGetFileInfoA(
                path_bytes,
                0,
                ctypes.byref(shfileinfo),
                ctypes.sizeof(shfileinfo),
                flags
            )
            
            if shfileinfo.hIcon:
                # Convert hIcon to PIL Image
                # We need to draw it to a DC and then capture it
                
                # 1. Create a Device Context
                hdc_screen = win32gui.GetDC(0)
                hdc = win32ui.CreateDCFromHandle(hdc_screen)
                
                # 2. Create a bitmap compatible with the screen
                bmp = win32ui.CreateBitmap()
                bmp.CreateCompatibleBitmap(hdc, 16, 16) # Small icon size
                
                # 3. Create a memory DC compatible with screen
                mem_dc = hdc.CreateCompatibleDC()
                mem_dc.SelectObject(bmp)
                
                # 4. Draw the icon into the memory DC
                # DrawIconEx(hdc, x, y, hIcon, cx, cy, stepIfAni, hbrFlickerFreeDraw, actions)
                win32gui.DrawIconEx(mem_dc.GetHandleOutput(), 0, 0, shfileinfo.hIcon, 16, 16, 0, 0, 3) 
                
                # 5. Convert to PIL
                bmpinfo = bmp.GetInfo()
                bmpstr = bmp.GetBitmapBits(True)
                
                img = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1)
                
                # Cleanup
                win32gui.DestroyIcon(shfileinfo.hIcon)
                win32gui.DeleteObject(bmp.GetHandle())
                mem_dc.DeleteDC()
                win32gui.ReleaseDC(0, hdc_screen)
                
                return ImageTk.PhotoImage(img)
                
        except Exception as e:
            # print(f"Icon Extract Error: {e}", flush=True)
            pass
        return None

class PeekWindow(tk.Toplevel):
    def __init__(self, parent, folder_path, x, y):
        super().__init__(parent)
        self.folder_path = folder_path
        self.overrideredirect(True) # Frameless
        self.attributes("-topmost", True)
        self.attributes("-toolwindow", True) # Hide from taskbar
        self.geometry(f"+{x}+{y}")
        
        self.icon_extractor = IconExtractor()
        self.icons = [] # Keep references!
        
        # Theme Detection
        self.is_dark = self._is_system_dark()
        self.colors = {
            "bg": "#202020" if self.is_dark else "#f9f9f9",
            "fg": "#ffffff" if self.is_dark else "#000000",
            "select_bg": "#444444" if self.is_dark else "#cce8ff",
            "header": "#2d2d2d" if self.is_dark else "#e1e1e1"
        }
        
        self.configure(bg=self.colors["bg"])
        
        # Apply Windows 11 Rounded Corners & Dark Attributes
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            # Immersive Dark Mode
            if self.is_dark:
                windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(c_int(1)), 4)
            # Rounded Corners
            windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, byref(c_int(DWMWCP_ROUND)), 4)
        except:
            pass
        
        # UI Structure
        self.frame = tk.Frame(self, bg=self.colors["bg"], highlightthickness=1, highlightbackground="#555" if self.is_dark else "#ccc")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(self.frame, bg=self.colors["header"])
        header_frame.pack(fill=tk.X)
        
        lbl_path = tk.Label(header_frame, text=os.path.basename(folder_path), 
                          font=("Segoe UI", 9, "bold"), 
                          bg=self.colors["header"], fg=self.colors["fg"],
                          anchor="w", padx=5)
        lbl_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        btn_open = tk.Button(header_frame, text="↗", font=("Segoe UI", 8),
                            bg=self.colors["header"], fg=self.colors["fg"],
                            borderwidth=0, activebackground=self.colors["select_bg"],
                            command=lambda: os.startfile(folder_path))
        btn_open.pack(side=tk.RIGHT, padx=2)
        
        # Treeview for Icons + Text
        # Define style
        style = ttk.Style()
        style_name = "Peek.Treeview"
        style.theme_use("clam") # 'clam' allows custom colors better than 'vista'
        
        style.configure(style_name, 
                       background=self.colors["bg"], 
                       foreground=self.colors["fg"], 
                       fieldbackground=self.colors["bg"],
                       font=("Segoe UI", 9),
                       rowheight=20,
                       borderwidth=0)
        style.map(style_name, background=[('selected', self.colors["select_bg"])])
        
        self.tree = ttk.Treeview(self.frame, show="tree", style=style_name, height=12)
        # Create a single column, but tree always has the '#0' main column for icon+text
        self.tree.column("#0", width=250, anchor='w')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.populate()
        
        # Bindings
        self.tree.bind("<Double-Button-1>", self.on_open)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Motion>", self.on_hover_item)
        self.bind("<Leave>", self.on_mouse_leave)
        
        self.sub_window = None

    def show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        
        self.tree.selection_set(item_id)
        
        menu = tk.Menu(self, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menu.add_command(label="Open", command=self.on_open)
        menu.add_command(label="Show in Folder", command=self.show_in_folder)
        menu.post(event.x_root, event.y_root)

    def show_in_folder(self):
        item_id = self.tree.focus()
        if not item_id: return
        
        item_text = self.tree.item(item_id, "text").strip()
        path = os.path.normpath(os.path.join(self.folder_path, item_text))
        
        # Open explorer and select the file
        subprocess_cmd = f'explorer /select,"{path}"'
        import subprocess
        subprocess.Popen(subprocess_cmd)
        self.destroy()

    def _is_system_dark(self):
        try:
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except:
            return False

    def populate(self):
        try:
            items = os.listdir(self.folder_path)
            # Sort: Folders first, then files
            folders = sorted([f for f in items if os.path.isdir(os.path.join(self.folder_path, f))])
            files = sorted([f for f in items if not os.path.isdir(os.path.join(self.folder_path, f))])
            
            # Helper to insert
            def add_item(fname, is_dir):
                full = os.path.join(self.folder_path, fname)
                icon = self.icon_extractor.get_icon(full)
                iid = self.tree.insert("", tk.END, text=f" {fname}", open=False)
                if icon:
                    self.icons.append(icon) # Valid reference
                    self.tree.item(iid, image=icon)
            
            for f in folders:
                add_item(f, True)
            for f in files:
                add_item(f, False)
                
        except Exception as e:
            self.tree.insert("", tk.END, text=f"<Error: {e}>")

    def on_open(self, event=None):
        item_id = self.tree.focus()
        if not item_id: return
        
        item_text = self.tree.item(item_id, "text").strip()
        path = os.path.join(self.folder_path, item_text)
        
        try:
            os.startfile(path)
            self.destroy()
        except Exception:
            pass

    def on_hover_item(self, event):
        pass

    def on_mouse_leave(self, event):
        # We need to be careful: query pointer pos
        x, y = self.winfo_pointerxy()
        wx, wy = self.winfo_rootx(), self.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        
        # Tolerate slight pixel border
        if not (wx <= x <= wx+w and wy <= y <= wy+h):
             self.destroy()

class PeekManager:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.thread = None
        self.current_window = None
        self.last_hovered_name = None
        self.last_debug_name = None
        self.hover_start_time = 0
        
    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.current_window:
            self.current_window.destroy()
        
    def _poll_loop(self):
        # Need COINIT for shell/icon operations potentially, but mostly for uiautomation
        with auto.UIAutomationInitializerInThread(debug=False):
            # Also initialize COM for this thread for shell
            pythoncom.CoInitialize()
            try:
                while self.running:
                    try:
                        # 1. Get Element under mouse
                        element = auto.ControlFromCursor()
                        if not element:
                            time.sleep(0.2)
                            continue
                        
                        # DIAGNOSTIC: Print whatever is under the mouse if it changes
                        current_debug_name = f"{element.Name} ({element.ClassName})"
                        if self.last_debug_name != current_debug_name:
                             # print(f"CURSOR OVER: Name='{element.Name}' Class='{element.ClassName}' Type='{element.ControlTypeName}'", flush=True)
                             self.last_debug_name = current_debug_name

                        # 2. Check if it's a ListItem on Desktop
                        is_desktop_list = False
                        parent = element.GetParentControl()
                        depth = 0
                        max_depth = 5
                        
                        # Check for ListItem or ListItemControl (depending on uiautomation version/locale)
                        is_list_item = "ListItem" in element.ControlTypeName
                        
                        # Debug ancestry for ListItems
                        if is_list_item:
                             temp_parent = parent
                             while temp_parent and depth < max_depth:
                                 if temp_parent.ClassName == "SysListView32":
                                     is_desktop_list = True
                                     break
                                 
                                 if not temp_parent.GetParentControl(): break
                                 temp_parent = temp_parent.GetParentControl()
                                 depth += 1

                        if is_list_item and is_desktop_list:
                            name = element.Name
                            
                            if name != self.last_hovered_name:
                                self.last_hovered_name = name
                                self.hover_start_time = time.time()
                            else:
                                if time.time() - self.hover_start_time > 0.5:
                                     # Try full path resolution - handle both Standard and OneDrive Desktops
                                     desktop_path = os.path.expanduser("~/Desktop")
                                     full_path = os.path.join(desktop_path, name)
                                     
                                     onedrive_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", name)
                                     
                                     target_path = None
                                     if os.path.isdir(full_path):
                                         target_path = full_path
                                     elif os.path.isdir(onedrive_path):
                                         target_path = onedrive_path
                                     
                                     if target_path:
                                         # print(f"DEBUG: Opening Peek for {name}", flush=True)
                                         if not self.current_window or not self.current_window.winfo_exists():
                                              self._show_peek(target_path)
                        else:
                            self.last_hovered_name = None
                            
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"Peek Loop Error: {e}", flush=True)
                        time.sleep(0.5)
            finally:
                pythoncom.CoUninitialize()

    def _show_peek(self, path):
        # Thread-safe GUI call
        self.root.after(0, lambda: self._create_window_safe(path))
        
    def _create_window_safe(self, path):
        if self.current_window and self.current_window.winfo_exists():
            if self.current_window.folder_path == path:
                return
            self.current_window.destroy()
            
        x, y = self.root.winfo_pointerxy()
        # Offset to not block mouse immediately
        self.current_window = PeekWindow(self.root, path, x + 10, y + 10)
