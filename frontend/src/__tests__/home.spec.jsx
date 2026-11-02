import { describe, expect, it } from 'vitest'
import { within } from '@testing-library/react'
import { server, failingTrips } from '../mocks/server'
import { demoSession } from '../test/renderApp'
import { renderApp, screen } from '../test/renderApp'

describe('S2 · дом: empty / loading / error состояния (design §4 S2)', () => {
  it('пустые данные → «Нет путешествий» + CTA создания', async () => {
    renderApp('/', { auth: demoSession() })
    await screen.findByText('Нет путешествий', {}, { timeout: 3000 })
    const emptyCard = screen.getByText('Нет путешествий').closest('.trips-empty')
    expect(within(emptyCard).getByRole('button', { name: 'Создать путешествия' })).toBeVisible()
  })

  it('ошибка API → alert «Не удалось загрузить»', async () => {
    server.use(failingTrips())
    renderApp('/', { auth: demoSession() })
    await screen.findByRole('alert', {}, { timeout: 3000 })
    expect(screen.getByRole('alert')).toHaveTextContent('Не удалось загрузить')
  })

  it('без аутентификации дом недоступен — редирект на вход (product §4)', async () => {
    renderApp('/')
    await screen.findByText('Вход', {}, { timeout: 3000 })
    expect(screen.getByRole('button', { name: 'Войти' })).toBeVisible()
  })
})
