import { configureApi } from './client'
import { authApi } from './authApi'
import { useAuth } from '../stores/authStore'

/**
 * Связь HTTP-клиента с сессией (без циклических импортов).
 * Используется в main.jsx и в тестах (renderApp) — единая точка правды.
 */
export function wireApi() {
  configureApi({
    getToken: () => useAuth.getState().access,
    refresh: async () => {
      const refresh = useAuth.getState().refresh
      if (!refresh) throw new Error('no refresh token')
      const res = await authApi.refresh(refresh)
      useAuth.getState().setSession({ access: res.data.access })
      return res.data.access
    },
    onUnauthorized: () => {
      useAuth.getState().logout()
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.assign('/login')
      }
    },
  })
}
