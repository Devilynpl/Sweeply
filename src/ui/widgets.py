import tkinter as tk
import random
from .styles import HUD_BG, HUD_PANEL, HUD_CYAN, HUD_TEXT, HUD_MUTED, HUD_BORDER, DARK

class GlowButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=140, height=45, color=HUD_CYAN, **kwargs):
        # Safely resolve parent background color
        try:
            parent_bg = parent["bg"]
        except Exception:
            parent_bg = HUD_BG
        super().__init__(parent, width=width, height=height, bg=parent_bg,
                         highlightthickness=0, cursor="hand2", **kwargs)
        self.text = text
        self.command = command
        self.color = color
        self.width = width
        self.height = height
        self.state = tk.NORMAL
        self.hovered = False

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        self._draw()

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius=5, **kwargs):
        points = [x1+radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _draw(self):
        self.delete("all")
        w, h = self.width, self.height

        # Windows 11 native button colors
        if self.state == tk.DISABLED:
            bg_color     = HUD_PANEL
            border_color = HUD_BORDER
            text_color   = HUD_MUTED
        elif self.hovered:
            bg_color     = self.color
            border_color = self.color
            text_color   = "#FFFFFF"
        else:
            bg_color     = HUD_PANEL
            border_color = HUD_BORDER
            text_color   = HUD_TEXT

        # Draw rounded rectangle container
        self._draw_rounded_rect(2, 2, w-2, h-2, radius=5, fill=bg_color, outline=border_color, width=1)
        
        # Draw text in Fluent style
        self.create_text(w/2, h/2, text=self.text, fill=text_color, 
                         font=("Segoe UI Semibold", 9), justify=tk.CENTER)

    def _on_enter(self, e):
        if self.state == tk.NORMAL:
            self.hovered = True
            self._draw()

    def _on_leave(self, e):
        if self.state == tk.NORMAL:
            self.hovered = False
            self._draw()

    def _on_click(self, e):
        if self.state == tk.NORMAL and self.command:
            self.command()

    def configure(self, cnf=None, **kw):
        if cnf:
            kw.update(cnf)
        if "state" in kw:
            new_state = kw["state"]
            if new_state != self.state:
                self.state = new_state
                self._draw()
        valid_kw = {k: v for k, v in kw.items() if k not in ["state", "alpha"]}
        return super().configure(valid_kw)

    def config(self, cnf=None, **kw):
        return self.configure(cnf, **kw)

class PieChart(tk.Canvas):
    def __init__(self, parent, width=200, height=200, bg=HUD_PANEL, **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, 
                         highlightthickness=0, **kwargs)
        self.bg_color = bg
        self.data = {} # category -> size
        # Windows 11 Soft Accent Palette
        self.colors = ["#0078D4", "#107C41", "#D83B01", "#5C2D91", "#008272", "#A80000", "#4A6572"]

    def set_data(self, data):
        self.data = data
        self._draw()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1:
            w = int(self.cget("width"))
        if h <= 1:
            h = int(self.cget("height"))

        if not self.data or sum(self.data.values()) == 0:
            # Draw a clean empty state donut placeholder
            side = min(w, h)
            x_offset = (w - side) / 2
            y_offset = (h - side) / 2
            margin = 15
            
            # Outer donut circle
            self.create_oval(x_offset + margin, y_offset + margin,
                             x_offset + side - margin, y_offset + side - margin,
                             fill=self.bg_color, outline=HUD_BORDER, width=2)
            
            # Inner hole
            hole_margin = side * 0.30
            self.create_oval(x_offset + hole_margin, y_offset + hole_margin,
                             x_offset + side - hole_margin, y_offset + side - hole_margin,
                             fill=self.bg_color, outline=HUD_BORDER, width=1)
            
            # Center text
            self.create_text(w/2, h/2 - 7, text="BRAK DANYCH", fill=HUD_MUTED, font=("Segoe UI Semibold", 7))
            self.create_text(w/2, h/2 + 7, text="0 B", fill=HUD_CYAN, font=("Segoe UI Semibold", 9, "bold"))
            return

        total = sum(self.data.values())
        side = min(w, h)
        x_offset = (w - side) / 2
        y_offset = (h - side) / 2
        margin = 15
        
        # Calculate bounding box for perfect circle
        x1 = x_offset + margin
        y1 = y_offset + margin
        x2 = x_offset + side - margin
        y2 = y_offset + side - margin
        
        start_angle = 0
        i = 0
        for cat, size in sorted(self.data.items(), key=lambda x: x[1], reverse=True):
            extent = (size / total) * 358
            color = self.colors[i % len(self.colors)]
            
            # Draw arc with soft outline
            self.create_arc(x1, y1, x2, y2, 
                            start=start_angle, extent=extent, 
                            fill=color, outline=self.bg_color, width=1)
            
            start_angle += extent
            i += 1
        
        # Center hole (Donut chart feel)
        hole_margin = side * 0.30
        hx1 = x_offset + hole_margin
        hy1 = y_offset + hole_margin
        hx2 = x_offset + side - hole_margin
        hy2 = y_offset + side - hole_margin
        
        self.create_oval(hx1, hy1, hx2, hy2, fill=self.bg_color, outline=HUD_BORDER, width=1)
        
        # Format total size beautifully
        if total >= 1024 * 1024 * 1024:
            size_str = f"{total / (1024**3):.1f} GB"
        elif total >= 1024 * 1024:
            size_str = f"{total / (1024**2):.1f} MB"
        elif total >= 1024:
            size_str = f"{total / 1024:.1f} KB"
        else:
            size_str = f"{total} B"
            
        # Draw nice text labels in the center of the donut chart
        self.create_text(w/2, h/2 - 7, text="RAZEM", fill=HUD_MUTED, font=("Segoe UI Semibold", 7))
        self.create_text(w/2, h/2 + 7, text=size_str, fill=HUD_CYAN, font=("Segoe UI Semibold", 9, "bold"))
