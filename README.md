# DropSize 
DropSize  jest narzędziem umożliwiającym automatyczną detekcję oraz analizę kropel emulsji na obrazach uzyskanych spod mikroskopu.


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
  Pozwala na wybór obrazu, na którym będzie wykonywana detekcja kropel.

- **Powiększenie obrazu (lista rozwijalna)**  
  Wybór skali na podstawie powiększenia, w jakim wykonano zdjęcie.
  
- **Skala obrazu [µm/piksel]**  
  Pole umożliwiające ręczne podanie skali obrazu.

- **Wpisz skalę**  
  Zapisuje wprowadzoną wartość skali do pamięci programu.

- **Ustal skalę ręcznie**  
  Umożliwia ręczne wyznaczenie skali poprzez zaznaczenie dwóch punktów na obrazie, a następnie podanie rzeczywistej odległości pomiędzy nimi (w µm).  
  Zalecane w przypadku obrazów o niestandardowej rozdzielczości.

---

### Detekcja i edycja kropel

- **Uruchom detekcję**  
  Oznacza wykryte krople na obrazie oraz zapisuje dane pomiarowe do pliku `.csv`.

- **Dodaj kroplę**  
  Funkcja umożliwiająca ręczne dodanie oznaczenia kropel poprzez:
  1. Kliknięcie w środek kropli
  2. Kliknięcie na jego krawędź (wyznaczenie promienia)
 
- **Usuń kroplę**
  Funkcja umożliwiająca ręczne usunięcie kropli poprzez:
  1. Kliknięcie w obszar jej oznaczenia

---

### Analiza wyników

- **Histogram ilościowy / częstościowy**  
  Wyświetla histogram ilościowy lub częstościowy średnic lropel.

- **Średnica Sautera**  
  Oblicza średnicę Sautera dla analizowanych kropel.

---

## Zapisywanie wyników

Po uruchomieniu detekcji, możliwe jest zapisanie:
  1. Średnic kropel w pliku .csv
  2. Obrazu wraz z naniesionymi obrysami kropel


Program jest własnością koła naukowego KN PUT STEM, działającego na Politechnice Poznańskiej

Autorzy programu: inż. Kamil Dalil, inż. Mateusz Frąckowiak, mgr inż. Ewelina Warmbier-Wytykowska, dr hab. inż. Sylwia Różańska, mgr inż. Anna Martin, inż. Michał Dulek, Wiktor Makowski

