import { Navigate, useLocation } from 'react-router'
import { useAuth, selectIsAuthenticated } from '../stores/authStore'

/** Гость видит только auth-страницы (product §4); владелец — продукт. */
export function RequireAuth({ children }) {
  const isAuthed = useAuth(selectIsAuthenticated)
  const location = useLocation()
  if (!isAuthed) return <Navigate to="/login" replace state={{ from: location }} />
  return children
}

export function RequireGuest({ children }) {
  const isAuthed = useAuth(selectIsAuthenticated)
  if (isAuthed) return <Navigate to="/" replace />
  return children
}
