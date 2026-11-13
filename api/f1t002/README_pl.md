# F1T002

## Informacje ogólne

| Informacja | Wartość |
|---|---|
| **Opiekun biznesowy** | |
| **Serwis RPA** | ServiceDesk → Żądanie/Incydent → Kategoria → RPA |
| **Konto robota (system)** | |
| **Konto AD (sieć/zasoby)** | |

## Opis

Robot pobiera wyniki wyścigów Formuły 1 z [OpenF1 API](https://openf1.org) (bez klucza API, dane od sezonu 2023).

Zadanie `prep`:

1. Szuka w `SHARED/in/` plików `*RACES*.xlsx` (kolumna A – rok, kolumna B – nazwa GP, toru lub kraju w dowolnej formie, np. `baku`, `Monaco`, `cota`).
2. Tłumaczy nazwę GP słownikiem `SHARED/dicts/GP_DICT.xlsx` i wyszukuje wyścig.
3. Pobiera klasyfikację, kierowców i strategie opon, a dla każdego wyścigu dodaje osobną zakładkę (np. `2025 Baku`).
4. W kolumnie C zapisuje status wiersza i przenosi plik do `SHARED/out/`.

Szczegóły i diagramy: [docs/PL/README.md](docs/PL/README.md)

## Uruchomienie

```
./F1T002.sh prep
```

## Wyniki

#### `SHARED/out/` – przetworzone pliki

- kolumna C: `OK` (szare tło) albo opis błędu (czerwone tło), np. nie znaleziono GP, niejednoznaczna nazwa GP, GP odwołane
- zakładka dla każdego wyścigu: Poz | Nr | Kierowca | Zespół | Gap do lidera / DNF | Opony (np. `HM`) | Okrążenia na stintach (np. `40/11`)
- nazwa pliku z datą i godziną przetworzenia, a przy błędzie z przedrostkiem `ERROR_`

#### `SHARED/log/prep/` – przebieg pracy robota

- `log.html` – działania robota krok po kroku i ewentualne błędy
- `stdout_<data>.log` – komunikaty z konsoli

#### `./log/` – statystyki (lokalnie)

- `f1t002-logs.xlsx` – statystyki pracy robota zebrane z plików `.json` przez zadanie `Dolog`

## Konfiguracja (.env)

| Zmienna | Opis |
|---|---|
| `MODE` | tryb pracy (`PROD` / `TEST`) |
| `TYPE` | typ robota (`API`) |
| `SHARED` | ścieżka do zasobu współdzielonego (puste = praca lokalna) |
| `SDIR` | lokalny folder z danymi testowymi (`./testcifs`) |
| `URL_PROD`, `URL_TEST` | adres OpenF1 API |
| `LANGUAGE` | język komunikatów (`pl` / `en`) |
| `WAIT_TO_RESPONSE` | timeout zapytania w ms (stosowane minimum 5 s) |
| `DRYRUN` | tryb testowy bez zapytań do API (`0` / `1`) |
| `RED`, `GREEN`, `GRAY`, `WHITE` | kolory komórek (ARGB) |
| `SECURED` | odszyfrowanie zmiennych z `.envs` (`0` / `1`) |
