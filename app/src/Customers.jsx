import { NEW } from './release'
import { CUSTOMERS } from './data'
import s from './modern.module.css'

export default function Customers() {
  return (
    <section>
      <div className="toolbar">
        <h2 style={{ margin: 0, flex: 1 }}>Customers</h2>
        {NEW
          ? <button className={s.primary} data-testid="add-customer-btn">Add customer</button>
          : <button id="add-customer" className="btn btn-success">Add Customer</button>}
      </div>
      <table>
        <thead><tr><th>Name</th><th>Email</th><th>City</th></tr></thead>
        <tbody>{CUSTOMERS.map(c => <tr key={c.id}><td>{c.name}</td><td>{c.email}</td><td>{c.city}</td></tr>)}</tbody>
      </table>
    </section>
  )
}
