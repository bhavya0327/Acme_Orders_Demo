import { useState } from 'react'
import { createPortal } from 'react-dom'
import { NEW, RELEASE } from './release'
import s from './modern.module.css'

const LINKS_539 = [['/orders', 'Orders'], ['/customers', 'Customers'], ['/reports', 'Reports']]
// 5.40 adds Dashboard as the FIRST nav item -> every positional nav XPath shifts by one.
const LINKS_540 = [['/dashboard', 'Dashboard'], ['/orders', 'Orders'], ['/customers', 'Customers'], ['/reports', 'Reports']]

export default function Layout({ route, children }) {
  const [open, setOpen] = useState(false)
  const links = NEW ? LINKS_540 : LINKS_539
  return (
    <>
      <nav className="navbar">
        <span className="brand">Acme<span className="release">v{RELEASE}</span></span>
        <div>
          <ul>
            {links.map(([href, label]) => (
              <li key={href}>
                {NEW
                  ? <a href={'#' + href} className={route === href ? s.navLinkActive : s.navLink} aria-current={route === href ? 'page' : undefined}>{label}</a>
                  : <a href={'#' + href} className={route === href ? 'active' : ''}>{label}</a>}
              </li>
            ))}
          </ul>
        </div>
        <div className="user-menu">
          {NEW ? (
            <button data-testid="user-menu" aria-haspopup="menu" aria-expanded={open} onClick={() => setOpen(!open)}>admin ▾</button>
          ) : (
            <button id="user-menu-btn" onClick={() => setOpen(!open)}>admin ▾</button>
          )}
          {open && !NEW && (
            <ul className="dropdown">
              <li><a href="#/profile">Profile</a></li>
              <li><a id="logout" href="#/login">Logout</a></li>
            </ul>
          )}
        </div>
      </nav>
      {/* 5.40: menu is rendered in a portal at the end of <body>, only while open */}
      {open && NEW && createPortal(
        <div role="menu" className={s.menu}>
          <a role="menuitem" className={s.menuItem} href="#/profile">My profile</a>
          <a role="menuitem" className={s.menuItem} href="#/login" data-testid="menu-signout">Sign out</a>
        </div>, document.body)}
      <main>{children}</main>
    </>
  )
}
