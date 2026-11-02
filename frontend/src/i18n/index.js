import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

// Стандарт i18n (architecture §9): все строки — через i18n-механизм без хардкода,
// единственная локаль ru; добавление локали должно оставаться механической операцией.
const ru = {
  app: { name: 'Trip Planner' },
  nav: {
    home: 'Список путешествий',
    logout: 'Выйти',
    guest: 'Гостевой режим',
  },
  auth: {
    login_title: 'Вход',
    login_subtitle: 'Войдите, чтобы продолжить планирование',
    register_title: 'Регистрация',
    register_subtitle: 'Создайте аккаунт — всего один шаг',
    reset_title: 'Восстановление пароля',
    reset_subtitle: 'Укажите email — пришлём письмо со ссылкой',
    confirm_subtitle: 'Придумайте новый пароль',
    email: 'Email',
    password: 'Пароль',
    new_password: 'Новый пароль',
    repeat_password: 'Повторите пароль',
    name: 'Имя',
    token: 'Код из письма',
    submit_login: 'Войти',
    submit_register: 'Зарегистрироваться',
    submit_reset: 'Отправить письмо',
    submit_confirm: 'Установить пароль',
    to_register: 'Регистрация',
    to_login: 'Войти',
    to_reset: 'Забыли пароль?',
    reset_sent: 'Письмо отправлено. Проверьте почту.',
    confirm_done: 'Пароль изменён. Теперь войдите с новым паролем.',
    email_not_found: 'Пользователь с таким email не найден',
    invalid_credentials: 'Неверный email или пароль',
    invalid_token: 'Ссылка устарела или неверна',
  },
  home: {
    empty_title: 'Нет путешествий',
    empty_hint: 'Заведите первую поездку: даты, маршрут и план по дням — всё в одном месте.',
    cta_create: 'Создать путешествия',
    load_failed: 'Не удалось загрузить',
    retry: 'Повторить',
    skeleton_hint: 'Загружаем путешествия…',
    not_implemented: 'Создание путешествия появится в следующем инкременте',
  },
  not_found: {
    title: 'Страница не найдена',
    hint: 'Проверьте адрес или вернитесь на главную.',
    home: 'На главную',
  },
  common: {
    loading: 'Загрузка…',
    save_error: 'Сохранить не удалось. Попробуйте ещё раз.',
  },
}

i18n.use(initReactI18next).init({
  resources: { ru: { translation: ru } },
  lng: 'ru',
  fallbackLng: 'ru',
  interpolation: { escapeValue: false },
})

export default i18n
