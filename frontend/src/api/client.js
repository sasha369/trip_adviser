import axios from 'axios'

/*
 * HTTP-слой (architecture §7/§9): Axios, интерсепторы JWT-refresh и request-id.
 * Клиент не знает о store — зависимости подключаются через configureApi()
 * в main.jsx, чтобы не было циклических импортов.
 */

const tokenProvider = { current: () => null }
let refreshAction = null
let onUnauthorized = null

export function configureApi({ getToken, refresh, unauthorized }) {
  if (getToken) tokenProvider.current = getToken
  if (refresh) refreshAction = refresh
  if (unauthorized) onUnauthorized = unauthorized
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = tokenProvider.current()
  if (token) config.headers.Authorization = `Bearer ${token}`
  // request-id (§9 observability): клиент ставит id, бэкенд прокидывает его в логи/Селery
  config.headers['X-Request-Id'] = crypto.randomUUID()
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config ?? {}
    const status = error.response?.status
    const isAuthPath = String(original.url ?? '').includes('/auth/')

    // Обновление access по refresh и однократный ретрай исходного запроса (§7 refresh)
    if (status === 401 && refreshAction && !original._retried && !isAuthPath) {
      original._retried = true
      const refreshed = await refreshAction().catch((e) => {
        onUnauthorized?.(e)
        return null
      })
      if (refreshed) return api(original)
    }

    if (status === 401 && !refreshAction) onUnauthorized?.(error)
    return Promise.reject(error)
  },
)

/**
 * Единый формат ошибок §9: {code, detail, fields}.
 * Возвращает нормализованный объект для UI: инлайн-ошибки полей +
 * alert-текст сверху.
 */
export function extractError(error) {
  const body = error.response?.data ?? {}
  return {
    code: body.code ?? 'network_error',
    detail: body.detail ?? 'Не удалось выполнить запрос. Проверьте соединение.',
    fields: body.fields ?? {},
    status: error.response?.status ?? 0,
  }
}
