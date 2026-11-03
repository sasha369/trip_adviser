import '@testing-library/jest-dom/vitest'
import { afterEach } from 'vitest'
import { server } from '../mocks/server'
import { resetDb } from '../mocks/db'
import { useAuth } from '../stores/authStore'

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))

beforeEach(() => {
  resetDb({ withDemoUser: true })
})

afterEach(() => {
  server.resetHandlers()
  useAuth.setState({ access: null, refresh: null, user: null })
  localStorage.clear()
})

afterAll(() => server.close())
