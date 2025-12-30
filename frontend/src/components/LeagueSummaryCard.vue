<script setup lang="ts">
import { computed } from 'vue'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import type { League } from '../stores/league'

interface Props {
  league: League | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const platformLogo = computed(() => {
  const logos: Record<string, string> = {
    sleeper: '🛏️',
    espn: '📺',
    yahoo: '🟣',
  }
  return props.league ? logos[props.league.platform] || '🏈' : '🏈'
})

const scoringTypeLabel = computed(() => {
  const labels: Record<string, string> = {
    ppr: 'PPR',
    half_ppr: 'Half PPR',
    standard: 'Standard',
  }
  return props.league ? labels[props.league.scoringType] || 'Unknown' : ''
})

const playoffStatus = computed(() => {
  if (!props.league) return ''

  const { currentWeek, totalWeeks } = props.league
  const regularSeasonWeeks = totalWeeks - 4 // Assuming 4 playoff weeks

  if (currentWeek <= regularSeasonWeeks) {
    return `Week ${currentWeek} of ${regularSeasonWeeks}`
  } else {
    return 'Playoffs'
  }
})

const isPlayoffs = computed(() => {
  if (!props.league) return false
  const regularSeasonWeeks = props.league.totalWeeks - 4
  return props.league.currentWeek > regularSeasonWeeks
})
</script>

<template>
  <Card class="league-summary-card">
    <template #content>
      <div v-if="loading" class="summary-loading">
        <div class="logo-skeleton"></div>
        <div class="info-skeleton">
          <div class="title-skeleton"></div>
          <div class="stats-skeleton">
            <div class="stat-skeleton"></div>
            <div class="stat-skeleton"></div>
          </div>
        </div>
      </div>

      <div v-else-if="league" class="summary-content">
        <!-- Platform Badge -->
        <div class="platform-badge" :title="league.platform">
          <span class="platform-logo">{{ platformLogo }}</span>
          <Tag
            v-if="isPlayoffs"
            severity="success"
            value="Playoffs"
            icon="pi pi-trophy"
            rounded
            class="playoff-tag"
          />
        </div>

        <!-- League Info -->
        <div class="league-info">
          <h2 class="league-name">{{ league.name }}</h2>

          <div class="league-stats">
            <div class="stat-item">
              <i class="pi pi-calendar"></i>
              <span>{{ league.season }}</span>
            </div>

            <div class="stat-item">
              <i class="pi pi-chart-bar"></i>
              <span>{{ scoringTypeLabel }}</span>
            </div>

            <div class="stat-item">
              <i class="pi pi-users"></i>
              <span>{{ league.teams.length }} Teams</span>
            </div>

            <div class="stat-item highlight">
              <i class="pi pi-clock"></i>
              <span>{{ playoffStatus }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <i class="pi pi-inbox"></i>
        <p>No league selected</p>
      </div>
    </template>
  </Card>
</template>

<style scoped>
.league-summary-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.league-summary-card :deep(.p-card-content) {
  padding: 1.5rem;
}

/* Loading State */
.summary-loading {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-skeleton {
  width: 56px;
  height: 56px;
  background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 50%, #f3f4f6 100%);
  background-size: 200% 100%;
  animation: skeleton 1.5s ease-in-out infinite;
  border-radius: 12px;
}

.info-skeleton {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.title-skeleton {
  height: 24px;
  width: 80%;
  background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 50%, #f3f4f6 100%);
  background-size: 200% 100%;
  animation: skeleton 1.5s ease-in-out infinite;
  border-radius: 4px;
}

.stats-skeleton {
  display: flex;
  gap: 0.5rem;
}

.stat-skeleton {
  height: 16px;
  width: 60px;
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

/* Content */
.summary-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.platform-badge {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.platform-logo {
  font-size: 2.5rem;
  line-height: 1;
}

.playoff-tag {
  font-size: 0.75rem;
}

.league-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.league-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  line-height: 1.3;
  margin: 0;
}

.league-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #4b5563;
  transition: all 0.2s ease;
}

.stat-item i {
  color: #9ca3af;
  font-size: 0.875rem;
}

.stat-item.highlight {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #667eea;
  font-weight: 600;
}

.stat-item.highlight i {
  color: #667eea;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: #9ca3af;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 0.75rem;
  display: block;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

/* Responsive */
@media (max-width: 992px) {
  .league-stats {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .league-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
