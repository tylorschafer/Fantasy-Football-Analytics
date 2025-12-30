import type { AxiosError } from 'axios'

export class ApiError extends Error {
  statusCode?: number
  originalError?: AxiosError

  constructor(
    message: string,
    statusCode?: number,
    originalError?: AxiosError
  ) {
    super(message)
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.originalError = originalError
  }
}

export function handleApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error
  }

  const axiosError = error as AxiosError

  if (axiosError.response) {
    // Server responded with error status
    const statusCode = axiosError.response.status
    const message = getErrorMessage(axiosError.response.data, statusCode)
    return new ApiError(message, statusCode, axiosError)
  }

  if (axiosError.request) {
    // Request made but no response
    return new ApiError('No response from server. Please check your connection.', undefined, axiosError)
  }

  // Something else happened
  return new ApiError(
    axiosError.message || 'An unexpected error occurred',
    undefined,
    axiosError
  )
}

function getErrorMessage(data: unknown, statusCode: number): string {
  // Try to extract error message from response data
  if (data && typeof data === 'object') {
    const errorData = data as Record<string, unknown>
    if (errorData.message && typeof errorData.message === 'string') {
      return errorData.message
    }
    if (errorData.detail && typeof errorData.detail === 'string') {
      return errorData.detail
    }
  }

  // Fallback to generic messages based on status code
  switch (statusCode) {
    case 400:
      return 'Bad request. Please check your input.'
    case 401:
      return 'Unauthorized. Please log in again.'
    case 403:
      return 'Access forbidden.'
    case 404:
      return 'Resource not found.'
    case 500:
      return 'Internal server error. Please try again later.'
    case 503:
      return 'Service unavailable. Please try again later.'
    default:
      return `Request failed with status ${statusCode}`
  }
}

export function isNetworkError(error: ApiError): boolean {
  return !error.statusCode && error.originalError?.code === 'ERR_NETWORK'
}

export function isTimeoutError(error: ApiError): boolean {
  return error.originalError?.code === 'ECONNABORTED'
}

export function isServerError(error: ApiError): boolean {
  return !!error.statusCode && error.statusCode >= 500
}

export function isClientError(error: ApiError): boolean {
  return !!error.statusCode && error.statusCode >= 400 && error.statusCode < 500
}
