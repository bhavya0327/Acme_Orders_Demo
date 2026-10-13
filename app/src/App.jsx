import { useEffect, useState } from 'react'
import { NEW, RELEASE } from './release'
import Login from './Login.jsx'
import Layout from './Layout.jsx'
import Orders from './Orders.jsx'
import Customers from './Customers.jsx'
import Reports from './Reports.jsx'
import Dashboard from './Dashboard.jsx'

function useHashRoute() {
  const get = () => (window.location.hash.replace(/^#/, '') || '/login')
  const [route, setRoute] = useState(get)
  useEffect(() => {
    const on = () => setRoute(get())
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  return route
}

export default function App() {
  const route = useHashRoute()
  useEffect(() => { document.title = `Acme Orders ${RELEASE}` }, [])
  if (route === '/login') return <Login />
  const pages = { '/orders': Orders, '/customers': Customers, '/reports': Reports }
  if (NEW) pages['/dashboard'] = Dashboard
  const Page = pages[route] || Orders
  return <Layout route={route}><Page /></Layout>
}
