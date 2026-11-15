import type { Task, TaskStatus, TaskSummary } from './types'

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8001').replace(
  /\/+$/,
  '',
)

function serverErrorMessage(body: unknown): string | null {
  if (typeof body !== 'object' || body === null || !('detail' in body)) {
    return null
  }

  const detail = body.detail
  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    const messages = detail.flatMap((item) => {
      if (typeof item === 'object' && item !== null && 'msg' in item) {
        return typeof item.msg === 'string' ? [item.msg] : []
      }

      return []
    })

    return messages.length > 0 ? messages.join(', ') : null
  }

  return null
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init)

  if (!response.ok) {
    let body: unknown

    try {
      body = await response.json()
    } catch {
      body = null
    }

    throw new Error(
      serverErrorMessage(body) ?? `Request failed with status ${response.status}`,
    )
  }

  return (await response.json()) as T
}

export function fetchTasks(
  status?: TaskStatus,
  signal?: AbortSignal,
): Promise<Task[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : ''

  return requestJson<Task[]>(`/tasks${query}`, { signal })
}

export function fetchSummary(signal?: AbortSignal): Promise<TaskSummary> {
  return requestJson<TaskSummary>('/summary', { signal })
}

export function createTask(title: string): Promise<Task> {
  return requestJson<Task>('/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  })
}
