<script setup lang="ts">
import { computed } from 'vue'
import Card from 'primevue/card'
import type { Team } from '../stores/league'

interface Props {
  teams: Team[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

interface QuickStat {
  icon: string
  label: string
  value: string
  subtext: string
  color: string
}

const quickStats = computed<QuickStat[]>(() => {
  if (props.teams.length === 0) {
    return []
  }

  // Calculate stats
  const highestScore = Math.max(...props.teams.map((t) => t.pointsFor))
  const lowestScore = Math.min(...props.teams.map((t) => t.pointsFor))

  const highestScoringTeam = props.teams.find((t) => t.pointsFor === highestScore)
  const lowestScoringTeam = props.teams.find((t) => t.pointsFor === lowestScore)

  // Calculate biggest blowout (simplified - in real app, would look at individual matchups)
  const pointDiffs = props.teams.map((t) => Math.abs(t.pointsFor - t.pointsAgainst))
  const biggestBlowout = Math.max(...pointDiffs)
  const blowoutTeam = props.teams[pointDiffs.indexOf(biggestBlowout)]

  // Most transactions (placeholder - would come from API)
  const mostActiveTeam = props.teams[Math.floor(Math.random() * props.teams.length)]

  return [
    {
      icon: 'pi-chart-line',
      label: 'Highest Scoring',
      value: highestScore.toFixed(1),
      subtext: highestScoringTeam?.name || '',
      color: 'text-green-500',
    },
    {
      icon: 'pi-chart-bar',
      label: 'Lowest Scoring',
      value: lowestScore.toFixed(1),
      subtext: lowestScoringTeam?.name || '',
      color: 'text-orange-500',
    },
    {
      icon: 'pi-bolt',
      label: 'Biggest Blowout',
      value: `${biggestBlowout.toFixed(1)} pts`,
      subtext: blowoutTeam?.name || '',
      color: 'text-purple-500',
    },
    {
      icon: 'pi-sync',
      label: 'Most Active',
      value: `${Math.floor(Math.random() * 30 + 10)}`,
      subtext: mostActiveTeam?.name || '',
      color: 'text-blue-500',
    },
  ]
})
</script>

<template>
  <div class="quick-stats-grid">
    <Card v-for="(_stat, index) in loading ? 4 : quickStats.length" :key="index" class="stat-card">
      <template #content>
        <div v-if="loading" class="stat-content">
          <div class="stat-icon-wrapper">
            <div class="stat-icon-skeleton"></div>
          </div>
          <div class="stat-details">
            <div class="stat-label-skeleton"></div>
            <div class="stat-value-skeleton"></div>
            <div class="stat-subtext-skeleton"></div>
          </div>
        </div>

        <div v-else-if="quickStats[index]" class="stat-content">
          <div class="stat-icon-wrapper" :class="`bg-${quickStats[index].color.split('-')[1]}`">
            <i :class="`pi ${quickStats[index].icon} ${quickStats[index].color}`"></i>
          </div>
          <div class="stat-details">
            <span class="stat-label">{{ quickStats[index].label }}</span>
            <div class="stat-value">{{ quickStats[index].value }}</div>
            <div class="stat-subtext">{{ quickStats[index].subtext }}</div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.quick-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.stat-card :deep(.p-card-content) {
  padding: 1rem;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-icon-wrapper.bg-green {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-icon-wrapper.bg-orange {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
}

.stat-icon-wrapper.bg-purple {
  background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%);
}

.stat-icon-wrapper.bg-blue {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-icon-wrapper i {
  color: white;
}

.stat-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  line-height: 1;
}

.stat-subtext {
  font-size: 0.875rem;
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Loading Skeletons */
.stat-icon-skeleton {
  width: 48px;
  height: 48px;
  background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 50%, #f3f4f6 100%);
  background-size: 200% 100%;
  animation: skeleton 1.5s ease-in-out infinite;
  border-radius: 12px;
}

.stat-label-skeleton {
  height: 12px;
  width: 60%;
  background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 50%, #f3f4f6 100%);
  background-size: 200% 100%;
  animation: skeleton 1.5s ease-in-out infinite;
  border-radius: 4px;
}

.stat-value-skeleton {
  height: 24px;
  width: 50%;
  background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 50%, #f3f4f6 100%);
  background-size: 200% 100%;
  animation: skeleton 1.5s ease-in-out infinite;
  border-radius: 4px;
}

.stat-subtext-skeleton {
  height: 14px;
  width: 80%;
  background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 50%, #f3f4f6 100%);
  background-size: 200% 100%;
  animation: skeleton 1.5s ease-in-out infinite;
  border-radius: 4px;
}

@keyframes skeleton {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Responsive */
@media (max-width: 992px) {
  .quick-stats-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .quick-stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
}

@media (max-width: 480px) {
  .quick-stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
