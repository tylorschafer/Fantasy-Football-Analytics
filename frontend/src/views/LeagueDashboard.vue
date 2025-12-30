<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useLeagueStore } from '../stores/league'
import { useUiStore } from '../stores/ui'
import LeagueSummaryCard from '../components/LeagueSummaryCard.vue'
import StandingsTable from '../components/StandingsTable.vue'
import QuickStatsGrid from '../components/QuickStatsGrid.vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Message from 'primevue/message'

const router = useRouter()
const leagueStore = useLeagueStore()
const uiStore = useUiStore()

const isLoading = computed(() => uiStore.loadingStates['league:fetch'] || uiStore.loadingStates['league:standings'])
const hasError = computed(() => uiStore.hasError)
const errorMessage = computed(() => uiStore.globalError?.message || 'An error occurred')

// For demo purposes, generate mock data
const mockLeague = ref({
  id: 'demo-league-123',
  name: 'Fantasy Football Champions',
  season: 2024,
  platform: 'sleeper' as const,
  teams: [
    {
      id: '1',
      name: 'Thunder Cats',
      owner: 'Alex Johnson',
      wins: 9,
      losses: 3,
      ties: 0,
      pointsFor: 1425.6,
      pointsAgainst: 1298.4,
    },
    {
      id: '2',
      name: 'Gridiron Gang',
      owner: 'Sarah Miller',
      wins: 8,
      losses: 4,
      ties: 0,
      pointsFor: 1398.2,
      pointsAgainst: 1312.8,
    },
    {
      id: '3',
      name: 'The Eliminators',
      owner: 'Mike Wilson',
      wins: 8,
      losses: 4,
      ties: 0,
      pointsFor: 1375.9,
      pointsAgainst: 1289.5,
    },
    {
      id: '4',
      name: 'Dynasty Warriors',
      owner: 'Emily Davis',
      wins: 7,
      losses: 5,
      ties: 0,
      pointsFor: 1356.4,
      pointsAgainst: 1334.2,
    },
    {
      id: '5',
      name: 'Red Zone Rebels',
      owner: 'Chris Brown',
      wins: 7,
      losses: 5,
      ties: 0,
      pointsFor: 1342.1,
      pointsAgainst: 1345.7,
    },
    {
      id: '6',
      name: 'End Zone Elite',
      owner: 'Jessica Taylor',
      wins: 6,
      losses: 6,
      ties: 0,
      pointsFor: 1328.5,
      pointsAgainst: 1356.9,
    },
    {
      id: '7',
      name: 'Touchdown Titans',
      owner: 'David Martinez',
      wins: 6,
      losses: 6,
      ties: 0,
      pointsFor: 1298.7,
      pointsAgainst: 1342.3,
    },
    {
      id: '8',
      name: 'Blitz Brigade',
      owner: 'Amanda Garcia',
      wins: 5,
      losses: 7,
      ties: 0,
      pointsFor: 1276.3,
      pointsAgainst: 1378.1,
    },
    {
      id: '9',
      name: 'The Fumble Bunch',
      owner: 'Ryan Anderson',
      wins: 4,
      losses: 8,
      ties: 0,
      pointsFor: 1245.8,
      pointsAgainst: 1398.6,
    },
    {
      id: '10',
      name: 'Last Place Legends',
      owner: 'Nicole Thomas',
      wins: 2,
      losses: 10,
      ties: 0,
      pointsFor: 1198.4,
      pointsAgainst: 1456.2,
    },
  ],
  currentWeek: 13,
  totalWeeks: 17,
  scoringType: 'ppr' as const,
})

onMounted(async () => {
  // In a real app, this would fetch actual league data
  // For demo purposes, we'll use mock data
  try {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Set mock data to store
    leagueStore.setCurrentLeague(mockLeague.value)
  } catch (error) {
    console.error('Failed to load league:', error)
    uiStore.setError(error as Error)
  }
})

function handleTeamClick(team: any) {
  console.log('Team clicked:', team)
  // In a real app, navigate to team detail page
  // router.push({ name: 'team-detail', params: { teamId: team.id } })
}

function handleRefresh() {
  // In a real app, refetch data
  console.log('Refreshing league data...')
}
</script>

<template>
  <div class="league-dashboard">
    <!-- Error Message -->
    <Message v-if="hasError && !isLoading" severity="error" :closable="false" class="dashboard-error">
      {{ errorMessage }}
      <template #icon>
        <i class="pi pi-exclamation-triangle"></i>
      </template>
    </Message>

    <!-- Main Dashboard Layout -->
    <div class="dashboard-container">
      <!-- Left Column: Summary + Stats -->
      <div class="dashboard-sidebar">
        <!-- League Summary -->
        <LeagueSummaryCard :league="leagueStore.currentLeague" :loading="isLoading" />

        <!-- Quick Stats Grid -->
        <QuickStatsGrid
          :teams="leagueStore.teams"
          :loading="isLoading"
        />
      </div>

      <!-- Right Column: Standings -->
      <div class="dashboard-main">
        <Card class="standings-card">
          <template #title>
            <div class="standings-header">
              <div class="standings-title">
                <i class="pi pi-trophy"></i>
                <span>League Standings</span>
              </div>
              <Button
                icon="pi pi-refresh"
                text
                rounded
                :loading="isLoading"
                @click="handleRefresh"
                v-tooltip.left="'Refresh'"
              />
            </div>
          </template>
          <template #content>
            <StandingsTable
              :teams="leagueStore.teams"
              :playoff-teams="6"
              :loading="isLoading"
              @team-click="handleTeamClick"
            />
          </template>
        </Card>
      </div>
    </div>

    <!-- Empty State -->
    <Card v-if="!isLoading && !leagueStore.hasLeague && !hasError" class="empty-state">
      <template #content>
        <div class="empty-state-content">
          <i class="pi pi-inbox"></i>
          <h3>No League Selected</h3>
          <p>Connect your fantasy league to view standings and stats</p>
          <Button
            label="Connect League"
            icon="pi pi-link"
            severity="secondary"
            @click="router.push('/')"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.league-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1.5rem;
}

.dashboard-error {
  max-width: 1600px;
  margin: 0 auto 1.5rem;
}

.dashboard-container {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
  align-items: start;
}

/* Left Sidebar */
.dashboard-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  position: sticky;
  top: 1.5rem;
}

/* Right Main Area */
.dashboard-main {
  min-height: calc(100vh - 3rem);
}

.standings-card {
  height: 100%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  overflow: hidden;
}

.standings-card :deep(.p-card-title) {
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.standings-card :deep(.p-card-content) {
  padding: 0;
  max-height: calc(100vh - 12rem);
  overflow-y: auto;
}

.standings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.standings-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.standings-title i {
  color: #f59e0b;
  font-size: 1.5rem;
}

/* Empty State */
.empty-state {
  max-width: 600px;
  margin: 4rem auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
}

.empty-state-content {
  text-align: center;
  padding: 3rem 2rem;
}

.empty-state-content i {
  font-size: 4rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 1.5rem;
}

.empty-state-content h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: white;
}

.empty-state-content p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1.5rem;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .dashboard-container {
    grid-template-columns: 350px 1fr;
  }
}

@media (max-width: 992px) {
  .league-dashboard {
    padding: 1rem;
  }

  .dashboard-container {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .dashboard-sidebar {
    position: static;
  }

  .dashboard-main {
    min-height: auto;
  }

  .standings-card :deep(.p-card-content) {
    max-height: none;
  }
}

@media (max-width: 768px) {
  .league-dashboard {
    padding: 0.75rem;
  }

  .dashboard-container {
    gap: 0.75rem;
  }

  .dashboard-sidebar {
    gap: 0.75rem;
  }

  .standings-title {
    font-size: 1.1rem;
  }

  .standings-title i {
    font-size: 1.25rem;
  }
}

/* Custom Scrollbar */
.standings-card :deep(.p-card-content)::-webkit-scrollbar {
  width: 8px;
}

.standings-card :deep(.p-card-content)::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.standings-card :deep(.p-card-content)::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 4px;
}

.standings-card :deep(.p-card-content)::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}
</style>
