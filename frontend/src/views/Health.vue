<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface HealthStatus {
  status: string
  app: string
  version: string
}

const backendHealth = ref<HealthStatus | null>(null)
const backendError = ref<string | null>(null)
const loading = ref(true)

const checkBackendHealth = async () => {
  try {
    const response = await fetch('http://localhost:8000/health')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    backendHealth.value = await response.json()
    backendError.value = null
  } catch (error) {
    backendError.value = error instanceof Error ? error.message : 'Unknown error'
    backendHealth.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkBackendHealth()
})
</script>

<template>
  <div class="health-container">
    <h1>Fantasy Football League Analyzer</h1>

    <div class="health-section">
      <h2>Frontend Health</h2>
      <div class="health-card healthy">
        <div class="status-indicator"></div>
        <div class="status-text">
          <p><strong>Status:</strong> Healthy</p>
          <p><strong>Framework:</strong> Vue 3 + Vite + TypeScript</p>
        </div>
      </div>
    </div>

    <div class="health-section">
      <h2>Backend Health</h2>
      <div v-if="loading" class="health-card">
        <p>Checking backend status...</p>
      </div>
      <div v-else-if="backendHealth" class="health-card healthy">
        <div class="status-indicator"></div>
        <div class="status-text">
          <p><strong>Status:</strong> {{ backendHealth.status }}</p>
          <p><strong>App:</strong> {{ backendHealth.app }}</p>
          <p><strong>Version:</strong> {{ backendHealth.version }}</p>
        </div>
      </div>
      <div v-else class="health-card unhealthy">
        <div class="status-indicator"></div>
        <div class="status-text">
          <p><strong>Status:</strong> Unreachable</p>
          <p><strong>Error:</strong> {{ backendError }}</p>
          <p class="hint">Make sure the backend is running on http://localhost:8000</p>
        </div>
      </div>
    </div>

    <div class="actions">
      <button @click="checkBackendHealth" :disabled="loading">
        {{ loading ? 'Checking...' : 'Refresh Backend Status' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.health-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: #42b883;
  text-align: center;
  margin-bottom: 2rem;
}

.health-section {
  margin-bottom: 2rem;
}

h2 {
  color: #35495e;
  margin-bottom: 1rem;
}

.health-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.health-card.healthy {
  border-left: 4px solid #42b883;
}

.health-card.unhealthy {
  border-left: 4px solid #f56c6c;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.healthy .status-indicator {
  background-color: #42b883;
}

.unhealthy .status-indicator {
  background-color: #f56c6c;
}

.status-text p {
  margin: 0.5rem 0;
  color: #2c3e50;
}

.hint {
  font-size: 0.875rem;
  color: #666;
  font-style: italic;
}

.actions {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

button {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #35a372;
}

button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}
</style>
