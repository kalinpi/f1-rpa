# Checklista F1T002

1. ✅ Wykonanie kodu zgodnie z diagramami

2. ✅ Warunek wejścia do tasków
    + Prep - pliki w katalogu `in/` o masce `*RACES*.xlsx`
    + Dolog - pliki `*.json` w katalogu `log/`

3. ✅ Warunek zakończenia tasków
    + Prep - po wykonaniu pracy pliki z katalogu `in/` są przenoszone do `out/` (z datą lub z prefiksem `ERROR_`)
    + Dolog - pliki `*.json` z katalogu `log/` są usuwane

4. ✅ Odnotowanie pracy (zabezpieczenie przed ponownym uruchomieniem)
    + Prep - zapisywanie statusu w kolumnie C (OK / opis błędu)
    + Dolog - usunięte pliki `*.json` z katalogu `log/`

5. ✅ Czas oczekiwania na odpowiedź dynamicznie
    + Prep - oczekiwanie ze zmiennej `WAIT_TO_RESPONSE` w `.env` (ms przeliczane na sekundy dla requests)

6. ✅ Obsługa błędów (try/except)
    + Prep - kontynuacja pracy przy niedostępności OpenF1 API lub przekroczeniu limitu zapytań (pauzy między zapytaniami)

7. ✅ Komunikaty tasków w oddzielnych plikach
    + Prep - komunikaty o nieznalezionym GP, niejednoznacznej nazwie GP i braku danych w API (`translations/pl.yaml`, `en.yaml`)

8. ✅ Diagramy
    + ✅ Infrastruktury
    + ✅ Komponentów (prep)
    + ✅ Sekwencji (dolog, kopia z WTH001)
    + ✅ Opisy funkcji w kodzie

9. ❌ Fixy z/do szablonu v2
    + ✅ Pobranie poprawek do Dolog (identyczny z v2)
    + ❌ Zgłoszenie poprawek do v2 (WAIT_TO_RESPONSE w ms przekazywany do requests jako sekundy; nazwa logu `.json` z dokładnością do sekundy – szybki przebieg nadpisuje zamknięty log)

10. ✅ Policzenie pracy
    + ✅ Zapis przebiegu do `.json`
    + ✅ Formuły Excel w statystykach Dolog

11. ❌ Weryfikacja pliku `F1T002.sh` oraz proxy
    + ✅ Składnia `bash -n`
    + ❌ Uruchomienie przez `rcc` i proxy na serwerze

12. ✅ Dokumentacja
    + ✅ `docs/README.md` (PL/EN)
    + ✅ `README.md` / `README_pl.md` robota

13. ❌ Pilot - weryfikacja i strojenie na środowisku docelowym (powtórzenie pkt. 1-12)
