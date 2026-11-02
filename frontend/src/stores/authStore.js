import { create } from 'zustand'
import { persist } from 'zustand/middleware'

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
