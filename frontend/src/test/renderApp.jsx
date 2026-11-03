import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider, createMemoryRouter } from 'react-router'
import { render, screen } from '@testing-library/react'
import '../i18n'
import { wireApi } from '../api/wiring'
import { routes } from '../routes/routes'
import { useAuth } from '../stores/authStore'

wireApi()
import { findUserByEmail, issueSession } from '../mocks/db'

/**
 * Сессия под мок-моделью: токены реально выпущены issueSession, поэтому
 * GET /api/trips не отвечает 401 на подделанный access.
 */
export function demoSession() {
  const user = findUserByEmail('demo@trip.pl')
  const { access, refresh } = issueSession(user.id)
  return { access, refresh, user: { id: user.id, name: user.name, email: user.email } }
}

/**
 * Рендер приложения под память-роутером для любого нужного пути.
 */
export function renderApp(path = '/', { auth = null } = {}) {
  if (auth) useAuth.setState(auth)
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
  })
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  return render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  )
}

export { screen }
