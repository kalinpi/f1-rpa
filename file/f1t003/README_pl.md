# F1T003

## 📋 General Information (Informacje ogólne)
| | |
|---|---|
| **Opiekun biznesowy** | xxxxx@poczta-polska.pl |
| **Serwis RPA** | ServiceDesk → Żądanie/Incydent → Kategoria → RPA |
| **Konto robota (system)** | `xxx_F1T` |
| **Konto AD (sieć/zasoby)** | `xxx_F1T_ad` |

## Description (Opis)

Robot liczy statystyki wyścigów Formuły 1 z pliku wynikowego F1T001 / F1T002 (bez połączenia z internetem) i składa się z zadań (tasków):

⚡prep - sprawdza czy w `SHARED\in\` są dane w pliku *RACES*.xlsx (zakładka na każdy wyścig: Poz | Nr | Kierowca | Zespół | Gap | Opony | Okrążenia na stintach), liczy statystyki każdego wyścigu i podsumowanie, dopisuje zakładkę `Statystyki` i przenosi plik do `SHARED\out\`.

[📖 Szczegółowy opis tasków](docs/PL/README.md)

## ▶️ Run (Uruchomienie)
```
./F1T003.sh prep
```

## Results (Wyniki)

🚀 Po uruchomieniu robota, sprawdź przetworzone pliki w `SHARED/out/`

#### A→ W podkatalogu `SHARED/out`

- pliki `*RACES*.xlsx`, które robot już przetworzył
- zakładka `Statystyki`: wiersz na każdy wyścig (zwycięzca, zespół zwycięzcy, sklasyfikowani, DNF/DNS/DSQ, średnia liczba pit stopów, najczęstsza strategia opon, status)
- pod tabelą podsumowanie: liczba wyścigów, najczęstsza strategia, średnia pit stopów, suma DNF, najlepszy zespół (punkty 25-18-15-12-10-8-6-4-2-1), najwięcej zwycięstw
- pliki mają dopisaną datę i godzinę przetworzenia
- pliki z błędami (np. zakładka w złym formacie) otrzymują przedrostek `ERROR_`

#### B→ W podkatalogu `SHARED/log`

- w pliku `log.html` działania robota krok po kroku oraz ewentualne błędy
- w pliku `stdout.log` komunikaty z konsoli z działania robota

#### C→ W podkatalogu lokalnym `./log`
- w pliku `f1t003-logs.xlsx`, arkusze ze statystykami zebranymi z plików `.json`

## ⚙️ Configuration (.env) (Konfiguracja)
- *MODE* → tryb pracy (`PROD` / `TEST`)
- *TYPE* → tryb podłączenia robota `FIL`
- *SHARED* → ścieżka do zasobu współdzielonego (puste = praca lokalna)
- *SDIR* → lokalny folder z danymi testowymi (`./testcifs`)
- *URL_PROD*, *URL_TEST* → nieużywane (tryb FILE)
- *LANGUAGE* → język komunikatów robota (`pl` / `en`)
- *WAIT_TO_RESPONSE* → nieużywane (tryb FILE)
- *DRYRUN* → tryb testowy, same statusy bez statystyk (`0` / `1`)
- *RED*, *GREEN*, *GRAY*, *WHITE* → kolory komórek (ARGB)
- *SECURED* → odszyfrowanie zmiennych `.envs` Fernetem (`0` / `1`)
