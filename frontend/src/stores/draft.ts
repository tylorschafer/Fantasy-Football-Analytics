import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '../api/client'
import { useUiStore } from './ui'

export interface DraftPick {
  round: number
  pick: number
  overallPick: number
  teamId: string
  playerId: string
  playerName: string
  position: string
}

export interface DraftPlayer {
  id: string
  name: string
  position: string
  team: string
  byeWeek?: number
  projectedPoints?: number
  adp?: number
  rank?: number
  isAvailable: boolean
  isDrafted: boolean
}

export interface Draft {
  id: string
  leagueId: string
  season: number
  rounds: number
  picks: DraftPick[]
  status: 'not_started' | 'in_progress' | 'completed'
  currentPick?: number
}

export type PositionFilter = 'ALL' | 'QB' | 'RB' | 'WR' | 'TE' | 'K' | 'DEF'

export const useDraftStore = defineStore('draft', () => {
  const uiStore = useUiStore()

  // State
  const currentDraft = ref<Draft | null>(null)
  const availablePlayers = ref<DraftPlayer[]>([])
  const draftedPlayers = ref<DraftPlayer[]>([])
  const searchQuery = ref('')
  const positionFilter = ref<PositionFilter>('ALL')
  const sortBy = ref<'rank' | 'adp' | 'projected_points'>('rank')

  // Computed
  const hasDraft = computed(() => currentDraft.value !== null)

  const filteredPlayers = computed(() => {
    let players = availablePlayers.value

    // Filter by position
    if (positionFilter.value !== 'ALL') {
      players = players.filter((p) => p.position === positionFilter.value)
    }

    // Filter by search query
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase()
      players = players.filter(
        (p) =>
          p.name.toLowerCase().includes(query) ||
          p.team.toLowerCase().includes(query) ||
          p.position.toLowerCase().includes(query)
      )
    }

    // Filter only available players
    players = players.filter((p) => p.isAvailable && !p.isDrafted)

    return players
  })

  const sortedPlayers = computed(() => {
    const players = [...filteredPlayers.value]

    players.sort((a, b) => {
      switch (sortBy.value) {
        case 'rank':
          return (a.rank || Infinity) - (b.rank || Infinity)
        case 'adp':
          return (a.adp || Infinity) - (b.adp || Infinity)
        case 'projected_points':
          return (b.projectedPoints || 0) - (a.projectedPoints || 0)
        default:
          return 0
      }
    })

    return players
  })

  const picksByTeam = computed(() => {
    if (!currentDraft.value) return {}

    const pickMap: Record<string, DraftPick[]> = {}
    const picks = currentDraft.value.picks || []
    picks.forEach((pick) => {
      if (!pickMap[pick.teamId]) {
        pickMap[pick.teamId] = []
      }
      pickMap[pick.teamId]!.push(pick)
    })

    return pickMap
  })

  const currentPickNumber = computed(() => currentDraft.value?.currentPick || 1)

  const totalPicks = computed(() => {
    if (!currentDraft.value) return 0
    return currentDraft.value.rounds * (currentDraft.value.picks.length || 0)
  })

  // Actions
  async function fetchDraft(draftId: string) {
    return uiStore.withLoading('draft:fetch', async () => {
      try {
        const draft = await apiClient.get<Draft>(`/api/v1/drafts/${draftId}`)
        currentDraft.value = draft
        return draft
      } catch (error) {
        uiStore.setError(error as Error)
        throw error
      }
    })
  }

  async function fetchAvailablePlayers(leagueId: string) {
    return uiStore.withLoading('draft:players', async () => {
      try {
        const players = await apiClient.get<DraftPlayer[]>(
          `/api/v1/leagues/${leagueId}/available-players`
        )
        availablePlayers.value = players
        return players
      } catch (error) {
        uiStore.setError(error as Error)
        throw error
      }
    })
  }

  async function draftPlayer(playerId: string, teamId: string) {
    if (!currentDraft.value) {
      throw new Error('No active draft')
    }

    const draftId = currentDraft.value.id

    return uiStore.withLoading('draft:pick', async () => {
      try {
        const pick = await apiClient.post<DraftPick>(`/api/v1/drafts/${draftId}/pick`, {
          playerId,
          teamId,
        })

        // Update local state
        const player = availablePlayers.value.find((p) => p.id === playerId)
        if (player) {
          player.isDrafted = true
          player.isAvailable = false
          draftedPlayers.value.push(player)
        }

        if (currentDraft.value) {
          currentDraft.value.picks.push(pick)
          if (currentDraft.value.currentPick !== undefined) {
            currentDraft.value.currentPick++
          }
        }

        return pick
      } catch (error) {
        uiStore.setError(error as Error)
        throw error
      }
    })
  }

  function setPositionFilter(position: PositionFilter) {
    positionFilter.value = position
  }

  function setSearchQuery(query: string) {
    searchQuery.value = query
  }

  function setSortBy(sort: 'rank' | 'adp' | 'projected_points') {
    sortBy.value = sort
  }

  function clearDraft() {
    currentDraft.value = null
    availablePlayers.value = []
    draftedPlayers.value = []
    searchQuery.value = ''
    positionFilter.value = 'ALL'
  }

  function markPlayerDrafted(playerId: string) {
    const player = availablePlayers.value.find((p) => p.id === playerId)
    if (player) {
      player.isDrafted = true
      player.isAvailable = false
      draftedPlayers.value.push(player)
    }
  }

  return {
    // State
    currentDraft,
    availablePlayers,
    draftedPlayers,
    searchQuery,
    positionFilter,
    sortBy,

    // Computed
    hasDraft,
    filteredPlayers,
    sortedPlayers,
    picksByTeam,
    currentPickNumber,
    totalPicks,

    // Actions
    fetchDraft,
    fetchAvailablePlayers,
    draftPlayer,
    setPositionFilter,
    setSearchQuery,
    setSortBy,
    clearDraft,
    markPlayerDrafted,
  }
})
