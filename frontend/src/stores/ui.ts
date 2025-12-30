import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ApiError } from '../api/errors'

export type FantasyPlatform = 'espn' | 'sleeper' | 'yahoo' | null

export interface LoadingState {
  [key: string]: boolean
}

export interface ErrorState {
  message: string
  code?: number
  timestamp: number
}

export const useUiStore = defineStore('ui', () => {
  // State
  const selectedPlatform = ref<FantasyPlatform>(null)
  const loadingStates = ref<LoadingState>({})
  const globalError = ref<ErrorState | null>(null)
  const notifications = ref<Array<{ id: string; message: string; type: 'info' | 'success' | 'warning' | 'error' }>>([])

  // Computed
  const isLoading = computed(() => {
    return Object.values(loadingStates.value).some((loading) => loading)
  })

  const hasError = computed(() => globalError.value !== null)

  // Actions
  function setLoading(key: string, value: boolean) {
    loadingStates.value[key] = value
  }

  function startLoading(key: string) {
    setLoading(key, true)
  }

  function stopLoading(key: string) {
    setLoading(key, false)
  }

  function clearLoading() {
    loadingStates.value = {}
  }

  function setSelectedPlatform(platform: FantasyPlatform) {
    selectedPlatform.value = platform
  }

  function setError(error: ApiError | Error | string) {
    if (typeof error === 'string') {
      globalError.value = {
        message: error,
        timestamp: Date.now(),
      }
    } else if (error instanceof Error) {
      globalError.value = {
        message: error.message,
        code: (error as ApiError).statusCode,
        timestamp: Date.now(),
      }
    }
  }

  function clearError() {
    globalError.value = null
  }

  function addNotification(message: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') {
    const id = `notification-${Date.now()}-${Math.random()}`
    notifications.value.push({ id, message, type })

    // Auto-remove after 5 seconds
    setTimeout(() => {
      removeNotification(id)
    }, 5000)

    return id
  }

  function removeNotification(id: string) {
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  function clearNotifications() {
    notifications.value = []
  }

  async function withLoading<T>(key: string, asyncFn: () => Promise<T>): Promise<T> {
    startLoading(key)
    try {
      return await asyncFn()
    } finally {
      stopLoading(key)
    }
  }

  return {
    // State
    selectedPlatform,
    loadingStates,
    globalError,
    notifications,

    // Computed
    isLoading,
    hasError,

    // Actions
    setLoading,
    startLoading,
    stopLoading,
    clearLoading,
    setSelectedPlatform,
    setError,
    clearError,
    addNotification,
    removeNotification,
    clearNotifications,
    withLoading,
  }
})
