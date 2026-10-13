import { useId, useState } from 'react'
import { NEW, RELEASE } from './release'
import s from './modern.module.css'

export default function Login() {
  const [error, setError] = useState('')
  const uid = useId(), pid = useId(), rid = useId()
  const submit = (e) => {
    e.preventDefault()
    const f = new FormData(e.target)
    if (f.get('username') && f.get('password')) window.location.hash = '/orders'
    else setError(NEW ? 'Please enter your username and password.' : 'Invalid credentials')
  }

  if (!NEW) {
    // ---------------- 5.39 ----------------
    return (
      <div className="login-card">
        <h1>Acme Orders <span className="release">v{RELEASE}</span></h1>
        <form id="login-form" onSubmit={submit}>
          <label htmlFor="username">Username</label>
          <input id="username" name="username" className="form-control" placeholder="Username" />
          <label htmlFor="password">Password</label>
          <input id="password" name="password" type="password" className="form-control" placeholder="Password" />
          <p><input type="checkbox" id="remember" name="remember" /> <label htmlFor="remember">Remember me</label></p>
          {error && <div className="alert alert-danger">{error}</div>}
          <button id="btn-login" className="btn btn-primary" type="submit">Login</button>
        </form>
      </div>
    )
  }
  // ---------------- 5.40 ----------------
  return (
    <div className={s.card}>
      <h1>Welcome back <span className="release">v{RELEASE}</span></h1>
      <form onSubmit={submit} noValidate>
        <label htmlFor={uid}>Username</label>
        <input id={uid} name="username" data-testid="login-username" className={s.input} placeholder="Enter your username" autoComplete="username" />
        <label htmlFor={pid}>Password</label>
        <input id={pid} name="password" type="password" data-testid="login-password" className={s.input} placeholder="Enter your password" />
        <p><input type="checkbox" id={rid} name="remember" /> <label htmlFor={rid}>Keep me signed in</label></p>
        {error && <div role="alert">{error}</div>}
        <button className={s.primary} type="submit" data-testid="login-submit">Sign in</button>
      </form>
    </div>
  )
}
