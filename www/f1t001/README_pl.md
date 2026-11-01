# F1T001

## 📋 General Information (Informacje ogólne)
| | |
|---|---|
| **Opiekun biznesowy** | xxxxx@poczta-polska.pl |
| **Serwis RPA** | ServiceDesk → Żądanie/Incydent → Kategoria → RPA |
| **Konto robota (system)** | `xxx_F1T` |
| **Konto AD (sieć/zasoby)** | `xxx_F1T_ad` |

## Description (Opis)

Robot pobiera wyniki wyścigów Formuły 1 ze strony [WWW](https://en.wikipedia.org) (Wikipedia, dane od sezonu 1950) i składa się z zadań (tasków):

⚡prep - sprawdza czy w `SHARED\in\` są dane w pliku `*RACES*.xlsx` (A = rok, B = nazwa GP, toru lub kraju w dowolnej formie), tłumaczy nazwę GP słownikiem `SHARED\dicts\GP_DICT.xlsx`, wyszukuje wyścig w kalendarzu sezonu i odczytuje klasyfikację ze strony wyścigu (scraping). Dla każdego wyścigu dodaje zakładkę (np. `2025 Azerbaijan`), w kolumnie C zapisuje status wiersza i przenosi plik do `SHARED\out\`.

> ℹ️ **Tryb WWW (scraping).** Robot otwiera w przeglądarce stronę sezonu
> (`/wiki/{rok}_Formula_One_World_Championship`), w tabeli kalendarza dopasowuje GP po kraju (flaga),
> nazwie GP, torze lub mieście, a potem odczytuje tabelę `Race_classification` ze strony wyścigu.
> Wikipedia nie publikuje strategii opon, dlatego kolumny Opony i Okrążenia na stintach są puste
> (pełne dane dla sezonów od 2023 daje robot F1T002).
> Między wczytaniami stron robot czeka 5 s (`Crawl-delay` z `robots.txt` Wikipedii).

[📖 Szczegółowy opis tasków](docs/PL/README.md)

## ▶️ Run (Uruchomienie)
```
./F1T001.sh prep
```

## Results (Wyniki)

🚀 Po uruchomieniu robota, sprawdź przetworzone pliki w `SHARED/out/`

#### A→ W podkatalogu `SHARED/out`

- pliki `*RACES*.xlsx`, które robot już przetworzył
- w kolumnie C `OK` (szary) albo opis błędu (czerwony), np. nie znaleziono GP, niejednoznaczna nazwa GP, brak wyników (wyścig jeszcze się nie odbył)
- zakładka dla każdego wyścigu: Poz | Nr | Kierowca | Zespół | Gap do lidera / DNF / DNS / DSQ | Opony (puste) | Okrążenia na stintach (puste)
- pliki mają dopisaną datę i godzinę przetworzenia
- pliki z błędami otrzymują przedrostek `ERROR_`

#### B→ W podkatalogu `SHARED/log`

- w pliku `log.html` działania robota krok po kroku oraz ewentualne błędy
- w pliku `stdout.log` komunikaty z konsoli z działania robota

#### C→ W podkatalogu lokalnym `./log`
- w pliku `f1t001-logs.xlsx`, arkusze ze statystykami zebranymi z plików `.json`

## ⚙️ Configuration (.env) (Konfiguracja)
- *MODE* → tryb pracy (`PROD` / `TEST`)
- *TYPE* → tryb podłączenia robota `WWW`
- *SHARED* → ścieżka do zasobu współdzielonego (puste = praca lokalna)
- *SDIR* → lokalny folder z danymi testowymi (`./testcifs`)
- *URL_PROD*, *URL_TEST* → adres strony (Wikipedia)
- *LANGUAGE* → język komunikatów robota (`pl` / `en`)
- *WAIT_TO_RESPONSE* → opóźnienie akcji przeglądarki (ms), timeout strony = 50 × wartość (minimum 20 s)
- *DRYRUN* → tryb testowy bez odczytu wyników ze strony (`0` / `1`)
- *RED*, *GREEN*, *GRAY*, *WHITE* → kolory komórek (ARGB)
- *SECURED* → odszyfrowanie zmiennych `.envs` Fernetem (`0` / `1`)
- W trybie uruchomienia WWW nie jest potrzebne login i hasło w pliku `.envs`
