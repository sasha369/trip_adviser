import { api } from './client'

/**
 * trips API (architecture §7 trips). Для queryFn возвращаем только тело
 * ответа — TanStack Query кладёт его в data.
 */
export const tripsApi = {
  list: async (params) => {
    const res = await api.get('/trips', { params })
    return res.data
  },
}
