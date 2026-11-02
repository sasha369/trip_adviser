import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { useTranslation } from 'react-i18next'
import { toast } from 'sonner'
import { AuthLayout } from '../../components/Layout'
import { Button } from '../../components/ui/Button'
import { TextField } from '../../components/ui/TextField'
import { Alert } from '../../components/ui/Alert'
import { authApi } from '../../api/authApi'
import { extractError } from '../../api/client'

export function ResetConfirmPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [token, setToken] = useState('')
  const [password, setPassword] = useState('')
  const [done, setDone] = useState(false)
  const [detail, setDetail] = useState(null)
  const [fields, setFields] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setDetail(null)
    setFields({})
    setSubmitting(true)
    try {
      await authApi.confirmReset({ token, password })
      setDone(true)
      toast.success(t('auth.confirm_done'))
      navigate('/login', { replace: true })
    } catch (err) {
      const n = extractError(err)
      setDetail(n.detail)
      setFields(n.fields ?? {})
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout title={t('auth.reset_title')} subtitle={t('auth.confirm_subtitle')}>
      {done ? (
        <Alert kind="success" title={t('auth.confirm_done')} />
      ) : (
        <>
          {detail && <Alert kind="error" title={detail} />}
          <form onSubmit={onSubmit} noValidate>
            <TextField
              id="token"
              label={t('auth.token')}
              value={token}
              onChange={(e) => setToken(e.target.value)}
              error={fields.token}
            />
            <TextField
              id="new-password"
              label={t('auth.new_password')}
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={fields.password}
            />
            <Button type="submit" block loading={submitting}>
              {t('auth.submit_confirm')}
            </Button>
            <p className="t-meta" style={{ textAlign: 'center' }}>
              <Link to="/login">{t('auth.to_login')}</Link>
            </p>
          </form>
        </>
      )}
    </AuthLayout>
  )
}
