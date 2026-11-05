# Issue Tracker

Backend: Local

Record: repo

The tracker is a JSON file driven by `tools/issues.py`. Run every command from the repository root.

## Operation Table

| Operation    | Backend call |
|--------------|--------------|
| fetch issue  | `python3 tools/issues.py fetch <N>` |
| list issues  | `python3 tools/issues.py list --state all --search <query>` |
| create issue | `python3 tools/issues.py create --title <title> --body-file <body-file>` |
| comment      | `python3 tools/issues.py comment <N> --body-file <body-file>` |
| edit body    | `python3 tools/issues.py edit <N> --body-file <body-file>` |
| add label    | `python3 tools/issues.py label add <N> <label>` |
| remove label | `python3 tools/issues.py label remove <N> <label>` |
| close issue  | `python3 tools/issues.py close <N>` |

`<query>` is one exact phrase matched against issue bodies.

## Label Role Mapping

| Canonical role  | Repo label      |
|-----------------|-----------------|
| needs-triage    | needs-triage    |
| needs-info      | needs-info      |
| ready-for-agent | ready-for-agent |
| ready-for-human | ready-for-human |
| wontfix         | wontfix         |
