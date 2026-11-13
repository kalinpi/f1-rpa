# F1T001

## Informacje ogólne

| Informacja | Wartość |
|---|---|
| **Opiekun biznesowy** | |
| **Serwis RPA** | ServiceDesk → Żądanie/Incydent → Kategoria → RPA |
| **Konto robota (system)** | |
| **Konto AD (sieć/zasoby)** | |

## Opis

Robot pobiera wyniki wyścigów Formuły 1 ze strony [Wikipedia](https://en.wikipedia.org) (scraping, dane od sezonu 1950).

Zadanie `prep`:

1. Szuka w `SHARED/in/` plików `*RACES*.xlsx` (kolumna A – rok, kolumna B – nazwa GP, toru lub kraju w dowolnej formie, np. `baku`, `monako`, `cota`).
2. Tłumaczy nazwę GP słownikiem `SHARED/dicts/GP_DICT.xlsx` i wyszukuje wyścig w kalendarzu sezonu (`/wiki/{rok}_Formula_One_World_Championship`) po kraju, nazwie GP, torze lub mieście.
3. Odczytuje tabelę `Race_classification` ze strony wyścigu i dla każdego wyścigu dodaje osobną zakładkę (np. `2025 Azerbaijan`).
4. W kolumnie C zapisuje status wiersza i przenosi plik do `SHARED/out/`.

Wikipedia nie publikuje strategii opon, dlatego kolumny Opony i Okrążenia na stintach są puste (pełne dane dla sezonów od 2023 daje robot F1T002). Między wczytaniami stron robot czeka 5 s (`Crawl-delay` z `robots.txt` Wikipedii).

Szczegóły i diagramy: [docs/PL/README.md](docs/PL/README.md)

## Uruchomienie

```
./F1T001.sh prep
```

## Wyniki

#### `SHARED/out/` – przetworzone pliki

- kolumna C: `OK` (szare tło) albo opis błędu (czerwone tło), np. nie znaleziono GP, niejednoznaczna nazwa GP, brak wyników (wyścig jeszcze się nie odbył)
- zakładka dla każdego wyścigu: Poz | Nr | Kierowca | Zespół | Gap do lidera / DNF / DNS / DSQ | Opony (puste) | Okrążenia na stintach (puste)
- nazwa pliku z datą i godziną przetworzenia, a przy błędzie z przedrostkiem `ERROR_`

#### `SHARED/log/prep/` – przebieg pracy robota

- `log.html` – działania robota krok po kroku i ewentualne błędy
- `stdout_<data>.log` – komunikaty z konsoli

#### `./log/` – statystyki (lokalnie)

- `f1t001-logs.xlsx` – statystyki pracy robota zebrane z plików `.json` przez zadanie `Dolog`

## Konfiguracja (.env)

| Zmienna | Opis |
|---|---|
| `MODE` | tryb pracy (`PROD` / `TEST`) |
| `TYPE` | typ robota (`WWW`) |
| `SHARED` | ścieżka do zasobu współdzielonego (puste = praca lokalna) |
| `SDIR` | lokalny folder z danymi testowymi (`./testcifs`) |
| `URL_PROD`, `URL_TEST` | adres strony (Wikipedia) |
| `LANGUAGE` | język komunikatów (`pl` / `en`) |
| `WAIT_TO_RESPONSE` | opóźnienie akcji przeglądarki w ms; timeout strony = 50 × wartość (minimum 20 s) |
| `DRYRUN` | tryb testowy bez odczytu wyników ze strony (`0` / `1`) |
| `RED`, `GREEN`, `GRAY`, `WHITE` | kolory komórek (ARGB) |
| `SECURED` | odszyfrowanie zmiennych z `.envs` (`0` / `1`) |

Robot nie loguje się na stronę, więc w `.envs` nie są potrzebne login i hasło.
