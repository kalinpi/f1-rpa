# F1T003

## Informacje ogólne

| Informacja | Wartość |
|---|---|
| **Opiekun biznesowy** | |
| **Serwis RPA** | ServiceDesk → Żądanie/Incydent → Kategoria → RPA |
| **Konto robota (system)** | |
| **Konto AD (sieć/zasoby)** | |

## Opis

Robot liczy statystyki wyścigów Formuły 1 z pliku wynikowego robota F1T001 lub F1T002 (bez połączenia z internetem).

Zadanie `prep`:

1. Szuka w `SHARED/in/` plików `*RACES*.xlsx` z zakładką na każdy wyścig (Poz | Nr | Kierowca | Zespół | Gap | Opony | Okrążenia na stintach).
2. Liczy statystyki każdego wyścigu oraz podsumowanie wszystkich wyścigów.
3. Dopisuje zakładkę `Statystyki` i przenosi plik do `SHARED/out/`.

Szczegóły i diagramy: [docs/PL/README.md](docs/PL/README.md)

## Uruchomienie

```
./F1T003.sh prep
```

## Wyniki

#### `SHARED/out/` – przetworzone pliki

- zakładka `Statystyki`: wiersz na każdy wyścig (zwycięzca, zespół zwycięzcy, sklasyfikowani, DNF/DNS/DSQ, średnia liczba pit stopów, najczęstsza strategia opon, status)
- pod tabelą podsumowanie: liczba wyścigów, najczęstsza strategia, średnia pit stopów, suma DNF, najlepszy zespół (punkty 25-18-15-12-10-8-6-4-2-1), najwięcej zwycięstw
- nazwa pliku z datą i godziną przetworzenia, a przy błędzie (np. zakładka w złym formacie) z przedrostkiem `ERROR_`

#### `SHARED/log/prep/` – przebieg pracy robota

- `log.html` – działania robota krok po kroku i ewentualne błędy
- `stdout_<data>.log` – komunikaty z konsoli

#### `./log/` – statystyki (lokalnie)

- `f1t003-logs.xlsx` – statystyki pracy robota zebrane z plików `.json` przez zadanie `Dolog`

## Konfiguracja (.env)

| Zmienna | Opis |
|---|---|
| `MODE` | tryb pracy (`PROD` / `TEST`) |
| `TYPE` | typ robota (`FIL`) |
| `SHARED` | ścieżka do zasobu współdzielonego (puste = praca lokalna) |
| `SDIR` | lokalny folder z danymi testowymi (`./testcifs`) |
| `URL_PROD`, `URL_TEST` | nieużywane (robot FILE) |
| `LANGUAGE` | język komunikatów (`pl` / `en`) |
| `WAIT_TO_RESPONSE` | nieużywane (robot FILE) |
| `DRYRUN` | tryb testowy – same statusy, bez statystyk (`0` / `1`) |
| `RED`, `GREEN`, `GRAY`, `WHITE` | kolory komórek (ARGB) |
| `SECURED` | odszyfrowanie zmiennych z `.envs` (`0` / `1`) |
