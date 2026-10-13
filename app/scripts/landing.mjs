// Writes dist/index.html: a landing page linking both releases (used by the Vercel build).
import { writeFileSync } from 'node:fs'
writeFileSync('dist/index.html', `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Acme Orders - releases</title>
<style>body{font:16px system-ui,sans-serif;max-width:560px;margin:12vh auto;padding:0 16px;color:#1d2733}
a{display:block;padding:14px 18px;margin:10px 0;border:1px solid #c7d0d9;border-radius:10px;text-decoration:none;color:#2457d6}
a:hover{background:#f4f6f8}small{color:#5b6775}</style></head>
<body><h1>Acme Orders</h1><p>Two builds of the same app for testing locator migration.</p>
<a href="5.39/#/login">Release 5.39 <small>- the Katalon project was recorded here</small></a>
<a href="5.40/#/login">Release 5.40 <small>- the upgraded DOM</small></a>
</body></html>
`)
console.log('dist/index.html written')
