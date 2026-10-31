## Dokumentacja opisująca zakres prac Robota F1T003

### Zadania (taski) robota

Robot składa się z dwóch zadań uruchamianych niezależnie (`F1T003.sh <zadanie>`):

| Zadanie | Opis |
|---|---|
| `prep` | Główne zadanie robota: wczytuje plik wynikowy F1T001 / F1T002 (`*RACES*.xlsx`) z katalogu `in/`, liczy statystyki wyścigów, dopisuje zakładkę `Statystyki` i przenosi plik do katalogu `out/`. Działa bez internetu. |
| `Dolog` | Zbiera logi `.json` z kolejnych uruchomień do pliku Excel ze statystykami pracy robota. |

Zapis `F1T003@prep` na diagramach oznacza: robot F1T003, zadanie `prep`.

### Opis diagramów

- Diagramy opisujące, jak komponenty komunikują się ze sobą (i w jakiej kolejności).
    - Uproszczony zakres F1T003 na infrastrukturze
    ![0_tasks_Infrastructure](./0_tasks_Infrastructure.plantuml)

    - Zadanie prepare

        Liczenie statystyk (zwycięzca, DNF, pit stopy, strategie opon, najlepszy zespół) z zakładek z wynikami wyścigów – zakres realizowany w F1T003@prep
        ![1_task_prep_Component_Diagram](./1_task_prep_Component_Diagram.plantuml)

    - [4_dolog_DiagramSekwencji](./4_dolog_SequenceDiagram.plantuml) główne sekwencje w dolog.py do zbierania statystyk do Excela.

#### VS Code
1. Zainstaluj rozszerzenie [PlantUML](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml) dla VS Code.
2. Zainstaluj Javę i Graphviz zgodnie z opisem wtyczki.
3. Otwórz plik `.plantuml` i wciśnij `Option+D` (macOS) / `Alt+D` (Windows), aby zobaczyć podgląd.

#### WWW
4. Ewentualnie wklej treść diagramu na stronie http://www.plantuml.com/plantuml/uml
