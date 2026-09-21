# Key Development Commands

Every row runs from the repository root, in any host shell – spell `python3` as `python` where only the Windows launcher is on PATH. The package resolves through the working directory, so a row run from elsewhere fails to import `src.reporter`.

## Running the Application

| Command | Description |
|---|---|
| `python3 -m src.reporter examples/march.csv --out .agent_temp/reports` | Export the sample ledger |
| `python3 -m src.reporter --help` | Arguments and defaults |

## Testing

| Tier | Command | Description |
|---|---|---|
| fast | `python3 -m unittest discover -s tests -t .` | Once per story – the unit suite |
| full | `python3 -m unittest discover -s tests -t . && python3 -m unittest discover -s tests -t . -p "journey_*.py"` | End of run – the unit suite plus the command-line journeys |
| run one test | `python3 -m unittest {file}.{test}` | One test, `{file}` a dotted module and `{test}` `Class.method` |

## Build & Deployment

| Command | Description |
|---|---|
| – | There is no build: the tool ships as the source tree and runs with `python3 -m` |
