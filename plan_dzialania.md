# Plan Działania: Desktop Cleaner Modernization & Optimization

Plik ten przedstawia harmonogram i zakres prac mających na celu dopracowanie wyglądu Windows 11, natywnej integracji systemowej, pełnego pokrycia testowego oraz optymalizacji pamięci (memory leaks) i wydajności aplikacji.

---

## Faza 1: Dalszy Szlif Wizualny (UI & UX Windows 11)

### Krok 1.1: Standaryzacja Kontrolek i Formularzy
* **Czynność 1.1.1**: Wyrównanie marginesów i paddingów w głównym oknie oraz panelu ustawień do siatki Fluent Design (np. równe odstępy 8px/16px/24px).
* **Czynność 1.1.2**: Zastąpienie domyślnych pasków przewijania (Scrollbar) niestandardowymi, wąskimi scrollbarami Tkinter pasującymi do nowoczesnego stylu.
* **Czynność 1.1.3**: Usprawnienie wyglądu listy plików w głównym oknie (Treeview) – dodanie zaokrąglonych krawędzi, subtelnego podświetlenia wiersza oraz zwiększenie wysokości wierszy (`rowheight`).

### Krok 1.2: Animacje i Efekty Przejść
* **Czynność 1.2.1**: Dodanie płynnej zmiany koloru (fade transition) przy najechaniu myszą na przyciski `GlowButton`.
* **Czynność 1.2.2**: Wprowadzenie animacji ładowania/postępu (Spinner lub płynący pasek) w trakcie skanowania pulpitu.

---

## Faza 2: Natywna Integracja z API Windows 11

### Krok 2.1: Udoskonalenie Funkcji Peek (Podgląd Folderów)
* **Czynność 2.1.1**: Wykorzystanie natywnych bibliotek systemowych (np. `ctypes`, `pywin32` jeśli dostępne) do pobierania oficjalnych ikon plików/folderów z powłoki Windows Shell.
* **Czynność 2.1.2**: Zapewnienie asynchronicznego ładowania podglądu (w osobnym wątku), aby interfejs graficzny Tkinter nie zacinał się przy dużych folderach.
* **Czynność 2.1.3**: Dodanie zaokrąglonych rogów okna podglądu Peek przy użyciu atrybutów kompozycji okien systemu Windows 11 (DWM - Desktop Window Manager API).

### Krok 2.2: Obsługa Powiadomień i Paska Zadań
* **Czynność 2.2.1**: Zastąpienie niestandardowych okienek ostrzegawczych (toasts) natywnymi powiadomieniami systemu Windows.
* **Czynność 2.2.2**: Poprawienie integracji z zasobnikiem systemowym (Tray) – płynne przełączanie między minimalizacją a pełnym widokiem, unikanie podwójnych ikon przy restartach aplikacji.

---

## Faza 3: Testy Kodu i Pokrycie (Testing & Code Quality)

### Krok 3.1: Testy Jednostkowe Logiki GUI
* **Czynność 3.1.1**: Dodanie testów sprawdzających filtrowanie listy plików na żywo podczas wpisywania znaków w polu wyszukiwania (`var_search`).
* **Czynność 3.1.2**: Napisanie testów weryfikujących zachowanie przycisków `GlowButton` przy zmianie stanu (`DISABLED` / `NORMAL`).
* **Czynność 3.1.3**: Implementacja testów dla Edytora Kategorii – sprawdzanie dodawania nowej kategorii, przypisywania rozszerzeń i poprawnego zapisu konfiguracji JSON.

### Krok 3.2: Testy Integracyjne i Scenariusze E2E
* **Czynność 3.2.1**: Stworzenie mocków dla operacji na plikach o wysokim wolumenie (np. symulacja skanowania pulpitu z 5000+ plikami).
* **Czynność 3.2.2**: Scenariusz cofnięcia (Undo) – upewnienie się, że operacja cofnięcia poprawnie przywraca strukturę folderów i atrybuty plików.

---

## Faza 4: Wykrywanie Wycieków Pamięci i Optymalizacja Wydajności

### Krok 4.1: Audyt Pamięci (Memory Leaks Audit)
* **Czynność 4.1.1**: Zaimplementowanie profilowania pamięci za pomocą modułu `tracemalloc` podczas operacji cyklicznych (check_schedule, check_capacity_loop).
* **Czynność 4.1.2**: Zweryfikowanie zwalniania pamięci przez moduł `pystray` (Tray Icon) oraz bibliotekę `PIL` (ładowanie i transformacje logo/obrazów).
* **Czynność 4.1.3**: Zapobieganie wyciekom w Tkinter – upewnienie się, że dynamicznie usuwane kontrolki (np. w `update_category_checkboxes`) są w pełni niszczone za pomocą `.destroy()`, a powiązane zmienne i bindingi są czyszczone.

### Krok 4.2: Optymalizacja Wydajnościowa
* **Czynność 4.2.1**: Zoptymalizowanie metody `filter_console` w celu zapobiegania zbędnemu odświeżaniu interfejsu (deboucing wpisywanych znaków filtra).
* **Czynność 4.2.2**: Zaimplementowanie buforowania wczytywanych ikon plików, by uniknąć ciągłego odczytu z dysku w trakcie przewijania listy.
