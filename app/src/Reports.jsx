import { NEW } from './release'

export default function Reports() {
  // The analytics widget is embedded in an iframe; its inner markup also changed in 5.40.
  return (
    <section>
      <h2>Reports</h2>
      <iframe id="analytics-frame" title="Analytics" src={NEW ? 'embed-540.html' : 'embed-539.html'} width="520" height="160" />
    </section>
  )
}
