<script setup lang="ts">
import { computed } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import type { Team } from '../stores/league'

interface Props {
  teams: Team[]
  playoffTeams?: number
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  playoffTeams: 6,
  loading: false,
})

const emit = defineEmits<{
  teamClick: [team: Team]
}>()

interface StandingsRow extends Team {
  rank: number
  winPct: number
  pointDiff: number
  streak: string
}

const standingsData = computed<StandingsRow[]>(() => {
  // Sort teams by wins (desc), then by points for (desc)
  const sorted = [...props.teams].sort((a, b) => {
    if (a.wins !== b.wins) {
      return b.wins - a.wins
    }
    return b.pointsFor - a.pointsFor
  })

  // Calculate additional stats
  return sorted.map((team, index) => {
    const totalGames = team.wins + team.losses + team.ties
    const winPct = totalGames > 0 ? team.wins / totalGames : 0

    return {
      ...team,
      rank: index + 1,
      winPct,
      pointDiff: team.pointsFor - team.pointsAgainst,
      streak: calculateStreak(team),
    }
  })
})

function calculateStreak(_team: Team): string {
  // This is a placeholder - in a real app, you'd calculate from recent games
  // Returning a static value to avoid reactive loops
  return '-'
}

function isPlayoffTeam(rank: number): boolean {
  return rank <= props.playoffTeams
}

function onRowClick(event: { data: StandingsRow }) {
  emit('teamClick', event.data)
}

function formatRecord(team: StandingsRow): string {
  if (team.ties > 0) {
    return `${team.wins}-${team.losses}-${team.ties}`
  }
  return `${team.wins}-${team.losses}`
}

// Loading skeleton data
const skeletonData = Array.from({ length: 10 }, (_, i) => ({
  id: `skeleton-${i}`,
  rank: i + 1,
}))
</script>

<template>
  <DataTable
    :value="loading ? skeletonData : standingsData"
    :rows="20"
    striped-rows
    :row-hover="!loading"
    responsive-layout="scroll"
    class="standings-table"
    @row-click="onRowClick"
  >
    <!-- Rank Column -->
    <Column field="rank" header="Rank" :sortable="!loading" style="width: 80px">
      <template #body="{ data }">
        <div v-if="loading" class="h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        <div v-else class="flex items-center gap-2">
          <span class="font-semibold">{{ data.rank }}</span>
          <i
            v-if="isPlayoffTeam(data.rank)"
            class="pi pi-star-fill text-yellow-500"
            v-tooltip.top="'Playoff Position'"
          ></i>
        </div>
      </template>
    </Column>

    <!-- Team Column -->
    <Column field="name" header="Team" :sortable="!loading">
      <template #body="{ data }">
        <div v-if="loading" class="space-y-1">
          <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-3/4"></div>
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-1/2"></div>
        </div>
        <div v-else>
          <div class="font-semibold">{{ data.name }}</div>
          <div class="text-sm text-gray-500 dark:text-gray-400">{{ data.ownerName }}</div>
        </div>
      </template>
    </Column>

    <!-- Record Column -->
    <Column field="wins" header="Record" :sortable="!loading" style="width: 120px">
      <template #body="{ data }">
        <div v-if="loading" class="h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        <div v-else class="font-medium">
          {{ formatRecord(data) }}
        </div>
      </template>
    </Column>

    <!-- Win % Column -->
    <Column field="winPct" header="Win %" :sortable="!loading" style="width: 100px">
      <template #body="{ data }">
        <div v-if="loading" class="h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        <span v-else>{{ (data.winPct * 100).toFixed(1) }}%</span>
      </template>
    </Column>

    <!-- Points For Column -->
    <Column field="pointsFor" header="PF" :sortable="!loading" style="width: 100px">
      <template #body="{ data }">
        <div v-if="loading" class="h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        <span v-else class="font-medium">{{ data.pointsFor.toFixed(1) }}</span>
      </template>
    </Column>

    <!-- Points Against Column -->
    <Column field="pointsAgainst" header="PA" :sortable="!loading" style="width: 100px">
      <template #body="{ data }">
        <div v-if="loading" class="h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        <span v-else>{{ data.pointsAgainst.toFixed(1) }}</span>
      </template>
    </Column>

    <!-- Point Differential Column -->
    <Column field="pointDiff" header="Diff" :sortable="!loading" style="width: 100px">
      <template #body="{ data }">
        <div v-if="loading" class="h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        <span
          v-else
          :class="{
            'text-green-600 dark:text-green-400': data.pointDiff > 0,
            'text-red-600 dark:text-red-400': data.pointDiff < 0,
          }"
        >
          {{ data.pointDiff > 0 ? '+' : '' }}{{ data.pointDiff.toFixed(1) }}
        </span>
      </template>
    </Column>

    <!-- Streak Column -->
    <Column field="streak" header="Streak" :sortable="!loading" style="width: 100px">
      <template #body="{ data }">
        <div v-if="loading" class="h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
        <Tag
          v-else-if="data.streak.startsWith('W')"
          :value="data.streak"
          severity="success"
          rounded
        />
        <Tag
          v-else-if="data.streak.startsWith('L')"
          :value="data.streak"
          severity="danger"
          rounded
        />
        <span v-else class="text-gray-400">-</span>
      </template>
    </Column>

    <!-- Empty State -->
    <template #empty>
      <div class="text-center py-8 text-gray-500 dark:text-gray-400">
        <i class="pi pi-inbox text-4xl mb-2"></i>
        <p>No standings data available</p>
      </div>
    </template>
  </DataTable>
</template>

<style scoped>
.standings-table {
  border-radius: 8px;
  overflow: hidden;
}

.standings-table :deep(.p-datatable-tbody > tr) {
  cursor: pointer;
  transition: background-color 0.2s;
}

.standings-table :deep(.p-datatable-tbody > tr:hover) {
  background-color: rgba(0, 0, 0, 0.02);
}

.standings-table :deep(.p-datatable-tbody > tr.p-highlight) {
  background-color: rgba(59, 130, 246, 0.1);
}
</style>
