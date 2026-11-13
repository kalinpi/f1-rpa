## Documentation describing the Robot F1T003 scope of work

### Robot tasks

The robot consists of two tasks run independently (`F1T003.sh <task>`):

| Task | Description |
|---|---|
| `prep` | Main robot task: reads the F1T001 / F1T002 output file (`*RACES*.xlsx`) from the `in/` folder, computes race statistics, adds the `Statistics` sheet and moves the file to the `out/` folder. Works offline. |
| `Dolog` | Collects `.json` logs from consecutive runs into an Excel file with robot work statistics. |

The notation `F1T003@prep` on the diagrams means: robot F1T003, task `prep`.

### Diagrams Description

- Diagrams describing how components communicate with each other (and in what order).
    - Simplified scope of F1T003 on infrastructure
    ![0_tasks_Infrastructure](./0_tasks_Infrastructure.png)

    - Prepare task

        Computing statistics (winner, DNF, pit stops, tyre strategies, best team) from race result sheets – scope implemented in F1T003@prep
        ![1_task_prep_Component_Diagram](./1_task_prep_Component_Diagram.png)

    - [4_dolog_SequenceDiagram](./4_dolog_SequenceDiagram.plantuml) main sequences in dolog.py for collecting statistics into Excel.

#### Viewing and editing the diagrams
The `.png` images above are generated from the `.plantuml` files. After changing a diagram, generate them again: `java -jar plantuml.jar -tpng <file>.plantuml`.

To preview `.plantuml` files:
- in an editor: install a PlantUML plugin (e.g. [VS Code](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml), [IntelliJ IDEA / PyCharm](https://plugins.jetbrains.com/plugin/7017-plantuml4idea)) and Java and Graphviz as described by the plugin,
- without installing anything: paste the diagram content on https://www.plantuml.com/plantuml/uml.
