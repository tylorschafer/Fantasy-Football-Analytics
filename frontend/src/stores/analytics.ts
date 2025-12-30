import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '../api/client'
import { useUiStore } from './ui'

export interface MatchupAnalysis {
  week: number
  teamId: string
  opponentId: string
  projectedScore: number
  opponentProjectedScore: number
  winProbability: number
  keyPlayers: string[]
  advice: string[]
}

export interface PlayerPerformance {
  playerId: string
  playerName: string
  position: string
  averagePoints: number
  totalPoints: number
  gamesPlayed: number
  consistency: number
  weeklyScores: number[]
  trend: 'up' | 'down' | 'stable'
}

export interface TeamStrength {
  teamId: string
  teamName: string
  overallRating: number
  offensiveRating: number
  defensiveRating: number
  rosterDepth: number
  positionStrengths: Record<string, number>
  weaknesses: string[]
}

export interface PowerRanking {
  teamId: string
  teamName: string
  rank: number
  powerScore: number
  weeklyChange: number
  strengthOfSchedule: number
}

export interface TradeAnalysis {
  tradeId: string
  givingPlayers: string[]
  receivingPlayers: string
  fairnessScore: number
  recommendation: 'accept' | 'decline' | 'consider'
  reasoning: string[]
  projectedImpact: number
}

export const useAnalyticsStore = defineStore('analytics', () => {
  const uiStore = useUiStore()

  // State
  const matchupAnalyses = ref<MatchupAnalysis[]>([])
  const playerPerformances = ref<PlayerPerformance[]>([])
  const teamStrengths = ref<TeamStrength[]>([])
  const powerRankings = ref<PowerRanking[]>([])
  const tradeAnalyses = ref<TradeAnalysis[]>([])
  const selectedWeek = ref<number>(1)

  // Computed
  const currentWeekMatchup = computed(() => {
    return matchupAnalyses.value.find((m) => m.week === selectedWeek.value) || null
  })

  const topPerformers = computed(() => {
    return [...playerPerformances.value]
      .sort((a, b) => b.averagePoints - a.averagePoints)
      .slice(0, 10)
  })

  const worstPerformers = computed(() => {
    return [...playerPerformances.value]
      .sort((a, b) => a.averagePoints - b.averagePoints)
      .slice(0, 10)
  })

  const mostConsistentPlayers = computed(() => {
    return [...playerPerformances.value]
      .sort((a, b) => b.consistency - a.consistency)
      .slice(0, 10)
  })

  const sortedPowerRankings = computed(() => {
    return [...powerRankings.value].sort((a, b) => a.rank - b.rank)
  })

  const recommendedTrades = computed(() => {
    return tradeAnalyses.value.filter((t) => t.recommendation === 'accept')
  })

  // Actions
  async function fetchMatchupAnalysis(teamId: string, week: number) {
    return uiStore.withLoading('analytics:matchup', async () => {
      try {
        const analysis = await apiClient.get<MatchupAnalysis>(
          `/api/v1/analytics/matchup/${teamId}/${week}`
        )

        const index = matchupAnalyses.value.findIndex((m) => m.week === week && m.teamId === teamId)
        if (index !== -1) {
          matchupAnalyses.value[index] = analysis
        } else {
          matchupAnalyses.value.push(analysis)
        }

        return analysis
      } catch (error) {
        uiStore.setError(error as Error)
        throw error
      }
    })
  }

  async function fetchPlayerPerformances(leagueId: string, teamId?: string) {
    return uiStore.withLoading('analytics:players', async () => {
      try {
        const endpoint = teamId
          ? `/api/v1/analytics/players/${leagueId}?teamId=${teamId}`
          : `/api/v1/analytics/players/${leagueId}`

        const performances = await apiClient.get<PlayerPerformance[]>(endpoint)
        playerPerformances.value = performances
        return performances
      } catch (error) {
        uiStore.setError(error as Error)
        throw error
      }
    })
  }

  async function fetchTeamStrengths(leagueId: string) {
    return uiStore.withLoading('analytics:teams', async () => {
      try {
        const strengths = await apiClient.get<TeamStrength[]>(
          `/api/v1/analytics/team-strengths/${leagueId}`
        )
        teamStrengths.value = strengths
        return strengths
      } catch (error) {
        uiStore.setError(error as Error)
        throw error
      }
    })
  }

  async function fetchPowerRankings(leagueId: string) {
    return uiStore.withLoading('analytics:rankings', async () => {
      try {
        const rankings = await apiClient.get<PowerRanking[]>(
          `/api/v1/analytics/power-rankings/${leagueId}`
        )
        powerRankings.value = rankings
        return rankings
      } catch (error) {
        uiStore.setError(error as Error)
        throw error
      }
    })
  }

  async function analyzeTrade(
    leagueId: string,
    givingPlayerIds: string[],
    receivingPlayerIds: string[]
  ) {
    return uiStore.withLoading('analytics:trade', async () => {
      try {
        const analysis = await apiClient.post<TradeAnalysis>(
          `/api/v1/analytics/trade/${leagueId}`,
          {
            givingPlayers: givingPlayerIds,
            receivingPlayers: receivingPlayerIds,
          }
        )

        tradeAnalyses.value.push(analysis)
        return analysis
      } catch (error) {
        uiStore.setError(error as Error)
        throw error
      }
    })
  }

  function setSelectedWeek(week: number) {
    selectedWeek.value = week
  }

  function clearAnalytics() {
    matchupAnalyses.value = []
    playerPerformances.value = []
    teamStrengths.value = []
    powerRankings.value = []
    tradeAnalyses.value = []
    selectedWeek.value = 1
  }

  function getPlayerPerformance(playerId: string): PlayerPerformance | null {
    return playerPerformances.value.find((p) => p.playerId === playerId) || null
  }

  function getTeamStrength(teamId: string): TeamStrength | null {
    return teamStrengths.value.find((t) => t.teamId === teamId) || null
  }

  function getPowerRanking(teamId: string): PowerRanking | null {
    return powerRankings.value.find((r) => r.teamId === teamId) || null
  }

  return {
    // State
    matchupAnalyses,
    playerPerformances,
    teamStrengths,
    powerRankings,
    tradeAnalyses,
    selectedWeek,

    // Computed
    currentWeekMatchup,
    topPerformers,
    worstPerformers,
    mostConsistentPlayers,
    sortedPowerRankings,
    recommendedTrades,

    // Actions
    fetchMatchupAnalysis,
    fetchPlayerPerformances,
    fetchTeamStrengths,
    fetchPowerRankings,
    analyzeTrade,
    setSelectedWeek,
    clearAnalytics,
    getPlayerPerformance,
    getTeamStrength,
    getPowerRanking,
  }
})
