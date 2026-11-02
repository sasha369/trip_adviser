import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { useTranslation } from 'react-i18next'
import { AuthLayout } from '../../components/Layout'
import { Button } from '../../components/ui/Button'
import { TextField } from '../../components/ui/TextField'
import { Alert } from '../../components/ui/Alert'
import { authApi } from '../../api/authApi'
import { extractError } from '../../api/client'
import { useAuth } from '../../stores/authStore'

export function RegisterPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const setSession = useAuth((s) => s.setSession)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [detail, setDetail] = useState(null)
  const [fields, setFields] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setDetail(null)
    setFields({})
    setSubmitting(true)
    try {
      // §7: регистрация сразу выдаёт JWT — email-подтверждение не входит в продукт
      const res = await authApi.register({ name, email, password })
      setSession(res.data)
      navigate('/', { replace: true })
    } catch (err) {
      const n = extractError(err)
      setDetail(n.detail)
      setFields(n.fields)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout title={t('auth.register_title')} subtitle={t('auth.register_subtitle')}>
      {detail && <Alert kind="error" title={detail} />}
      <form onSubmit={onSubmit} noValidate>
        <TextField
          id="name"
          label={t('auth.name')}
          autoComplete="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={fields.name}
        />
        <TextField
          id="email"
          label={t('auth.email')}
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={fields.email}
        />
        <TextField
          id="password"
          label={t('auth.password')}
          type="password"
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={fields.password}
          hint="Минимум 8 символов"
        />
        <Button type="submit" block loading={submitting}>
          {t('auth.submit_register')}
        </Button>
        <p className="t-meta" style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/login">{t('auth.to_login')}</Link>
        </p>
      </form>
    </AuthLayout>
  )
}
