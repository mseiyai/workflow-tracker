export type TaskStatus = 'pending' | 'in_progress' | 'done'
export type TaskFilter = 'all' | TaskStatus

export interface Task {
  id: number
  title: string
  status: TaskStatus
}

export interface TaskSummary {
  total: number
  pending: number
  in_progress: number
  done: number
  open: number
}
