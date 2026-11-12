# Issue 001: Summarize example tasks

Status: ready

## User story
As a shop owner, I want task counts so I can see outstanding work.

## Acceptance criteria
- Create backend/summary.py.
- Use only the Python standard library.
- Read data/tasks.json relative to the script's project location.
- Print Total, Pending, In progress, and Done, in that order.
- The supplied example produces counts 3, 1, 1, 1.
- Running from the project root or backend directory works.
- Update README.md with the run command.
- Print Open after Done, counting pending plus in_progress tasks.
## Scope
Implement the summary command only.
Do not add frameworks, dependencies, web services, or a database.
Do not commit.
