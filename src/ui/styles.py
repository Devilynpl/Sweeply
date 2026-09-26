import platform

def get_windows_accent_color():
    if platform.system() != "Windows":
        return "#0078D4"
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM")
        value, _ = winreg.QueryValueEx(key, "AccentColor")
        r = value & 0xff
        g = (value >> 8) & 0xff
        b = (value >> 16) & 0xff
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return "#0078D4"

def is_dark_mode():
    if platform.system() != "Windows":
        return False
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0  # 0 = Dark mode
    except Exception:
        return False

import sys

# ── Detect system theme ────────────────────────────────────────────
DARK = is_dark_mode()
ACCENT = get_windows_accent_color()
NO_SKIN = "--no-skin" in sys.argv

if NO_SKIN:
    # Native Windows system colors
    HUD_BG     = "SystemButtonFace"
    HUD_PANEL  = "SystemButtonFace"
    HUD_CYAN   = "SystemHighlight"
    HUD_RED    = "#C42B1C"
    HUD_TEXT   = "SystemWindowText"
    HUD_MUTED  = "SystemGrayText"
    HUD_BORDER = "SystemButtonFace"
else:
    if DARK:
        # Windows 11 Dark palette
        HUD_BG     = "#202020"   # Main window background
        HUD_PANEL  = "#2D2D2D"   # Card / surface background
        HUD_CYAN   = ACCENT      # System accent (blue by default)
        HUD_RED    = "#FF4343"   # Error / danger
        HUD_TEXT   = "#F3F3F3"   # Primary text (near-white)
        HUD_MUTED  = "#9D9D9D"   # Secondary / muted text
        HUD_BORDER = "#3D3D3D"   # Subtle border
    else:
        # Windows 11 Light palette
        HUD_BG     = "#F3F3F3"   # Light gray Mica-like background
        HUD_PANEL  = "#FFFFFF"   # White cards
        HUD_CYAN   = ACCENT      # System accent
        HUD_RED    = "#C42B1C"   # Error / danger
        HUD_TEXT   = "#1A1A1A"   # Near-black primary text
        HUD_MUTED  = "#5F5F5F"   # Medium gray secondary text
        HUD_BORDER = "#E5E5E5"   # Subtle border

def setup_hud_styles(style):
    if NO_SKIN:
        if platform.system() == "Windows":
            try:
                style.theme_use('vista')
            except Exception:
                style.theme_use('default')
        else:
            style.theme_use('default')
        return

    style.configure(".",           background=HUD_BG,    foreground=HUD_TEXT, fieldbackground=HUD_BG)
    style.configure("TFrame",      background=HUD_BG)
    style.configure("HUD.TFrame",  background=HUD_PANEL)

    # Labels
    style.configure("TLabel",        background=HUD_BG,    foreground=HUD_TEXT,  font=("Segoe UI", 10))
    style.configure("Header.TLabel", font=("Segoe UI Semibold", 18), foreground=HUD_CYAN)
    style.configure("Path.TLabel",   font=("Segoe UI", 9),           foreground=HUD_MUTED)

    # LabelFrame
    style.configure("TLabelframe",       background=HUD_BG, bordercolor=HUD_BORDER, borderwidth=1)
    style.configure("TLabelframe.Label", background=HUD_BG, foreground=HUD_TEXT, font=("Segoe UI Semibold", 9))

    # Checkbuttons
    style.configure("TCheckbutton", background=HUD_BG, foreground=HUD_TEXT, font=("Segoe UI", 9))
    style.map("TCheckbutton",
              background=[("active", HUD_BG)],
              foreground=[("active", HUD_CYAN)])

    # Notebook
    style.configure("TNotebook",     background=HUD_BG,    borderwidth=0)
    style.configure("TNotebook.Tab", background=HUD_PANEL, foreground=HUD_MUTED, padding=[15, 5])
    style.map("TNotebook.Tab",
              background=[("selected", HUD_PANEL)],
              foreground=[("selected", HUD_CYAN)])

    # Treeview
    style.configure("Treeview",
                    background=HUD_PANEL, foreground=HUD_TEXT,
                    fieldbackground=HUD_PANEL, rowheight=25, borderwidth=0)
    style.map("Treeview",
              background=[("selected", HUD_CYAN)],
              foreground=[("selected", "#FFFFFF")])
    style.configure("Treeview.Heading",
                    background=HUD_PANEL, foreground=HUD_TEXT,
                    font=("Segoe UI Semibold", 9))

    # Buttons
    style.configure("TButton",
                    background=HUD_PANEL, foreground=HUD_TEXT,
                    font=("Segoe UI Semibold", 9), borderwidth=1, relief="flat")
    style.map("TButton",
              background=[("active", HUD_BORDER), ("pressed", HUD_CYAN)],
              foreground=[("pressed", "#FFFFFF")])


