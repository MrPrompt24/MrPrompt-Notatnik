<div align="center">

# MrPrompt Notatnik 📝

Nowoczesny, lekki notatnik dla Windows z polską pisownią, markerem, sejfami na notatki i asystentką AI Leną.
<br>
A modern, lightweight Windows notepad with Polish spell-checking, highlighter, note vaults and the AI assistant Lena.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg)

**[Polski](#-polski) | [English](#-english)**

</div>

---

## 🇵🇱 Polski

### Spis treści
- [O projekcie](#o-projekcie)
- [Funkcje](#funkcje)
- [Stack technologiczny](#stack-technologiczny)
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Uruchomienie](#uruchomienie)
- [Konfiguracja](#konfiguracja)
- [Użycie](#użycie)
- [Struktura projektu](#struktura-projektu)
- [Testy](#testy)
- [Współtworzenie](#współtworzenie)
- [Licencja](#licencja)
- [Kontakt](#kontakt)

### O projekcie
**MrPrompt Notatnik** to rozbudowana alternatywa dla systemowego Notatnika Windows, napisana w Pythonie (Tkinter). Jest dla osób, które dużo piszą po polsku i chcą szybko notować: z kontrolą pisowni, formatowaniem (RTF), zakreślaczem, szybkim zapisem do wybranych folderów („sejfów”) oraz opcjonalną pomocą AI. Działa lokalnie, bez konta i bez chmury — internet jest potrzebny wyłącznie dla Leny.

### Funkcje
- **Polska pisownia** — słownik Hunspell `pl_PL` (jak w LibreOffice), podkreślanie błędów na żywo (lub `F7`), podpowiedzi pod prawym przyciskiem myszy, „Ignoruj” i „Dodaj do słownika”.
- **Zakreślacz** — 5 kolorów (żółty, zielony, błękitny, różowy, pomarańczowy) i gumka.
- **Formatowanie** — pogrubienie `Ctrl+B`, kursywa `Ctrl+I`, podkreślenie `Ctrl+U`.
- **Listy** — punktowane (`Ctrl+L`) i zadań `- [ ]` / `- [x]` (`Ctrl+Shift+T`) z automatyczną kontynuacją po `Enter`.
- **Pliki RTF i TXT** — RTF zachowuje formatowanie (otwiera się w Wordzie i WordPadzie); rozpoznawanie kodowania UTF-8, UTF-8 BOM, Windows-1250, UTF-16; ostrzeżenie przed utratą zmian.
- **Sejfy** — zapis notatki jednym kliknięciem (lub `Ctrl+1…9`) do zdefiniowanych folderów, z nazwą proponowaną z pierwszej linijki; domyślnie `.md`.
- **Znajdź i zamień** — `Ctrl+F` / `Ctrl+H`, `F3` / `Shift+F3`, wielkość liter, całe słowa, „Zamień wszystkie” cofane jednym `Ctrl+Z`.
- **Aktywne linki** — URL-e i e-maile otwierane kliknięciem (opcjonalnie z `Ctrl`).
- **Kopia robocza** — autozapis niezapisanego dokumentu co 15 s i propozycja przywrócenia po awarii.
- **Narzędzia tekstowe** — sortowanie linii wg polskiego alfabetu, usuwanie duplikatów, zmiana wielkości liter.
- **Ostatnio otwarte**, przeciąganie plików `.rtf` / `.txt` / `.md` na okno, **tryb ciemny**, **zawsze na wierzchu**, pasek stanu (pozycja kursora, słowa, znaki, kodowanie).
- **Lena — asystentka AI** (opcjonalnie): poprawia, skraca, rozwija, zmienia ton, tłumaczy PL ⇄ EN, streszcza, wyciąga zadania i proponuje nazwę pliku. Zawsze pokazuje propozycję do akceptacji.

### Stack technologiczny
- **Python 3** + **Tkinter** (GUI)
- [`spylls`](https://pypi.org/project/spylls/) — silnik Hunspell w czystym Pythonie (sprawdzanie pisowni)
- [`Pillow`](https://pypi.org/project/pillow/) — ikony w menu
- [`tkinterdnd2`](https://pypi.org/project/tkinterdnd2/) — przeciąganie plików na okno
- Słownik `pl_PL` (LibreOffice), ikony **Font Awesome Free**
- Lena: API [Groq](https://console.groq.com/) (modele GPT-OSS 120B / 20B), wyłącznie biblioteka standardowa

### Wymagania
- Windows 10 / 11
- Python 3 (zalecany 3.13; `uruchom.bat` sam szuka zainstalowanego Pythona)
- Opcjonalnie: darmowy klucz API Groq dla Leny

### Instalacja
```bash
git clone https://github.com/MrPrompt24/MrPrompt-Notatnik.git
cd MrPrompt-Notatnik
pip install -r requirements.txt
```
Słownik polski jest w katalogu `slownik/`. Gdyby go zabrakło, pobierzesz go poleceniem `python setup_slownik.py`.

### Uruchomienie
- Dwuklik na **`uruchom.bat`** (doinstaluje brakujące biblioteki) lub **`uruchom_bez_okna.vbs`** (bez okna konsoli),
- albo z wiersza poleceń:
```bash
python main.py
python main.py notatka.txt   # otwarcie konkretnego pliku
```

### Konfiguracja
Wszystkie ustawienia zapisują się lokalnie w folderze programu i **nie są częścią repozytorium** (`.gitignore`):

| Plik | Zawartość |
|---|---|
| `ustawienia.json` | sejfy, motyw, ostatnio otwarte, model Leny |
| `slownik_uzytkownika.txt` | własne słowa dodane do słownika |
| `lena_klucz.txt` | Twój klucz API Groq (zwykły tekst) |
| `kopie_robocze/` | autozapis niezapisanej notatki |

**Lena:** w menu *Lena → Ustawienia Leny* wklej własny, darmowy klucz z <https://console.groq.com/keys>. Do Groq trafia tylko tekst, na którym wykonujesz akcję (maks. 4000 znaków). Bez klucza i bez internetu reszta notatnika działa normalnie. **Nie udostępniaj pliku `lena_klucz.txt`.**

### Użycie
- Pisz, formatuj i zakreślaj tekst; zapisuj jako `.rtf` (z formatowaniem) lub `.txt`.
- Dodaj sejfy w *Narzędzia → Zarządzaj sejfami*, potem zapisuj notatki klikając sejf lub `Ctrl+1…9`.
- Prawy przycisk myszy na podkreślonym słowie pokazuje sugestie pisowni.
- Zaznacz fragment i użyj menu *Lena*, aby go poprawić, skrócić lub przetłumaczyć.

### Struktura projektu
```
MrPrompt-Notatnik/
├── main.py              # aplikacja (GUI, edytor, RTF, sejfy, pisownia)
├── lena.py              # moduł Leny (klient API Groq)
├── setup_slownik.py     # pobieranie słownika pl_PL
├── uruchom.bat          # launcher (wykrywa Pythona, instaluje zależności)
├── uruchom_bez_okna.vbs # launcher bez konsoli
├── requirements.txt
├── assets/              # ikona aplikacji
├── fonts/               # Font Awesome Free
└── slownik/             # słownik Hunspell pl_PL
```

### Testy
Projekt nie zawiera na razie automatycznych testów.

### Współtworzenie
Zgłoszenia błędów i pomysły są mile widziane — otwórz *Issue* lub wyślij *Pull Request*. Prosimy, by nie dołączać plików z danymi osobistymi (`ustawienia.json`, `lena_klucz.txt`, notatki).

### Licencja
Ten projekt jest objęty licencją MIT — zobacz plik [LICENSE](LICENSE).
Ikony: Font Awesome Free (CC BY 4.0, czcionka SIL OFL 1.1). Słownik `pl_PL`: projekt LibreOffice/Hunspell, na własnych licencjach.

### Kontakt
Autor: **MrPrompt24** — MrPrompt Centrum Otwartych Innowacji, <https://mrprompt.eu/> • GitHub: [@MrPrompt24](https://github.com/MrPrompt24)

---

## 🇬🇧 English

### Table of Contents
- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Tests](#tests)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

### About
**MrPrompt Notatnik** is a feature-rich alternative to the built-in Windows Notepad, written in Python (Tkinter). It is aimed at people who write a lot in Polish and want to take notes fast: spell-checking, RTF formatting, a highlighter, one-click saving to chosen folders ("vaults") and optional AI help. It runs locally with no account and no cloud — internet access is needed only for Lena.

### Features
- **Polish spell-checking** — Hunspell `pl_PL` dictionary (as in LibreOffice), live underlining (or `F7`), right-click suggestions, "Ignore" and "Add to dictionary".
- **Highlighter** — 5 colours (yellow, green, blue, pink, orange) plus an eraser.
- **Formatting** — bold `Ctrl+B`, italic `Ctrl+I`, underline `Ctrl+U`.
- **Lists** — bullet (`Ctrl+L`) and task lists `- [ ]` / `- [x]` (`Ctrl+Shift+T`) that continue automatically on `Enter`.
- **RTF and TXT files** — RTF keeps formatting (opens in Word and WordPad); encoding detection for UTF-8, UTF-8 BOM, Windows-1250, UTF-16; unsaved-changes warning.
- **Vaults** — save a note with one click (or `Ctrl+1…9`) into predefined folders, with a file name suggested from the first line; `.md` by default.
- **Find & replace** — `Ctrl+F` / `Ctrl+H`, `F3` / `Shift+F3`, match case, whole words, "Replace all" undone with a single `Ctrl+Z`.
- **Clickable links** — URLs and e-mails open on click (optionally with `Ctrl`).
- **Crash recovery** — an unsaved document is auto-saved every 15 s and offered back after a crash.
- **Text tools** — sort lines by Polish alphabet, remove duplicates, change letter case.
- **Recent files**, drag-and-drop of `.rtf` / `.txt` / `.md` files, **dark mode**, **always on top**, status bar (cursor position, words, characters, encoding).
- **Lena — AI assistant** (optional): fixes, shortens, expands, changes tone, translates PL ⇄ EN, summarises, extracts tasks and suggests a file name. It always shows a proposal for you to accept.

### Tech Stack
- **Python 3** + **Tkinter** (GUI)
- [`spylls`](https://pypi.org/project/spylls/) — pure-Python Hunspell engine (spell-checking)
- [`Pillow`](https://pypi.org/project/pillow/) — menu icons
- [`tkinterdnd2`](https://pypi.org/project/tkinterdnd2/) — drag-and-drop
- `pl_PL` dictionary (LibreOffice), **Font Awesome Free** icons
- Lena: [Groq](https://console.groq.com/) API (GPT-OSS 120B / 20B), standard library only

### Requirements
- Windows 10 / 11
- Python 3 (3.13 recommended; `uruchom.bat` locates an installed Python automatically)
- Optional: a free Groq API key for Lena

### Installation
```bash
git clone https://github.com/MrPrompt24/MrPrompt-Notatnik.git
cd MrPrompt-Notatnik
pip install -r requirements.txt
```
The Polish dictionary ships in `slownik/`. If it is missing, download it with `python setup_slownik.py`.

### Running the App
- Double-click **`uruchom.bat`** (installs missing libraries) or **`uruchom_bez_okna.vbs`** (no console window),
- or from the command line:
```bash
python main.py
python main.py notatka.txt   # open a specific file
```

### Configuration
All settings are stored locally next to the program and are **not part of the repository** (`.gitignore`):

| File | Contents |
|---|---|
| `ustawienia.json` | vaults, theme, recent files, Lena model |
| `slownik_uzytkownika.txt` | custom words added to the dictionary |
| `lena_klucz.txt` | your Groq API key (plain text) |
| `kopie_robocze/` | auto-saved unsaved note |

**Lena:** open *Lena → Ustawienia Leny* and paste your own free key from <https://console.groq.com/keys>. Only the text you run an action on (max. 4000 characters) is sent to Groq. Without a key or internet connection the rest of the notepad works normally. **Never share `lena_klucz.txt`.**

### Usage
- Write, format and highlight text; save as `.rtf` (with formatting) or `.txt`.
- Add vaults in *Narzędzia → Zarządzaj sejfami*, then save notes by clicking a vault or pressing `Ctrl+1…9`.
- Right-click an underlined word to see spelling suggestions.
- Select a fragment and use the *Lena* menu to fix, shorten or translate it.

### Project Structure
```
MrPrompt-Notatnik/
├── main.py              # application (GUI, editor, RTF, vaults, spell-check)
├── lena.py              # Lena module (Groq API client)
├── setup_slownik.py     # downloads the pl_PL dictionary
├── uruchom.bat          # launcher (finds Python, installs dependencies)
├── uruchom_bez_okna.vbs # console-less launcher
├── requirements.txt
├── assets/              # application icon
├── fonts/               # Font Awesome Free
└── slownik/             # Hunspell pl_PL dictionary
```

### Tests
The project does not include automated tests yet.

### Contributing
Bug reports and ideas are welcome — open an *Issue* or send a *Pull Request*. Please do not include personal data files (`ustawienia.json`, `lena_klucz.txt`, your notes).

### License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
Icons: Font Awesome Free (CC BY 4.0, font under SIL OFL 1.1). `pl_PL` dictionary: LibreOffice/Hunspell project, under its own licences.

### Contact
Author: **MrPrompt24** — MrPrompt Centrum Otwartych Innowacji, <https://mrprompt.eu/> • GitHub: [@MrPrompt24](https://github.com/MrPrompt24)
