# Sweeply Desktop Cleaner

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?logo=windows)](https://microsoft.com)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![Repository](https://img.shields.io/badge/GitHub-Devilynpl%2FSweeply-181717?logo=github)](https://github.com/Devilynpl/Sweeply)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[🇵🇱 Wersja Polska](#polska-wersja) | [🇬🇧 English Version](#english-version)

---

<a name="polska-wersja"></a>
## 🇵🇱 Polska Wersja

**Sweeply Desktop Cleaner** to zaawansowane narzędzie dla systemu Windows (10/11) stworzone do automatycznego porządkowania pulpitu, ochrony układu ikon użytkownika oraz monitorowania przestrzeni roboczej. Aplikacja łączy nowoczesny interfejs Heads-Up Display (HUD), niskopoziomową integrację z API Windows (Win32), transakcyjny system cofania operacji oraz inteligentną kategoryzację plików.

### Główne Funkcjonalności

- **Inteligentna Automatyczna Kategoryzacja**:
  - Przenosi pliki i foldery do dedykowanych podkatalogów (Dokumenty, Obrazy, Wideo, Muzyka, Archiwa, Kod, Programy itp.) na podstawie rozszerzeń zdefiniowanych w `src/categories.json`.
  - Opcjonalne sortowanie czasowe: możliwość automatycznego grupowania w datowanych folderach (`YYYY-MM-DD`).
  - Szybkie skanowanie systemu plików oparte o `os.scandir`.

- **Transakcyjny System Cofania (Undo)**:
  - Moduł `UndoManager` rejestruje każdą operację przeniesienia na stosie historii.
  - Umożliwia bezpieczne i bezstratne przywrócenie plików do ich oryginalnych lokalizacji.

- **Zapisywanie i Przywracanie Pozycji Ikon Pulpitu (Win32)**:
  - Bezpośrednia komunikacja z powłoką Windows (`Progman` / `WorkerW` -> `SHELLDLL_DefView` -> `SysListView32`).
  - Pamięta i przywraca dokładne współrzędne `(X, Y)` ikon na pulpicie, zapobiegając zaburzeniu indywidualnego układu użytkownika.

- **Interaktywny Podgląd Folderów "Peek"**:
  - Płynny podgląd zawartości folderów w stylu Windows 11 (zaokrąglone narożniki, cień systemowy).
  - Pobieranie natywnych ikon systemowych oraz możliwość bezpośredniego otwierania plików z poziomu okna podglądu.

- **Monitorowanie Pojemności i Zagęszczenia Siatki Pulpitu**:
  - Dynamiczne obliczanie optymalnej liczby ikon na podstawie rozdzielczości ekranu wirtualnego (`SM_CXVIRTUALSCREEN`, `SM_CYVIRTUALSCREEN`).
  - Wskaźnik HUD informuje o przeładowaniu pulpitu.

- **Dwa Tryby Interfejsu Użytkownika**:
  - **Tryb HUD**: Futurologiczny design high-tech/cyberpunk z animacjami, podświetlanymi przyciskami (`GlowButton`) i wykresem kołowym typów plików.
  - **Tryb Standardowy (`--no-skin`)**: Natywny, lekki interfejs Windows dla zachowania minimalnego obciążenia zasobów.

- **Praca w Tle i Zasobnik Systemowy (Tray)**:
  - Działanie w tle w obszarze powiadomień Windows za pośrednictwem biblioteki `pystray`.
  - Obsługa harmonogramu i cyklicznego porządkowania.

### Struktura Projektu

```text
desktop_cleaner/
├── main.py                     # Punkt startowy aplikacji i parser CLI
├── requirements.txt            # Zależności bibliotek Pythona
├── build_exe.py                # Skrypt kompilacji do pojedynczego pliku EXE (PyInstaller)
├── build_installers.py         # Skrypt budowania instalatorów Inno Setup (x86/x64)
├── sweeply_icon.ico            # Wielorozdzielczościowa ikona aplikacji
├── src/
│   ├── core.py                 # Silnik czyszczący, UndoManager, obsługa konfiguracji
│   ├── gui.py                  # Główny interfejs HUD, zdarzenia, obsługa zasobnika
│   ├── icon_layout.py          # Odczyt i zapis współrzędnych ikon (Win32 API)
│   ├── peek.py                 # Moduł podglądu folderów z ikonami powłoki
│   ├── utils.py                # Narzędzia pomocnicze i mapowanie kategorii
│   ├── categories.json         # Baza rozszerzeń przypisanych do kategorii
│   └── ui/
│       ├── category_editor.py  # Graficzny edytor reguł i rozszerzeń
│       ├── styles.py           # Paleta kolorów, fonty i definicje motywu
│       └── widgets.py          # Niestandardowe kontrolki HUD (GlowButton itp.)
└── tests/
    ├── test_core.py            # Testy jednostkowe logiki skanowania i cofania
    ├── test_gui.py             # Testy komponentów interfejsu graficznego
    └── debug_undo.py           # Skrypt diagnostyczny transakcji cofania
```

### Wymagania i Instalacja

- **System operacyjny**: Windows 10 lub Windows 11 (32-bit lub 64-bit)
- **Python**: 3.8 lub nowszy

```powershell
# Sklonuj repozytorium
git clone https://github.com/Devilynpl/Sweeply.git
cd desktop_cleaner

# Utwórz i aktywuj środowisko wirtualne
python -m venv .venv
.venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt
```

### Uruchomienie

```powershell
# Uruchomienie w domyślnym trybie HUD
python main.py

# Uruchomienie w standardowym trybie okna Windows
python main.py --no-skin
```

### Konfiguracja

Plik konfiguracyjny użytkownika zapisywany jest w `~/.sweeply_cfg.json`:
- `clean_folder_path`: Ścieżka docelowa dla uporządkowanych plików (domyślnie `Pulpit\Sweeply`).
- `dated_folders`: Tworzenie folderów z datą (`YYYY-MM-DD`).
- `skip_folders`: Pomijanie folderów znajdujących się na pulpicie.
- `ignored_items`: Lista wykluczonych nazw plików i katalogów.

Baza kategorii może być modyfikowana w interfejsie graficznym lub bezpośrednio w pliku `src/categories.json`.

### Budowanie Plików Wykonywalnych i Instalatorów

1. **Pojedynczy plik wykonywalny (.exe)**:
   ```powershell
   python build_exe.py
   ```
   Wynikowy plik pojawi się w katalogu `dist/DesktopCleanerHUD.exe`.

2. **Pakiety Instalacyjne Windows (Inno Setup x86 & x64)**:
   Wymagany zainstalowany [Inno Setup 6](https://jrsoftware.org/isdl.php).
   ```powershell
   python build_installers.py
   ```
   Skrypt automatycznie wygeneruje ikony, skompiluje wersje 32- oraz 64-bitowe, utworzy pliki `.iss` i zbuduje gotowe instalatory w katalogu `releases/`.

### Testy

Uruchomienie zestawu testów jednostkowych za pomocą frameworka `pytest`:
```powershell
pytest -v tests/
```

### Licencja

Projekt jest udostępniany na zasadach wolnej licencji [MIT](LICENSE). Szczegółowe postanowienia znajdują się w pliku `LICENSE`.

---

<a name="english-version"></a>
## 🇬🇧 English Version

**Sweeply Desktop Cleaner** is an advanced desktop organization utility for Windows (10/11) designed to automate desktop decluttering, preserve user icon layouts, and provide real-time workspace analytics. Combining a futuristic Heads-Up Display (HUD) interface, low-level Win32 shell integration, transactional undo operations, and flexible categorization, Sweeply delivers high-performance workspace hygiene in a single click.

### Key Features

- **Intelligent Automated Categorization**:
  - Automatically sorts desktop items into dedicated categories (Documents, Media, Code, Archives, Executables, etc.) driven by `src/categories.json`.
  - Optional temporal grouping (`YYYY-MM-DD` dated subfolders) for chronological archiving.
  - High-performance scanning powered by Python's `os.scandir`.

- **Transactional Multi-Level Undo Engine**:
  - Implements a stack-based `UndoManager` recording all file transfer operations.
  - Safely reverses moves back to exact original desktop locations without data loss.

- **Win32 Desktop Icon Position Persistence**:
  - Directly interfaces with the Windows Shell hierarchy (`Progman` / `WorkerW` -> `SHELLDLL_DefView` -> `SysListView32`).
  - Records and restores exact coordinate positions `(X, Y)` of desktop icons.

- **Interactive Folder "Peek" with Native Windows Shell Icons**:
  - Fluid Windows 11-style folder hover preview cards.
  - Renders native high-resolution system icons via Windows Shell APIs with direct file launch support.

- **Hardware-Aware Grid Density & Clutter Monitoring**:
  - Queries virtual desktop dimensions (`SM_CXVIRTUALSCREEN`, `SM_CYVIRTUALSCREEN`) to compute physical icon capacity.
  - Real-time HUD gauge alerts when icon density exceeds optimal ergonomics.

- **Dual User Interface Modes**:
  - **HUD Mode**: Cyberpunk/high-tech dark aesthetic with animations, glowing canvas widgets (`GlowButton`), and file distribution pie charts.
  - **Standard UI Mode (`--no-skin`)**: Lightweight native Windows appearance for minimal footprint.

- **Background Daemon & System Tray**:
  - Runs unobtrusively in the Windows Notification Area via `pystray`.
  - Supports automated scheduling routines for hands-free maintenance.

### Project Structure

```text
desktop_cleaner/
├── main.py                     # Application entry point & CLI parser
├── requirements.txt            # Python dependencies
├── build_exe.py                # Standalone single-binary PyInstaller builder
├── build_installers.py         # Multi-target (x86/x64) Inno Setup builder
├── sweeply_icon.ico            # Application multi-resolution icon
├── src/
│   ├── core.py                 # Core cleaning engine, UndoManager, configuration
│   ├── gui.py                  # Main HUD interface, event bindings & tray lifecycle
│   ├── icon_layout.py          # Win32 SysListView32 icon position serializer
│   ├── peek.py                 # Windows 11 styled shell preview system
│   ├── utils.py                # Category mapping helpers & system paths
│   ├── categories.json         # Extension-to-category definitions
│   └── ui/
│       ├── category_editor.py  # Interactive category rule manager
│       ├── styles.py           # Color palettes, typography & theme definitions
│       └── widgets.py          # Custom HUD controls (GlowButton, Canvas widgets)
└── tests/
    ├── test_core.py            # Unit tests for scanner, mover, and undo
    ├── test_gui.py             # GUI component and lifecycle verification
    └── debug_undo.py           # Diagnostic script for transaction verification
```

### Prerequisites & Installation

- **Operating System**: Windows 10 or Windows 11 (x64 / x86)
- **Python**: 3.8 or higher

```powershell
# Clone the repository
git clone https://github.com/Devilynpl/Sweeply.git
cd desktop_cleaner

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### Usage

```powershell
# Launch with default HUD Interface
python main.py

# Launch with Standard Windows UI (no skin)
python main.py --no-skin
```

### Configuration

Stored locally in `~/.sweeply_cfg.json`:
- `clean_folder_path`: Target destination for sorted files (default: `Desktop\Sweeply`).
- `dated_folders`: When `true`, creates timestamped subfolders (`YYYY-MM-DD`).
- `skip_folders`: When `true`, ignores directories present on the desktop.
- `ignored_items`: Whitelist of file/folder names excluded from cleaning.

Category rules and associations can be edited via the in-app Category Editor or directly within `src/categories.json`.

### Building Executables & Installers

1. **Standalone Executable (.exe)**:
   ```powershell
   python build_exe.py
   ```
   Output binary is generated at `dist/DesktopCleanerHUD.exe`.

2. **Windows Setup Installers (Inno Setup x86 & x64)**:
   Requires [Inno Setup 6](https://jrsoftware.org/isdl.php).
   ```powershell
   python build_installers.py
   ```
   Automates icon generation, dual-architecture PyInstaller compilation, `.iss` script creation, and outputs installers to `releases/`.

### Testing

Run the test suite using `pytest`:
```powershell
pytest -v tests/
```

### License

This project is licensed under the terms of the [MIT License](LICENSE). See the `LICENSE` file for details.
