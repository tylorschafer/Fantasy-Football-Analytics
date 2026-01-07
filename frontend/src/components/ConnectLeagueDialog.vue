<script setup lang="ts">
import { ref, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import { apiClient } from '../api/client'
import type { League } from '../stores/league'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'league-connected': [league: League]
}>()

const leagueId = ref('')
const season = ref(2024)
const loading = ref(false)
const error = ref<string | null>(null)

const isValid = computed(() => {
  return leagueId.value.trim().length > 0 && season.value >= 2020 && season.value <= 2025
})

async function handleConnect() {
  if (!isValid.value) return

  loading.value = true
  error.value = null

  // Add a 45 second timeout
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => reject(new Error('Connection timeout - request took too long')), 45000)
  })

  try {
    console.log('Connecting to league:', {
      platform: 'sleeper',
      league_id: leagueId.value.trim(),
      season: season.value,
    })

    const response = await Promise.race([
      apiClient.post<{ league: League }>('/api/v1/leagues/connect', {
        platform: 'sleeper',
        league_id: leagueId.value.trim(),
        season: season.value,
      }),
      timeoutPromise,
    ]) as { league: League }

    console.log('API Response:', response)

    if (!response || !response.league) {
      throw new Error('Invalid response format from server')
    }

    console.log('League data received:', response.league)
    emit('league-connected', response.league)
    emit('update:visible', false)

    // Reset form
    leagueId.value = ''
    season.value = 2024
  } catch (err: any) {
    console.error('Connection error:', err)
    console.error('Error response:', err.response)

    if (err.message && err.message.includes('timeout')) {
      error.value = 'Connection timed out. Please try again.'
    } else if (err.response?.status === 404) {
      error.value = 'League not found. Please check your League ID and try again.'
    } else if (err.response?.status === 400) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'object' && detail?.error) {
        error.value = detail.error
      } else {
        error.value = 'Invalid request. Please check your inputs.'
      }
    } else if (err.message) {
      error.value = err.message
    } else {
      error.value = err.response?.data?.detail || 'Failed to connect to league. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

function handleClose() {
  emit('update:visible', false)
  error.value = null
}
</script>

<template>
  <Dialog
    :visible="props.visible"
    modal
    header="Connect Sleeper League"
    :style="{ width: '500px' }"
    @update:visible="handleClose"
  >
    <div class="dialog-content">
      <p class="description">
        Enter your Sleeper league ID to connect and view your league data.
      </p>

      <Message v-if="error" severity="error" :closable="false" class="error-message">
        {{ error }}
      </Message>

      <div v-if="loading" class="loading-indicator">
        <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
        <p>Connecting to Sleeper and fetching league data...</p>
        <small>This may take a few seconds</small>
      </div>

      <div v-else class="form-field">
        <label for="league-id">League ID</label>
        <InputText
          id="league-id"
          v-model="leagueId"
          placeholder="e.g., 123456789"
          class="w-full"
          :disabled="loading"
          @keyup.enter="handleConnect"
        />
        <small class="help-text">
          Find this in your league URL: sleeper.com/leagues/<strong>123456789</strong>
        </small>
      </div>

      <div v-if="!loading" class="form-field">
        <label for="season">Season</label>
        <InputNumber
          id="season"
          v-model="season"
          :min="2020"
          :max="2025"
          :use-grouping="false"
          class="w-full"
          :disabled="loading"
        />
      </div>

      <div class="actions">
        <Button
          label="Cancel"
          severity="secondary"
          text
          @click="handleClose"
          :disabled="loading"
        />
        <Button
          label="Connect League"
          icon="pi pi-link"
          @click="handleConnect"
          :loading="loading"
          :disabled="!isValid"
        />
      </div>
    </div>
  </Dialog>
</template>

<style scoped>
.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.description {
  color: #6b7280;
  margin: 0;
  line-height: 1.5;
}

.error-message {
  margin: 0;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
  text-align: center;
}

.loading-indicator i {
  color: #667eea;
}

.loading-indicator p {
  margin: 0;
  font-weight: 600;
  color: #374151;
}

.loading-indicator small {
  color: #6b7280;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.help-text {
  color: #6b7280;
  font-size: 0.75rem;
  line-height: 1.4;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}
</style>
