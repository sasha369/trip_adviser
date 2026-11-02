import { api } from './client'

/**
 * Аутентификация — contracts: architecture.md §7 accounts (`/api/auth/*`).
 * Форма запроса/ответа фиксируется моками (MSW) по этим же контрактам
 * и сверяется с реальным Django API в INC-01 «Done when».
 */
export const authApi = {
  register: (payload) => api.post('/auth/register', payload),
  login: (payload) => api.post('/auth/login', payload),
  refresh: (refresh) => api.post('/auth/refresh', { refresh }),
  requestReset: (email) => api.post('/auth/reset', { email }),
  confirmReset: ({ token, password }) => api.post('/auth/reset/confirm', { token, password }),
  getProfile: () => api.get('/profile'),
}
