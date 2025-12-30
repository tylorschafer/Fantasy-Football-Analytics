import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '../api/client'
import { useUiStore } from './ui'

export interface Team {
  id: string
  name: string
  owner: string
  wins: number
  losses: number
  ties: number
  pointsFor: number
  pointsAgainst: number
  roster?: Player[]
}

export interface Player {
  id: string
  name: string
  position: string
  team: string
  status?: 'active' | 'injured' | 'bye'
}

export interface Standings {
  teamId: string
  rank: number
  wins: number
  losses: number
  ties: number
  pointsFor: number
  pointsAgainst: number
  winPercentage: number
}

export interface League {
  id: string
  name: string
  season: number
  platform: 'espn' | 'sleeper' | 'yahoo'
  teams: Team[]
  currentWeek: number
  totalWeeks: number
  scoringType: 'standard' | 'ppr' | 'half_ppr'
}

export const useLeagueStore = defineStore('league', () => {
  const uiStore = useUiStore()

  // State
  const currentLeague = ref<League | null>(null)
  const teams = ref<Team[]>([])
  const standings = ref<Standings[]>([])
  const userTeam = ref<Team | null>(null)

  // Computed
  const hasLeague = computed(() => currentLeague.value !== null)

  const sortedStandings = computed(() => {
    return [...standings.value].sort((a, b) => a.rank - b.rank)
  })

  const leagueTeamCount = computed(() => teams.value.length)

  const currentWeek = computed(() => currentLeague.value?.currentWeek || 1)

  const userTeamStanding = computed(() => {
    if (!userTeam.value) return null
    return standings.value.find((s) => s.teamId === userTeam.value!.id) || null
  })

  // Actions
  async function fetchLeague(leagueId: string) {
    return uiStore.withLoading('league:fetch', async () => {
      try {
        const league = await apiClient.get<League>(`/api/v1/leagues/${leagueId}`)
        currentLeague.value = league
        teams.value = league.teams
        return league
      } catch (error) {
        uiStore.setError(error as Error)
        throw error
      }
    })
  }

  async function fetchStandings(leagueId?: string) {
    const targetLeagueId = leagueId || currentLeague.value?.id
    if (!targetLeagueId) {
      throw new Error('No league ID available')
    }

    return uiStore.withLoading('league:standings', async () => {
      try {
        const standingsData = await apiClient.get<Standings[]>(
          `/api/v1/leagues/${targetLeagueId}/standings`
        )
        standings.value = standingsData
        return standingsData
      } catch (error) {
        uiStore.setError(error as Error)
        throw error
      }
    })
  }

  async function fetchTeam(teamId: string) {
    return uiStore.withLoading('league:team', async () => {
      try {
        const team = await apiClient.get<Team>(`/api/v1/teams/${teamId}`)
        const index = teams.value.findIndex((t) => t.id === teamId)
        if (index !== -1) {
          teams.value[index] = team
        } else {
          teams.value.push(team)
        }
        return team
      } catch (error) {
        uiStore.setError(error as Error)
        throw error
      }
    })
  }

  function setCurrentLeague(league: League) {
    currentLeague.value = league
    teams.value = league.teams
  }

  function setUserTeam(team: Team) {
    userTeam.value = team
  }

  function clearLeague() {
    currentLeague.value = null
    teams.value = []
    standings.value = []
    userTeam.value = null
  }

  function updateTeamInList(updatedTeam: Team) {
    const index = teams.value.findIndex((t) => t.id === updatedTeam.id)
    if (index !== -1) {
      teams.value[index] = updatedTeam
    }
  }

  return {
    // State
    currentLeague,
    teams,
    standings,
    userTeam,

    // Computed
    hasLeague,
    sortedStandings,
    leagueTeamCount,
    currentWeek,
    userTeamStanding,

    // Actions
    fetchLeague,
    fetchStandings,
    fetchTeam,
    setCurrentLeague,
    setUserTeam,
    clearLeague,
    updateTeamInList,
  }
})
