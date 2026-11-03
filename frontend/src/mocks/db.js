/**
 * In-memory база мока; resetDb даёт изоляцию между тестами.
 */
export const db = {
  users: [],
  // access-token -> { userId, exp }
  sessions: new Map(),
  // refresh-token -> { userId, exp }
  refreshSessions: new Map(),
  // reset-token -> { userId, exp }
  resetTokens: new Map(),
  trips: [],
}

const uuid = () => crypto.randomUUID()

export const DAY_MS = 24 * 60 * 60 * 1000

export function resetDb({ withDemoUser = false } = {}) {
  db.users = []
  db.sessions.clear()
  db.refreshSessions.clear()
  db.resetTokens.clear()
  db.trips = []
  if (withDemoUser) {
    db.users.push({ id: uuid(), name: 'Демо', email: 'demo@trip.pl', password: 'demo1234' })
  }
}

export function seedDemoUser() {
  if (!db.users.some((u) => u.email === 'demo@trip.pl')) {
    resetDb()
    db.users.push({ id: uuid(), name: 'Демо', email: 'demo@trip.pl', password: 'demo1234' })
  }
}

export function findUserByEmail(email) {
  return db.users.find((u) => u.email.toLowerCase() === String(email ?? '').toLowerCase())
}

export function createUser({ name, email, password }) {
  const user = { id: uuid(), name: name.trim(), email: String(email).toLowerCase(), password }
  db.users.push(user)
  return user
}

export function publicUser(user) {
  // Форма User по ER (architecture §8): id, email, name
  return { id: user.id, email: user.email, name: user.name }
}

export function issueSession(userId) {
  const access = `mock-access-${uuid()}`
  const refresh = `mock-refresh-${uuid()}`
  db.sessions.set(access, { userId, exp: Date.now() + DAY_MS })
  db.refreshSessions.set(refresh, { userId, exp: Date.now() + 14 * DAY_MS })
  return { access, refresh }
}

export function userFromAccess(token) {
  const entry = db.sessions.get(token)
  if (!entry || entry.exp < Date.now()) return null
  return { token, entry }
}

export function rotateSession(refreshToken) {
  const entry = db.refreshSessions.get(refreshToken)
  if (!entry || entry.exp < Date.now()) return null
  db.refreshSessions.delete(refreshToken)
  const access = `mock-access-${uuid()}`
  db.sessions.set(access, { userId: entry.userId, exp: Date.now() + DAY_MS })
  return access
}

export function userIdFromAccess(token) {
  const session = userFromAccess(token)
  return session ? session.entry.userId : null
}

export function createResetToken(userId) {
  const token = uuid()
  db.resetTokens.set(token, { userId, exp: Date.now() + DAY_MS })
  return token
}

export function consumeResetToken(token) {
  const entry = db.resetTokens.get(token)
  if (!entry || entry.exp < Date.now()) return null
  db.resetTokens.delete(token)
  return entry.userId
}

export function addTrip({ user_id, title, status, start_date, end_date, origin, destination }) {
  const trip = { id: uuid(), user_id, title, status, start_date, end_date, origin, destination }
  db.trips.push(trip)
  return trip
}

export function tripsOf(userId) {
  return db.trips.filter((t) => t.user_id === userId)
}
