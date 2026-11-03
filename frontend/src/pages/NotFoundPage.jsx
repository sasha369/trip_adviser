import { Link } from 'react-router'
import { useTranslation } from 'react-i18next'
import { useAuth, selectIsAuthenticated } from '../stores/authStore'

export function NotFoundPage() {
  const { t } = useTranslation()
  const isAuthed = useAuth(selectIsAuthenticated)
  return (
    <div className="gate">
      <div className="card auth-card" style={{ textAlign: 'center' }}>
        <h1 className="t-display">{t('not_found.title')}</h1>
        <p className="t-body" style={{ color: 'var(--color-text-muted)' }}>
          {t('not_found.hint')}
        </p>
        <p>{isAuthed ? <Link to="/">{t('not_found.home')}</Link> : <Link to="/login">{t('auth.to_login')}</Link>}</p>
      </div>
    </div>
  )
}
