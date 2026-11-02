import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../api/authApi'

/**
 * Сессия (architecture §7): access/refresh JWT + вернувшийся user.
 * Персистится в localStorage; выход — сброс пары токенов, серверного
 * logout-эндпоинта нет (§7 «Соглашения»).
 */
export const useAuth = create(
  persist(
    (set) => ({
      access: null,
      refresh: null,
      user: null,
      setSession: ({ access, refresh, user }) => set((s) => ({ access, refresh, user: user ?? s.user })),
      logout: () => set({ access: null, refresh: null, user: null }),
    }),
    { name: 'trip-planner-auth' },
  ),
)

export const selectIsAuthenticated = (s) => Boolean(s.access)

/**
 * Реальный SimpleJWT обычно возвращает только {access, refresh} без user.
 * adoptSession сохраняет токены и добирает профиль через GET /api/profile.
 * Мок уже кладёт user в ответ — fallback просто не сработает.
 */
export async function adoptSession(tokens) {
  useAuth.getState().setSession(tokens)
  if (!tokens.user) {
    const res = await authApi.getProfile()
    useAuth.getState().setSession({ user: res.data })
  }
}
