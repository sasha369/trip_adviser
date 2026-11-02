import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Layout } from '../components/Layout'
import { Button } from '../components/ui/Button'
import { Alert } from '../components/ui/Alert'
import { Skeleton } from '../components/ui/Skeleton'
import { tripsApi } from '../api/tripsApi'
import { extractError } from '../api/client'

/**
 * S2 · Список путешествий (дом) — для INC-01 только empty / loading / error
 * состояния по design §4. Карточки, фильтры, полоса напоминаний и CTA-действия
 * приходят в INC-02; кнопка «Создать путешествие» пока честно отвечает тостом.
 */
export function HomePage() {
  const { t } = useTranslation()
  const trips = useQuery({ queryKey: ['trips'], queryFn: () => tripsApi.list() })

  return (
    <Layout section={t('nav.home')}>
      <div className="trips-toolbar">
        <h1 className="t-display" style={{ margin: 0 }}>
          {t('nav.home')}
        </h1>
        <Button onClick={() => toast.info(t('home.not_implemented'))}>{t('home.cta_create')}</Button>
      </div>

      {trips.isPending && (
        <div className="trips-skeletons" role="status" aria-label={t('home.skeleton_hint')}>
          {Array.from({ length: 3 }, (_, i) => (
            <div className="card" key={i} style={{ padding: 'var(--space-4)' }}>
              <Skeleton style={{ height: 20, width: '60%', marginBottom: 12 }} />
              <Skeleton style={{ height: 14, width: '80%' }} />
            </div>
          ))}
        </div>
      )}

      {trips.isError && (
        <Alert kind="error" title={t('home.load_failed')}>
          {extractError(trips.error).detail}
        </Alert>
      )}

      {trips.isSuccess && trips.data.length === 0 && (
        <div className="trips-empty card" role="status">
          <h2 className="t-heading" style={{ margin: 0 }}>
            {t('home.empty_title')}
          </h2>
          <p className="t-body" style={{ color: 'var(--color-text-muted)', margin: 0 }}>
            {t('home.empty_hint')}
          </p>
          <Button onClick={() => toast.info(t('home.not_implemented'))}>{t('home.cta_create')}</Button>
        </div>
      )}
    </Layout>
  )
}
