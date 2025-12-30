<template>
  <div class="sample-primevue">
    <Card>
      <template #title>PrimeVue Component Demo</template>
      <template #content>
        <div class="form-demo">
          <div class="field">
            <label for="username">Username</label>
            <InputText id="username" v-model="username" placeholder="Enter username" />
          </div>

          <div class="field">
            <label for="position">Position</label>
            <Dropdown
              id="position"
              v-model="selectedPosition"
              :options="positions"
              option-label="name"
              placeholder="Select a Position"
            />
          </div>

          <Button label="Show Toast" icon="pi pi-check" @click="showSuccess" />
        </div>

        <DataTable :value="samplePlayers" class="mt-4">
          <Column field="name" header="Name"></Column>
          <Column field="position" header="Position"></Column>
          <Column field="team" header="Team"></Column>
          <Column field="points" header="Points"></Column>
        </DataTable>
      </template>
    </Card>

    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Toast from 'primevue/toast'

const toast = useToast()
const username = ref('')
const selectedPosition = ref()

const positions = [
  { name: 'QB', code: 'QB' },
  { name: 'RB', code: 'RB' },
  { name: 'WR', code: 'WR' },
  { name: 'TE', code: 'TE' },
]

const samplePlayers = [
  { name: 'Patrick Mahomes', position: 'QB', team: 'KC', points: 324 },
  { name: 'Christian McCaffrey', position: 'RB', team: 'SF', points: 298 },
  { name: 'Tyreek Hill', position: 'WR', team: 'MIA', points: 276 },
  { name: 'Travis Kelce', position: 'TE', team: 'KC', points: 245 },
]

const showSuccess = () => {
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: 'PrimeVue Toast is working!',
    life: 3000,
  })
}
</script>

<style scoped>
.sample-primevue {
  padding: 2rem;
}

.form-demo {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mt-4 {
  margin-top: 1.5rem;
}
</style>
