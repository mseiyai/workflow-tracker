import type { Task, TaskStatus, TaskSummary } from './types'

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8001').replace(
  /\/+$/,
  '',
)

async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { signal })

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }

  return (await response.json()) as T
}

export function fetchTasks(
  status?: TaskStatus,
  signal?: AbortSignal,
): Promise<Task[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : ''

  return getJson<Task[]>(`/tasks${query}`, signal)
}

export function fetchSummary(signal?: AbortSignal): Promise<TaskSummary> {
  return getJson<TaskSummary>('/summary', signal)
}
