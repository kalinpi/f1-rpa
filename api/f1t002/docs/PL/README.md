## Dokumentacja opisująca zakres prac Robota F1T002

### Zadania (taski) robota

Robot składa się z dwóch zadań uruchamianych niezależnie (`F1T002.sh <zadanie>`):

| Zadanie | Opis |
|---|---|
| `prep` | Główne zadanie robota: wczytuje `RACES.xlsx` z katalogu `in/`, pobiera dane z OpenF1 API i zapisuje wynik `RACES_out.xlsx` do katalogu `out/`. |
| `Dolog` | Zbiera logi `.json` z kolejnych uruchomień do pliku Excel ze statystykami pracy robota. |

Zapis `F1T002@prep` na diagramach oznacza: robot F1T002, zadanie `prep`.

### Opis diagramów

- Diagramy opisujące, jak komponenty komunikują się ze sobą (i w jakiej kolejności).
    - Uproszczony zakres F1T002 na infrastrukturze
    ![0_tasks_Infrastructure](./0_tasks_Infrastructure.png)

    - Zadanie prepare

        Pobieranie wyników wyścigów F1 (klasyfikacja, kierowcy, strategie opon) z OpenF1 API dla wyścigów podanych w pliku RACES.xlsx – zakres realizowany w F1T002@prep
        ![1_task_prep_Component_Diagram](./1_task_prep_Component_Diagram.png)

    - [4_dolog_DiagramSekwencji](./4_dolog_SequenceDiagram.plantuml) główne sekwencje w dolog.py do zbierania statystyk do Excela.

#### Podgląd i edycja diagramów
Obrazki `.png` powyżej są wygenerowane z plików `.plantuml`. Po zmianie diagramu trzeba wygenerować je ponownie: `java -jar plantuml.jar -tpng <plik>.plantuml`.

Podgląd plików `.plantuml`:
- w edytorze: zainstaluj wtyczkę PlantUML (np. [VS Code](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml), [IntelliJ IDEA / PyCharm](https://plugins.jetbrains.com/plugin/7017-plantuml4idea)) oraz Javę i Graphviz zgodnie z opisem wtyczki,
- bez instalacji: wklej treść diagramu na stronie https://www.plantuml.com/plantuml/uml.
