import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { vi } from 'vitest'
import Dashboard from '../pages/Dashboard'
import * as api from '../services/api'

// Mock the API module
vi.mock('../services/api', () => ({
  fetchRecentStudySession: vi.fn(),
  fetchStudyStats: vi.fn()
}))

describe('Dashboard', () => {
  const mockStats = {
    total_vocabulary: 100,
    total_words_studied: 50,
    mastered_words: 20,
    success_rate: 0.75,
    total_sessions: 10,
    active_groups: 3,
    current_streak: 5
  }

  const mockSession = {
    id: 1,
    group_id: 1,
    activity_name: "Basic Vocabulary",
    created_at: "2024-01-01T10:00:00",
    correct_count: 8,
    wrong_count: 2
  }

  beforeEach(() => {
    // Reset mocks before each test
    vi.resetAllMocks()
  })

  test('renders dashboard with stats and recent session', async () => {
    // Mock successful API responses
    vi.mocked(api.fetchStudyStats).mockResolvedValue(mockStats)
    vi.mocked(api.fetchRecentStudySession).mockResolvedValue(mockSession)

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )

    // Check loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument()

    // Wait for data to load and verify stats
    await waitFor(() => {
      expect(screen.getByText('75%')).toBeInTheDocument() // Success rate
      expect(screen.getByText('10')).toBeInTheDocument() // Total sessions
      expect(screen.getByText('3')).toBeInTheDocument() // Active groups
      expect(screen.getByText('5 days')).toBeInTheDocument() // Streak
    })

    // Verify recent session info
    expect(screen.getByText('Basic Vocabulary')).toBeInTheDocument()
    expect(screen.getByText('8 correct')).toBeInTheDocument()
    expect(screen.getByText('2 wrong')).toBeInTheDocument()
  })

  test('handles empty stats gracefully', async () => {
    // Mock empty stats
    const emptyStats = {
      total_vocabulary: 0,
      total_words_studied: 0,
      mastered_words: 0,
      success_rate: 0,
      total_sessions: 0,
      active_groups: 0,
      current_streak: 0
    }

    vi.mocked(api.fetchStudyStats).mockResolvedValue(emptyStats)
    vi.mocked(api.fetchRecentStudySession).mockResolvedValue(null)

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByText(/no sessions yet/i)).toBeInTheDocument()
      expect(screen.getByText(/start studying to see your progress/i)).toBeInTheDocument()
    })
  })

  test('handles API errors', async () => {
    // Mock API error
    vi.mocked(api.fetchStudyStats).mockRejectedValue(new Error('Failed to fetch'))
    vi.mocked(api.fetchRecentStudySession).mockRejectedValue(new Error('Failed to fetch'))

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )

    // Verify error handling UI
    await waitFor(() => {
      expect(screen.getByText(/failed to load dashboard data/i)).toBeInTheDocument()
    })
  })

  test('displays correct progress percentage', async () => {
    const statsWithProgress = {
      ...mockStats,
      total_vocabulary: 200,
      mastered_words: 50
    }

    vi.mocked(api.fetchStudyStats).mockResolvedValue(statsWithProgress)
    vi.mocked(api.fetchRecentStudySession).mockResolvedValue(mockSession)

    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )

    await waitFor(() => {
      // Should show 25% (50/200)
      expect(screen.getByText('25%')).toBeInTheDocument()
    })
  })
}) 