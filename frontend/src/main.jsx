import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router'
import { createBrowserRouter } from 'react-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import './styles/base.css'
import './styles/components.css'
import './i18n'
import { wireApi } from './api/wiring'
import { routes } from './routes/routes'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
})

wireApi()

/*
 * MSW: перехватывает /api в dev по контрактам architecture.md §7.
 * VITE_USE_MOCKS=false (см. frontend/.env.example) — работать против
 * реального Django API через прокси Vite на :8000.
 */
async function enableMocking() {
  if (import.meta.env.MODE === 'test') return
  if (import.meta.env.PROD) return
  if (import.meta.env.VITE_USE_MOCKS === 'false') return
  const { worker } = await import('./mocks/browser')
  await worker.start({ onUnhandledRequest: 'bypass' })
}

const router = createBrowserRouter(routes)

function render() {
  ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <Toaster position="top-center" theme="system" />
      </QueryClientProvider>
    </React.StrictMode>,
  )
}

enableMocking()
  .then(render)
  .catch((error) => {
    // MSW не стартовал — не оставляем белый экран: рендерим приложение,
    // оно честно покажет сетевые ошибки вместо/поверх моков.
    console.error('[MSW] worker не стартовал:', error)
    render()
  })
