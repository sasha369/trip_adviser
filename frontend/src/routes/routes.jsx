import { RequireAuth, RequireGuest } from './guards'
import { LoginPage } from '../pages/auth/LoginPage'
import { RegisterPage } from '../pages/auth/RegisterPage'
import { ResetRequestPage } from '../pages/auth/ResetRequestPage'
import { ResetConfirmPage } from '../pages/auth/ResetConfirmPage'
import { HomePage } from '../pages/HomePage'
import { NotFoundPage } from '../pages/NotFoundPage'

/**
 * Роутинг по design §2: гость видит только S1-страницы, владелец — S2+.
 * Плоские guard-маршруты без дублирующихся путей.
 * Вынесено отдельно от AppRouter, чтобы Fast Refresh не ругался (правило
 * react-refresh: только компоненты в файле-компоненте).
 */
export const routes = [
  {
    path: '/login',
    element: (
      <RequireGuest>
        <LoginPage />
      </RequireGuest>
    ),
  },
  {
    path: '/register',
    element: (
      <RequireGuest>
        <RegisterPage />
      </RequireGuest>
    ),
  },
  {
    path: '/reset',
    element: (
      <RequireGuest>
        <ResetRequestPage />
      </RequireGuest>
    ),
  },
  {
    path: '/reset/confirm',
    element: (
      <RequireGuest>
        <ResetConfirmPage />
      </RequireGuest>
    ),
  },
  {
    path: '/',
    element: (
      <RequireAuth>
        <HomePage />
      </RequireAuth>
    ),
  },
  { path: '*', element: <NotFoundPage /> },
]
