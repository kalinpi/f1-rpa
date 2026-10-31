# F1T002

## 📋 General Information (Informacje ogólne)
| | |
|---|---|
| **Opiekun biznesowy** | xxxxx@poczta-polska.pl |
| **Serwis RPA** | ServiceDesk → Żądanie/Incydent → Kategoria → RPA |
| **Konto robota (system)** | `xxx_F1T` |
| **Konto AD (sieć/zasoby)** | `xxx_F1T_ad` |

## Description (Opis)

Robot pobiera wyniki wyścigów Formuły 1 z [REST API OpenF1](https://api.openf1.org/v1) (bez klucza API, dane od sezonu 2023) i składa się z zadań (tasków):

⚡prep - sprawdza czy w `SHARED\in\` są dane w pliku *RACES*.xlsx (A = rok, B = nazwa GP, toru lub kraju w dowolnej formie), tłumaczy nazwę GP słownikiem `SHARED\dicts\GP_DICT.xlsx`, wyszukuje wyścig i pobiera klasyfikację, kierowców oraz strategie opon. Dla każdego wyścigu dodaje zakładkę (np. `2025 Baku`), w kolumnie C zapisuje status wiersza i przenosi plik do `SHARED\out\`.

[📖 Szczegółowy opis tasków](docs/PL/README.md)

## ▶️ Run (Uruchomienie)
```
./F1T002.sh prep
```

## Results (Wyniki)

🚀 Po uruchomieniu robota, sprawdź przetworzone pliki w `SHARED/out/`

#### A→ W podkatalogu `SHARED/out`

- pliki `*RACES*.xlsx`, które robot już przetworzył
- w kolumnie C `OK` (szary) albo opis błędu (czerwony), np. nie znaleziono GP, niejednoznaczna nazwa GP, GP odwołane
- zakładka dla każdego wyścigu: Poz | Nr | Kierowca | Zespół | Gap do lidera / DNF | Opony (np. `HM`) | Okrążenia na stintach (np. `40/11`)
- pliki mają dopisaną datę i godzinę przetworzenia
- pliki z błędami otrzymują przedrostek `ERROR_`

#### B→ W podkatalogu `SHARED/log`

- w pliku `log.html` działania robota krok po kroku oraz ewentualne błędy
- w pliku `stdout.log` komunikaty z konsoli z działania robota

#### C→ W podkatalogu lokalnym `./log`
- w pliku `f1t002-logs.xlsx`, arkusze ze statystykami zebranymi z plików `.json`

## ⚙️ Configuration (.env) (Konfiguracja)
- *MODE* → tryb pracy (`PROD` / `TEST`)
- *TYPE* → tryb podłączenia robota `API`
- *SHARED* → ścieżka do zasobu współdzielonego (puste = praca lokalna)
- *SDIR* → lokalny folder z danymi testowymi (`./testcifs`)
- *URL_PROD*, *URL_TEST* → adres API OpenF1
- *LANGUAGE* → język komunikatów robota (`pl` / `en`)
- *WAIT_TO_RESPONSE* → timeout żądania (ms, stosowane minimum 5 s)
- *DRYRUN* → tryb testowy bez zapytań do API (`0` / `1`)
- *RED*, *GREEN*, *GRAY*, *WHITE* → kolory komórek (ARGB)
- *SECURED* → odszyfrowanie zmiennych `.envs` Fernetem (`0` / `1`)
