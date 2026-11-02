import { RouterProvider, createBrowserRouter } from 'react-router'
import { routes } from './routes'

export function AppRouter() {
  const router = createBrowserRouter(routes)
  return <RouterProvider router={router} />
}
