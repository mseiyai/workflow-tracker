# Working instructions for Workflow Tracker

## Context
- Read README.md, docs/product.md, and the requested issue before editing.
- Treat repository files as the current project record.
- Do not assume a previous lesson or issue has been completed.

## Workflow
- Check the current directory, branch, and Git status first.
- Preserve existing changes. Do not reset, clean, or overwrite unrelated work.
- Implement only the requested issue.
- Keep changes small and explain assumptions.
- Do not add dependencies or frameworks unless the issue requires them.
- Do not commit, push, or deploy unless explicitly requested.

## Python
- Use the standard library for the current milestone.
- Keep counting logic separate from file reading and printing.
- Resolve project data paths from the script location.
- Do not modify data/tasks.json merely to make checks pass.

## Verification
Run from the repository root:
- python3 backend/summary.py
- (cd backend && python3 summary.py)
- python3 -m unittest discover -s tests -v, once tests exist
- git diff --check

Report actual commands, results, and any checks not run.
Zero discovered tests does not count as successful verification.