import { delay, http, HttpResponse } from 'msw'
import {
  createUser,
  db,
  findUserByEmail,
  issueSession,
  publicUser,
  rotateSession,
  tripsOf,
  userFromAccess,
  userIdFromAccess,
  consumeResetToken,
  createResetToken,
} from './db'

/**
 * MSW-обработчики: 1:1 по таблицам architecture.md §7.
 * Формат ошибок — §9: {code, detail, fields}; валидация — 400.
 * Задержки имитируют сетевой отклик.
 */

const LATENCY = () => delay(200 + Math.random() * 300)
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const json = (body, status = 200, init) => HttpResponse.json(body, { status, ...init })
const validationError = (detail, fields) => json({ code: 'validation_error', detail, fields }, 400)

function unauthorized() {
  return json({ code: 'unauthorized', detail: 'Требуется аутентификация', fields: {} }, 401)
}

function bearer(request) {
  const header = request.headers.get('Authorization') ?? ''
  return header.startsWith('Bearer ') ? header.slice(7) : null
}

export const handlers = [
  // --- accounts: аутентификация и профиль (architecture §7) ---
  http.post('*/api/auth/register', async ({ request }) => {
    await LATENCY()
    const body = await request.json()
    const fields = {}
    if (!body.name?.trim()) fields.name = 'Укажите имя'
    if (!EMAIL_RE.test(String(body.email ?? ''))) fields.email = 'Некорректный email'
    if (!body.password || String(body.password).length < 8) fields.password = 'Минимум 8 символов'
    if (Object.keys(fields).length) {
      return validationError('Проверьте поля формы', fields)
    }
    if (findUserByEmail(body.email)) {
      return validationError('Проверьте поля формы', { email: 'Этот email уже зарегистрирован' })
    }
    const user = createUser(body)
    const session = issueSession(user.id)
    return json({ access: session.access, refresh: session.refresh, user: publicUser(user) }, 201)
  }),

  http.post('*/api/auth/login', async ({ request }) => {
    await LATENCY()
    const { email, password } = await request.json()
    const user = findUserByEmail(email)
    if (!user || user.password !== password) {
      return json({ code: 'invalid_credentials', detail: 'Неверный email или пароль', fields: {} }, 400)
    }
    const session = issueSession(user.id)
    return json({ access: session.access, refresh: session.refresh, user: publicUser(user) })
  }),

  http.post('*/api/auth/refresh', async ({ request }) => {
    await LATENCY()
    const { refresh } = await request.json()
    const access = rotateSession(refresh)
    if (!access) {
      return json({ code: 'invalid_refresh', detail: 'Сессия истекла', fields: {} }, 401)
    }
    return json({ access })
  }),

  http.post('*/api/auth/reset', async ({ request }) => {
    await LATENCY()
    const { email } = await request.json()
    // По design §4 S1: «email не найден при восстановлении» — явная ошибка
    const user = findUserByEmail(email)
    if (!user) {
      return json({ code: 'email_not_found', detail: 'Пользователь с таким email не найден', fields: {} }, 400)
    }
    const token = createResetToken(user.id)
    // В моке «письмо» показываем код прямо в ответе — иначе до confirm не добраться.
    // В реальном API токен придёт по ссылке из письма.
    return json({ detail: `Если email существует, письмо со ссылкой отправлено (Мок: код для confirm — ${token})` })
  }),

  http.post('*/api/auth/reset/confirm', async ({ request }) => {
    await LATENCY()
    const { token, password } = await request.json()
    const userId = consumeResetToken(token)
    if (!userId) {
      return json({ code: 'invalid_token', detail: 'Ссылка устарела или неверна', fields: {} }, 400)
    }
    const user = db.users.find((u) => u.id === userId)
    if (user) user.password = password
    return json({ detail: 'Пароль изменён' })
  }),

  http.get('*/api/profile', ({ request }) => {
    const userId = userIdFromAccess(bearer(request))
    if (!userId) return unauthorized()
    const user = db.users.find((u) => u.id === userId)
    return json(publicUser(user))
  }),

  // --- trips: единственный trips-эндпоинт INC-01 (§7) ---
  http.get('*/api/trips', ({ request }) => {
    const session = userFromAccess(bearer(request))
    if (!session) return unauthorized()
    const list = tripsOf(session.entry.userId).map(({ user_id: _user_id, ...trip }) => trip)
    return json(list)
  }),
]
