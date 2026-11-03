import { describe, expect, it } from 'vitest'
import userEvent from '@testing-library/user-event'
import { useAuth } from '../stores/authStore'
import { demoSession } from '../test/renderApp'
import { renderApp, screen } from '../test/renderApp'

describe('S1 · вход/регистрация/восстановление (design §4 S1)', () => {
  it('гостю доступна только страница входа; успех переводит на дом S2', async () => {
    const user = userEvent.setup()
    renderApp('/login')

    await user.type(screen.getByLabelText('Email'), 'demo@trip.pl')
    await user.type(screen.getByLabelText('Пароль'), 'demo1234')
    await user.click(screen.getByRole('button', { name: 'Войти' }))

    // успешный вход → S2 с пустым состоянием (критерий: переход на S2)
    await screen.findByText('Нет путешествий', {}, { timeout: 3000 })
    expect(screen.getByRole('banner')).toHaveTextContent('Trip Planner')
  })

  it('неверные креды: инлайн/alert-ошибка, пользователь остаётся на S1', async () => {
    const user = userEvent.setup()
    renderApp('/login')

    await user.type(screen.getByLabelText('Email'), 'demo@trip.pl')
    await user.type(screen.getByLabelText('Пароль'), 'wrong-password')
    await user.click(screen.getByRole('button', { name: 'Войти' }))

    await screen.findByRole('alert', {}, { timeout: 3000 })
    expect(screen.getByRole('alert')).toHaveTextContent('Неверный email или пароль')
    expect(screen.getByLabelText('Email')).toBeVisible()
  })

  it('регистрация с валидационными ошибками показывает карточку полей', async () => {
    const user = userEvent.setup()
    renderApp('/register')

    await user.type(screen.getByLabelText('Email'), 'nota-valid-email')
    await user.click(screen.getByRole('button', { name: 'Зарегистрироваться' }))

    await screen.findByText('Некорректный email', {}, { timeout: 3000 })
    expect(screen.getByText('Укажите имя')).toBeVisible()
  })

  it('успешная регистрация сразу авторизует и открывает пустой дом', async () => {
    const user = userEvent.setup()
    renderApp('/register')

    await user.type(screen.getByLabelText('Имя'), 'Аля')
    await user.type(screen.getByLabelText('Email'), 'alya@example.com')
    await user.type(screen.getByLabelText('Пароль'), 'puщiniи8')
    await user.click(screen.getByRole('button', { name: 'Зарегистрироваться' }))

    await screen.findByText('Нет путешествий', {}, { timeout: 3000 })
    expect(screen.queryByLabelText('Имя')).toBeNull()
  })

  it('восстановление: неизвестный email даёт явную ошибку', async () => {
    const user = userEvent.setup()
    renderApp('/reset')

    await user.type(screen.getByLabelText('Email'), 'ghost@trip.pl')
    await user.click(screen.getByRole('button', { name: 'Отправить письмо' }))

    await screen.findByText('Пользователь с таким email не найден', {}, { timeout: 3000 })
  })

  it('аутентифицированный пользователь на гостевых страницах уходит на дом', async () => {
    useAuth.setState(demoSession())
    renderApp('/login')
    await screen.findByText('Нет путешествий', {}, { timeout: 3000 })
  })
})
