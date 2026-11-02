import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { handlers } from './handlers'

export const server = setupServer(...handlers)

/** Переопределение для тестов: /api/trips падает (состояние error на S2). */
export const failingTrips = () =>
  http.get('*/api/trips', () =>
    HttpResponse.json({ code: 'internal_error', detail: 'Не удалось загрузить', fields: {} }, { status: 500 }),
  )
