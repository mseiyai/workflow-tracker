# Issue 002: Make task counting reusable

Status: ready

## Purpose
The shop's future API should reuse task counts without running
a terminal command.

## Acceptance criteria
- Add summarize_tasks(tasks) to backend/summary.py.
- Return a dictionary with integer values for:
  total, pending, in_progress, done, open.
- Define open as pending plus in_progress.
- The function must not read files, print, or modify its input.
- Keep file reading and printing in main().
- Preserve the four existing output lines.
- Append Open if it is not already present.
- Importing backend.summary must not run the command.
- Add tests/test_summary.py using unittest.
- Test an empty list and a list containing all three statuses.
- Document the test command in README.md.
- Test two completed tasks: total 2, done 2, open 0.

## Boundaries
Use valid task records with the three documented statuses.
Do not add validation, dependencies, an API, or a database.
Do not change data/tasks.json.
Do not commit.