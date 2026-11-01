## Documentation describing the Robot F1T001 scope of work

### Robot tasks

The robot consists of two tasks run independently (`F1T001.sh <task>`):

| Task | Description |
|---|---|
| `prep` | Main robot task: reads `RACES.xlsx` from the `in/` folder, reads the calendar and results from the website (Wikipedia) and saves the result `RACES_out.xlsx` to the `out/` folder. |
| `Dolog` | Collects `.json` logs from consecutive runs into an Excel file with robot work statistics. |

The notation `F1T001@prep` on the diagrams means: robot F1T001, task `prep`.

### Diagrams Description

- Diagrams describing how components communicate with each other (and in what order).
    - Simplified scope of F1T001 on infrastructure
    ![0_tasks_Infrastructure](./0_tasks_Infrastructure.plantuml)

    - Prepare task

        Fetching F1 race results (classification, drivers, teams) from the website (Wikipedia) for the races listed in RACES.xlsx – scope implemented in F1T001@prep
        ![1_task_prep_Component_Diagram](./1_task_prep_Component_Diagram.plantuml)

    - [4_dolog_SequenceDiagram](./4_dolog_SequenceDiagram.plantuml) main sequences in dolog.py for collecting statistics into Excel.

#### VS Code
1. Install the [PlantUML](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml) extension for VS Code.
2. Install Java and Graphviz according to the extension description.
3. Open a `.plantuml` file and press `Option+D` (macOS) / `Alt+D` (Windows) to see the preview.

#### WWW
4. Alternatively, paste the diagram content on the page http://www.plantuml.com/plantuml/uml
