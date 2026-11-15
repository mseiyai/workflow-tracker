import { useEffect, useState, type FormEvent } from 'react'
import { createTask, fetchSummary, fetchTasks } from './api'
import type { Task, TaskFilter, TaskStatus, TaskSummary } from './types'
import './App.css'

interface DashboardData {
  tasks: Task[]
  summary: TaskSummary
}

interface DashboardProps extends DashboardData {
  selectedFilter: TaskFilter
  onFilterChange: (filter: TaskFilter) => void
}

const statusLabels: Record<TaskStatus, string> = {
  pending: 'Pending',
  in_progress: 'In progress',
  done: 'Done',
}

const filters: ReadonlyArray<{ label: string; value: TaskFilter }> = [
  { label: 'All', value: 'all' },
  { label: 'Pending', value: 'pending' },
  { label: 'In progress', value: 'in_progress' },
  { label: 'Done', value: 'done' },
]

function Dashboard({
  tasks,
  summary,
  selectedFilter,
  onFilterChange,
}: DashboardProps) {
  const summaryItems = [
    { label: 'Total', value: summary.total },
    { label: 'Pending', value: summary.pending },
    { label: 'In progress', value: summary.in_progress },
    { label: 'Done', value: summary.done },
    { label: 'Open', value: summary.open },
  ]

  return (
    <>
      <section className="summary-section" aria-labelledby="summary-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Today at a glance</p>
            <h2 id="summary-heading">Task summary</h2>
          </div>
          <p>Live totals from the workflow API</p>
        </div>

        <dl className="summary-grid">
          {summaryItems.map((item) => (
            <div
              className={`summary-card summary-card--${item.label.toLowerCase().replace(' ', '-')}`}
              key={item.label}
            >
              <dt>{item.label}</dt>
              <dd>{item.value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="tasks-section" aria-labelledby="tasks-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Current work</p>
            <h2 id="tasks-heading">Tasks</h2>
          </div>
          <p>{tasks.length === 1 ? '1 task' : `${tasks.length} tasks`}</p>
        </div>

        <div
          className="filter-controls"
          role="group"
          aria-label="Filter tasks by status"
        >
          {filters.map((filter) => {
            const isActive = selectedFilter === filter.value

            return (
              <button
                className={`filter-button${isActive ? ' filter-button--active' : ''}`}
                type="button"
                aria-pressed={isActive}
                onClick={() => onFilterChange(filter.value)}
                key={filter.value}
              >
                {filter.label}
              </button>
            )
          })}
        </div>

        {tasks.length === 0 ? (
          <div className="empty-state">
            <h3>No matching tasks</h3>
            <p>Try another status to see the work currently available.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">ID</th>
                  <th scope="col">Task</th>
                  <th scope="col">Status</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <tr key={task.id}>
                    <td className="task-id">#{task.id}</td>
                    <td className="task-title">{task.title}</td>
                    <td>
                      <span className={`status status--${task.status}`}>
                        {statusLabels[task.status]}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  )
}

function App() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedFilter, setSelectedFilter] = useState<TaskFilter>('all')
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [createError, setCreateError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)
  const [refreshVersion, setRefreshVersion] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    async function loadDashboard() {
      setLoading(true)
      setError(null)

      try {
        const [tasks, summary] = await Promise.all([
          fetchTasks(
            selectedFilter === 'all' ? undefined : selectedFilter,
            controller.signal,
          ),
          fetchSummary(controller.signal),
        ])

        setData({ tasks, summary })
      } catch (requestError: unknown) {
        if (controller.signal.aborted) {
          return
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : 'An unexpected error occurred',
        )
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    void loadDashboard()

    return () => controller.abort()
  }, [selectedFilter, refreshVersion])

  async function handleCreateTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (creating || !newTaskTitle.trim()) {
      return
    }

    setCreating(true)
    setCreateError(null)

    try {
      await createTask(newTaskTitle)
      setNewTaskTitle('')
      setRefreshVersion((version) => version + 1)
    } catch (requestError: unknown) {
      setCreateError(
        requestError instanceof Error
          ? requestError.message
          : 'An unexpected error occurred',
      )
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-mark" aria-hidden="true">
          WT
        </div>
        <div>
          <p className="eyebrow">Stationery operations</p>
          <h1>Workflow Tracker</h1>
          <p className="header-description">
            A clear view of orders, quotations, and deliveries.
          </p>
        </div>
      </header>

      <main>
        <section
          className="create-task-section"
          aria-labelledby="create-task-heading"
        >
          <div className="section-heading">
            <div>
              <p className="eyebrow">Add work</p>
              <h2 id="create-task-heading">Create a task</h2>
            </div>
            <p>New tasks start as pending</p>
          </div>

          <form className="create-task-form" onSubmit={handleCreateTask}>
            <div className="create-task-field">
              <label htmlFor="new-task-title">Task title</label>
              <input
                id="new-task-title"
                name="title"
                type="text"
                value={newTaskTitle}
                onChange={(event) => setNewTaskTitle(event.target.value)}
                aria-describedby={
                  createError
                    ? 'new-task-help new-task-error'
                    : 'new-task-help'
                }
                aria-invalid={createError ? true : undefined}
                required
              />
              <span id="new-task-help" className="field-help">
                Describe the order, quotation, or delivery.
              </span>
            </div>
            <button
              className="create-task-button"
              type="submit"
              disabled={creating || !newTaskTitle.trim()}
            >
              {creating ? 'Creating…' : 'Create task'}
            </button>
          </form>

          {createError && (
            <p id="new-task-error" className="form-error" role="alert">
              {createError}
            </p>
          )}
        </section>

        {loading && (
          <div className="state-panel" aria-live="polite">
            <div className="loading-indicator" aria-hidden="true" />
            <h2>Loading workflow</h2>
            <p>Gathering the latest tasks and totals…</p>
          </div>
        )}

        {!loading && error && (
          <div className="state-panel state-panel--error" role="alert">
            <span className="error-icon" aria-hidden="true">
              !
            </span>
            <h2>Unable to load the dashboard</h2>
            <p>{error}. Check that the API server is running and try again.</p>
          </div>
        )}

        {!loading && !error && data && (
          <Dashboard
            tasks={data.tasks}
            summary={data.summary}
            selectedFilter={selectedFilter}
            onFilterChange={setSelectedFilter}
          />
        )}
      </main>

      <footer>
        <p>Workflow Tracker · Local operations dashboard</p>
      </footer>
    </div>
  )
}

export default App
