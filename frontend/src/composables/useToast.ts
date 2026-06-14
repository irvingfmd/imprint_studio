import { reactive } from 'vue'

interface Toast {
  id: number
  message: string
  variant: 'success' | 'error' | 'info'
}

const toasts = reactive<Toast[]>([])
let nextId = 0

export function useToast() {
  function show(message: string, variant: 'success' | 'error' | 'info' = 'success') {
    const id = nextId++
    toasts.push({ id, message, variant })
    setTimeout(() => {
      const idx = toasts.findIndex(t => t.id === id)
      if (idx !== -1) toasts.splice(idx, 1)
    }, 3500)
  }

  return { toasts, show }
}
