import { useLocation } from 'react-router'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../stores/authStore'
import { Button } from './ui/Button'

/**
 * Постоянная верхняя шапка (design.md §2): логотип, имя раздела, справа
 * пользователь и действия. Для INC-01 достаточно блока «Выйти»;
 * «Создать путешествие» и «Профиль» приходят с полным S2 (INC-02) и S8 (INC-04).
 */
export function Layout({ section, children, maxWidth = 960 }) {
  const { t } = useTranslation()
  const location = useLocation()
  const user = useAuth((s) => s.user)
  const logout = useAuth((s) => s.logout)

  return (
    <div>
      <header className="header" role="banner">
        <div className="header__brand">
          <span className="header__logo">{t('app.name')}</span>
          <span className="header__section">{section ?? ''}</span>
        </div>
        <div className="header__actions">
          {user?.name && (
            <span className="header__user" title={user.email}>
              {user.name}
            </span>
          )}
          <Button
            variant="ghost"
            onClick={() => {
              logout()
              window.location.assign('/login')
            }}
          >
            {t('nav.logout')}
          </Button>
        </div>
      </header>
      <main
        id="content"
        style={{ maxWidth, margin: '0 auto', padding: 'var(--space-5)' }}
        data-path={location.pathname}
      >
        {children}
      </main>
    </div>
  )
}

export function AuthLayout({ title, subtitle, children }) {
  const { t } = useTranslation()
  return (
    <div className="gate" data-testid="guest-layout">
      <div className="card auth-card">
        <p className="t-meta" style={{ marginTop: 0 }}>
          {t('app.name')}
        </p>
        {title && (
          <h1 className="t-display" style={{ margin: '0 0 var(--space-2)' }}>
            {title}
          </h1>
        )}
        {subtitle && (
          <p className="t-body" style={{ color: 'var(--color-text-muted)', marginTop: 0 }}>
            {subtitle}
          </p>
        )}
        {children}
      </div>
    </div>
  )
}
