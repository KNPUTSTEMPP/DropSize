# KNPUTSTEMDetector
KNPUTSTEMDetector jest narzędziem umożliwiającym automatyczną detekcję oraz analizę pęcherzyków emulsji na obrazach uzyskanych spod mikroskopu.


# Instrukcja użytkowania

## Instalacja

Aby zainstalować program:
1. Przejdź do zakładki **Releases** w tym repozytorium.
2. Pobierz najnowszą wersję pliku wykonywalnego '.exe'.
3. Uruchom plik - instalacja nie jest wymagana.

Uwaga: Program został zbudowany przy użyciu PyInstaller. Niektóre programy antywirusowe mogą wyświetlać ostrzeżenie.

---

## Opis funkcji i przycisków

### Wczytywanie i skala obrazu

- **Wybierz obraz**  
  Pozwala na wybór obrazu, na którym będzie wykonywana detekcja pęcherzyków.

- **Skala obrazu [µm/piksel]**  
  Pole umożliwiające ręczne podanie skali obrazu.

- **Wpisz skalę**  
  Zapisuje wprowadzoną wartość skali do pamięci programu.

- **Ustal skalę**  
  Umożliwia ręczne wyznaczenie skali poprzez zaznaczenie dwóch punktów na obrazie, a następnie podanie rzeczywistej odległości pomiędzy nimi (w µm).  
  Zalecane w przypadku obrazów o niestandardowej rozdzielczości.

- **Powiększenie obrazu (lista rozwijalna)**  
  Wybór skali na podstawie powiększenia, w jakim wykonano zdjęcie.

---

### Detekcja i edycja pęcherzyków

- **Uruchom detekcję**  
  Oznacza wykryte pęcherzyki na obrazie oraz zapisuje dane pomiarowe do pliku `.csv`.

- **Dodaj bąbelek**  
  Funkcja umożliwiająca ręczne dodanie oznaczenia pęcherzyka poprzez:
  1. Kliknięcie w środek pęcherzyka
  2. Kliknięcie na jego krawędź (wyznaczenie promienia)

---

### Analiza wyników

- **Histogram ilościowy / częstościowy**  
  Wyświetla histogram ilościowy lub częstościowy średnic pęcherzyków.

- **Średnica Sautera**  
  Oblicza średnicę Sautera dla analizowanych pęcherzyków.

---

## Zapisywanie wyników

Po uruchomieniu detekcji, w katalogu, z którego został uruchomiony program, tworzony jest folder: **outputs**

W folderze tym zapisywane są pliki wynikowe w formacie `.csv`.

### Nazewnictwo plików

- Pierwszy pomiar:
test_bubble_wynik.csv


- Kolejne pomiary tego samego obrazu:
test_bubble_pomiar_{data}_{godzina}.csv

Program jest własnością koła naukowego KN PUT STEM, działającego na Politechnice Poznańskiej

Autorzy programu: Kamil Dalil, Mateusz Frąckowiak, Michał Dulek, Wiktor Makowski

