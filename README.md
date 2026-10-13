# MrPrompt Notatnik 📝

Nowoczesny, lekki notatnik dla systemu Windows stworzony w języku Python (Tkinter).

## 🚀 Główne funkcje

1. **Sprawdzanie polskiej pisowni**:
   - Słownik Hunspell `pl_PL` (ten sam co w LibreOffice) — rozpoznaje odmiany słów; ładuje się w tle przy starcie (ok. 4 s). Ignoruje skróty wielkimi literami, adresy URL, e-maile i wyrazy z cyframi.
   - Błędne słowa są automatycznie podkreślane na czerwono w trakcie pisania (lub po naciśnięciu `F7`).
   - **Kliknięcie prawym przyciskiem myszy** na podkreślonym słowie wyświetla listę sugerowanych poprawnych form oraz opcje *„Ignoruj to słowo”* i *„Dodaj do słownika”* (własne słowa zapisują się w `slownik_uzytkownika.txt`).

2. **Zakreślacz (marker tekstu)**:
   - Kolorowanie zaznaczonego tekstu jak prawdziwym markerem biurowym.
   - Dostępne kolory: **Żółty**, **Zielony**, **Błękitny**, **Różowy**, **Pomarańczowy**.
   - Przycisk gumki do szybkiego usuwania koloru zakreślenia.

3. **Formatowanie tekstu**:
   - **B** – Pogrubienie (`Ctrl+B`)
   - *I* – Kursywa (`Ctrl+I`)
   - <u>U</u> – Podkreślenie (`Ctrl+U`)

4. **Lista punktowa (wypunktowanie)**:
   - Przycisk `• Lista` lub skrót `Ctrl+L`.
   - Automatyczna kontynuacja punktów po naciśnięciu klawisza `Enter`.
   - Naciśnięcie `Enter` w pustym punkcie automatycznie kończy listę.

5. **Pliki RTF i TXT**:
   - **`.rtf`** – jeden plik z tekstem *i* formatowaniem (pogrubienie, kursywa, podkreślenie, marker, punkty). Otwiera się też w Wordzie i WordPadzie.
   - **`.txt`** – sam tekst bez formatowania (program ostrzega przy zapisie sformatowanego dokumentu).
   - Rozpoznawanie kodowania (**UTF-8**, UTF-8 z BOM, **Windows-1250**, UTF-16); plik zapisuje się w tym samym kodowaniu, które miał przy otwarciu (zmiana: Plik → Kodowanie).
   - Ostrzeżenie przed utratą niezapisanych zmian przy zamykaniu okna lub tworzeniu nowego pliku.

6. **Pasek stanu**:
   - Bieżąca pozycja kursora (`Ln X, Kol Y`).
   - Licznik słów i znaków na żywo.
   - Status sprawdzania pisowni i aktywne kodowanie.

7. **Sejfy (szybki zapis do folderów)**:
   - *Narzędzia → Zarządzaj sejfami* (lub przycisk „Sejfy…” na pasku): dodajesz foldery, np. sejfy z notatkami, nadajesz im nazwy i ustawiasz kolejność.
   - Kliknięcie sejfu na drugim pasku (albo `Ctrl+1…9`, albo *Plik → Zapisz w sejfie*) otwiera okno zapisu od razu w tym folderze, z nazwą zaproponowaną z pierwszej linijki notatki. Domyślne rozszerzenie to `.md`.
   - Lista sejfów jest w `ustawienia.json`.

8. **Aktywne linki**: adresy `http(s)://`, `www.` i e-maile są podświetlane i otwierają się kliknięciem (opcjonalnie tylko z `Ctrl`: *Narzędzia → Otwieraj linki tylko z klawiszem Ctrl*). Prawy przycisk: *Otwórz link* / *Kopiuj adres linku*.

9. **Znajdź i zamień**: `Ctrl+F` / `Ctrl+H` (`F3` / `Shift+F3` – następny/poprzedni). Podświetla wszystkie wyniki, opcje „Aa” (wielkość liter) i „Całe słowa”, „Zamień” i „Zamień wszystkie” (jedno `Ctrl+Z` cofa całość).

10. **Kopia robocza**: co 15 s niezapisany dokument (z formatowaniem) trafia do `kopie_robocze/`. Po awarii lub zabiciu procesu program proponuje przywrócenie przy następnym starcie. Normalne zamknięcie czyści kopię.

11. **Ostatnio otwarte** (*Plik → Ostatnio otwarte*) oraz **przeciąganie plików** `.rtf`/`.txt`/`.md` na okno programu.

12. **Tryb ciemny** i **Zawsze na wierzchu** (menu *Widok*, zapamiętywane).

13. **Narzędzia tekstowe** (*Narzędzia → Narzędzia tekstowe*): sortowanie linii wg polskiego alfabetu, usuwanie zduplikowanych linii, zmiana wielkości liter (zachowuje formatowanie). **Lista zadań** `- [ ]` / `- [x]` (`Ctrl+Shift+T`, `Enter` kontynuuje listę).

14. **Lena — asystentka AI** (menu *Lena*, ikona różdżki na pasku, prawy przycisk → *Lena*): działa na zaznaczonym fragmencie i pokazuje propozycję do akceptacji (można ją jeszcze poprawić przed wstawieniem; `Ctrl+Z` cofa).
   - **Popraw tekst** (pisownia, interpunkcja, styl), **Skróć**, **Rozwiń**, **Zmień ton** (formalnie / przyjaźnie / prościej), **Przetłumacz** PL ⇄ EN.
   - **Streść notatkę**, **Wyciągnij zadania** (lista `- [ ]`) — bez zaznaczenia działają na całej notatce.
   - **Zaproponuj nazwę pliku** — nazwa pojawia się potem w oknie zapisu (np. w sejfie).
   - Działa na darmowym API [Groq](https://console.groq.com/keys), domyślny model **GPT-OSS 120B** (do wyboru także 20B). Każdy użytkownik generuje własny, darmowy klucz; program prowadzi przez to krok po kroku (*Lena → Ustawienia Leny*, jest tam link do strony z kluczami).
   - Klucz jest zapisany lokalnie w pliku `lena_klucz.txt` w folderze programu (zwykły tekst — **nie udostępniaj tego folderu / pliku**, nie kopiuj go do repozytorium).
   - **Limity i oszczędność:** darmowe konto Groq ma limity zapytań i tokenów na minutę oraz na dobę. Lena wysyła dane tylko po kliknięciu, tylko zaznaczony fragment (maks. 4000 znaków) i prosi model o krótkie „myślenie”. Gdy limit się wyczerpie, pokazuje zrozumiały komunikat, ile trzeba poczekać.
   - **Prywatność:** do Groq trafia wyłącznie tekst, na którym wykonujesz akcję Leny. Bez klucza i bez internetu reszta notatnika działa normalnie.

---

## 🎨 Ikony
Menu i pasek narzędzi używają ikon **Font Awesome Free** (`fonts/fa-solid-900.ttf`, ikony CC BY 4.0, czcionka SIL OFL 1.1). Ikony w menu rozwijanym wymagają biblioteki Pillow.

## 💻 Jak uruchomić?

Najpierw (jednorazowo): `pip install -r requirements.txt`


Wystarczy kliknąć dwukrotnie na plik:
👉 **`uruchom.bat`**

Lub z poziomu wiersza poleceń / PowerShell:
```bash
python main.py
```
Można również otworzyć konkretny plik tekstowy:
```bash
python main.py notatka.txt
```
