import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosError } from 'axios'
import { handleApiError } from './errors'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance with default config
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth tokens
axiosInstance.interceptors.request.use(
  (config) => {
    // Get auth token from localStorage if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as AxiosRequestConfig & { _retryCount?: number }

    // Retry logic for transient failures
    if (config && shouldRetry(error)) {
      config._retryCount = config._retryCount || 0

      if (config._retryCount < 3) {
        config._retryCount++

        // Exponential backoff: 1s, 2s, 4s
        const delay = Math.pow(2, config._retryCount - 1) * 1000
        await new Promise((resolve) => setTimeout(resolve, delay))

        return axiosInstance(config)
      }
    }

    // Handle 401 Unauthorized - clear token and redirect to login
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      // You can dispatch an event or use router here to redirect to login
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }

    return Promise.reject(error)
  }
)

function shouldRetry(error: AxiosError): boolean {
  // Don't retry if no config (can't retry)
  if (!error.config) {
    return false
  }

  // Don't retry 4xx errors (client errors) except 429 (rate limit)
  if (error.response?.status && error.response.status >= 400 && error.response.status < 500) {
    return error.response.status === 429
  }

  // Retry on 5xx errors (server errors)
  if (error.response?.status && error.response.status >= 500) {
    return true
  }

  // Retry on network errors
  if (error.code === 'ERR_NETWORK') {
    return true
  }

  // Retry on timeout
  if (error.code === 'ECONNABORTED') {
    return true
  }

  return false
}

export const apiClient = {
  async get<T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await axiosInstance.get<T>(endpoint, config)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async post<T>(endpoint: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await axiosInstance.post<T>(endpoint, data, config)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async put<T>(endpoint: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await axiosInstance.put<T>(endpoint, data, config)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async patch<T>(endpoint: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await axiosInstance.patch<T>(endpoint, data, config)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },

  async delete<T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await axiosInstance.delete<T>(endpoint, config)
      return response.data
    } catch (error) {
      throw handleApiError(error)
    }
  },
}

export default axiosInstance
