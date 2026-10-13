import { useId, useState } from 'react'
import { createPortal } from 'react-dom'
import { NEW } from './release'
import { ORDERS } from './data'
import s from './modern.module.css'

function EditModal({ order, onClose, onSave }) {
  const [qty, setQty] = useState(order.qty)
  const qid = useId(), tid = useId()
  if (!NEW) {
    // 5.39: inline modal with stable ids
    return (
      <div className="modal-backdrop">
        <div className="modal" id="edit-order-modal">
          <h2>Edit Order {order.id}</h2>
          <label htmlFor="qty">Quantity</label>
          <input id="qty" className="form-control" type="number" value={qty} onChange={e => setQty(e.target.value)} />
          <div className="modal-actions">
            <button className="btn" onClick={onClose}>Cancel</button>
            <button id="btn-save-order" className="btn btn-primary" onClick={() => onSave(qty)}>Save</button>
          </div>
        </div>
      </div>
    )
  }
  // 5.40: accessible dialog rendered in a portal, no ids/testids on the buttons
  return createPortal(
    <div className="modal-backdrop">
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby={tid}>
        <h2 id={tid}>Edit order #{order.id}</h2>
        <label htmlFor={qid}>Quantity</label>
        <input id={qid} name="quantity" className={s.input} type="number" value={qty} onChange={e => setQty(e.target.value)} />
        <div className="modal-actions">
          <button className={s.ghost} onClick={onClose}>Cancel</button>
          <button className={s.primary} onClick={() => onSave(qty)}>Save</button>
        </div>
      </div>
    </div>, document.body)
}

export default function Orders() {
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('')
  const [editing, setEditing] = useState(null)
  const [toast, setToast] = useState('')
  const rows = ORDERS.filter(o => (!status || o.status === status) &&
    (!q || o.customer.toLowerCase().includes(q.toLowerCase()) || String(o.id).includes(q)))
  const save = () => { setEditing(null); setToast(NEW ? 'Order updated successfully' : 'Order saved'); setTimeout(() => setToast(''), 4000) }

  return (
    <section>
      <div className="toolbar">
        {NEW
          ? <input type="search" aria-label="Search orders" placeholder="Search by customer or order #" value={q} onChange={e => setQ(e.target.value)} />
          : <input id="search" placeholder="Search orders" value={q} onChange={e => setQ(e.target.value)} />}
        {NEW
          ? <select name="status" data-testid="status-filter" value={status} onChange={e => setStatus(e.target.value)}>
              <option value="">All statuses</option><option>Pending</option><option>Shipped</option><option>Delivered</option></select>
          : <select id="status-filter" value={status} onChange={e => setStatus(e.target.value)}>
              <option value="">All</option><option>Pending</option><option>Shipped</option><option>Delivered</option></select>}
        {/* 5.40 adds a "Save" button for saved views -> a second visible "Save" on the page */}
        {NEW && <button className={s.ghost}>Save</button>}
        <span style={{ flex: 1 }} />
        {/* 5.40 removed Export CSV from this page (moved into Reports as "Download Excel") */}
        {!NEW && <button id="export-btn" className="btn">Export CSV</button>}
        {NEW
          ? <button className={s.primary} data-testid="new-order">New order</button>
          : <button className="btn btn-success">+ New Order</button>}
      </div>
      <div className={NEW ? s.wrap : undefined}>
        <table {...(NEW ? { 'data-testid': 'orders-table' } : { id: 'orders-table' })}>
          <thead><tr><th>Order</th><th>Customer</th><th>Status</th><th>Total</th><th></th></tr></thead>
          <tbody>
            {rows.map(o => (
              <tr key={o.id}>
                <td>{o.id}</td><td>{o.customer}</td><td>{o.status}</td><td>${o.total.toFixed(2)}</td>
                <td>{NEW
                  ? <button className="icon-btn" aria-label={`Edit order ${o.id}`} title="Edit" onClick={() => setEditing(o)}>✎</button>
                  : <button className="btn-edit" onClick={() => setEditing(o)}>Edit</button>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {editing && <EditModal order={editing} onClose={() => setEditing(null)} onSave={save} />}
      {toast && (NEW
        ? <div role="status" className={s.toast}>{toast}</div>
        : <div className="toast success">{toast}</div>)}
    </section>
  )
}
