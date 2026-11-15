# Issue 005: Display the workflow dashboard

Status: ready

## User story

As the stationery shop owner, I want a browser dashboard showing task
totals and current work so that I can understand the workload at a glance.

## Acceptance criteria

- Create a React and TypeScript application in frontend/.
- Use the Vite react-ts template.
- Display the title "Workflow Tracker".
- Fetch summary data from GET /summary.
- Fetch tasks from GET /tasks.
- Define TypeScript types for Task, TaskStatus, and TaskSummary.
- Keep HTTP request functions in frontend/src/api.ts.
- Display cards for Total, Pending, In progress, Done, and Open.
- Display task ID, title, and status in a table.
- Show a loading message while requests are running.
- Show a visible error message if either request fails.
- Show an empty-state message if there are no tasks.
- Read VITE_API_URL, falling back to http://localhost:8001.
- Allow only the local Vite origins in FastAPI CORS configuration.
- Preserve all existing API contracts and backend tests.
- Update README.md with frontend and full-stack startup instructions.
- npm run build succeeds.
- data/tasks.json is unchanged.

## Out of scope

- Creating or editing tasks
- Authentication
- Routing
- State-management libraries
- Frontend testing frameworks
- PostgreSQL
- Docker
- Deployment

## Verification

- python -m unittest discover -s tests -v
- npm run build
- Run both development servers.
- Confirm summary cards agree with GET /summary.
- Confirm the task table agrees with GET /tasks.
- Confirm loading, error, empty, and success states were considered.
- git diff --check

Do not commit.