# Issue 006: Create tasks and update their status

Status: ready

## User story

As the stationery shop owner, I want to add work and change its status
so that the tracker reflects the shop's current workflow.

## Acceptance criteria

- Add POST /tasks.
- Accept a JSON body containing only title.
- Trim surrounding whitespace from title.
- Reject a blank title or a title longer than 120 characters with HTTP 422.
- Reject unexpected request fields with HTTP 422.
- Assign the next available integer ID.
- Give every new task the pending status.
- Return HTTP 201 and the created task.
- Add PATCH /tasks/{task_id}/status.
- Accept pending, in_progress, or done.
- Return the updated task with HTTP 200.
- Return HTTP 404 when the task ID does not exist.
- Return HTTP 422 for an unsupported status.
- Existing GET /tasks and GET /summary reflect in-memory changes.
- Use explicit Pydantic request and response models.
- Keep mutable storage outside endpoint functions.
- Each API test receives isolated task state.
- Extend CORS to permit GET, POST, and PATCH.
- Preserve all existing API response contracts.
- Update README.md.
- Do not modify data/tasks.json.

## Temporary-storage boundary

- Initialize the in-memory store from data/tasks.json.
- Do not persist writes to the JSON file.
- Restarting the application may reset created and updated tasks.
- PostgreSQL persistence belongs to a later issue.

## Verification

- python -m unittest discover -s tests -p "test_api_write.py" -v
- python -m unittest discover -s tests -v
- npm run build
- Manual POST, PATCH, GET, and invalid-body requests
- git diff --check
- git diff -- data/tasks.json

Do not commit.