import { useState } from 'react'
import { Link } from 'react-router'
import { useTranslation } from 'react-i18next'
import { AuthLayout } from '../../components/Layout'
import { Button } from '../../components/ui/Button'
import { TextField } from '../../components/ui/TextField'
import { Alert } from '../../components/ui/Alert'
import { authApi } from '../../api/authApi'
import { extractError } from '../../api/client'

export function ResetRequestPage() {
  const { t } = useTranslation()
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [detail, setDetail] = useState(null)
  const [fields, setFields] = useState({})
  const [submitting, setSubmitting] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setDetail(null)
    setFields({})
    setSubmitting(true)
    try {
      await authApi.requestReset(email)
      // Токен «не найден» → 400 email_not_found (design §4 S1). Успех → success-состояние.
      setSent(true)
    } catch (err) {
      const n = extractError(err)
      setDetail(n.detail)
      setFields(n.fields ?? {})
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout title={t('auth.reset_title')} subtitle={t('auth.reset_subtitle')}>
      {detail && <Alert kind="error" title={detail} />}
      {sent ? (
        <>
          <Alert kind="success" title={t('auth.reset_sent')} />
          <p className="t-meta" style={{ textAlign: 'center' }}>
            <Link to="/reset/confirm">{t('auth.token')}</Link>
            <span style={{ margin: '0 8px' }}>·</span>
            <Link to="/login">{t('auth.to_login')}</Link>
          </p>
        </>
      ) : (
        <form onSubmit={onSubmit} noValidate>
          <TextField
            id="reset-email"
            label={t('auth.email')}
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={fields.email}
          />
          <Button type="submit" block loading={submitting}>
            {t('auth.submit_reset')}
          </Button>
          <p className="t-meta" style={{ textAlign: 'center' }}>
            <Link to="/login">{t('auth.to_login')}</Link>
          </p>
        </form>
      )}
    </AuthLayout>
  )
}
