# Acme Orders: a test bed for katalon-locator-migrator

This kit is a small React (Vite) app shipped as two releases, plus a Katalon project recorded against the older one. It recreates the customer situation: tests that worked on **5.39** break on **5.40** because the DOM changed.

```
acme-demo/
├─ app/                      React source (one codebase; every `NEW ? … : …` is a 5.40 change)
├─ builds/5.39  builds/5.40  production builds (static, ready to serve)
├─ serve.sh                  serves 5.39 on :4539 and 5.40 on :4540
├─ katalon-project/          Katalon project, git repo
│    master                    = as recorded on 5.39 (start here)
│    locator-migration-5.40    = reference result after running the plugin
├─ tools/record_539.py       regenerates the Object Repository from the live 5.39 build (Recorder-style)
├─ tools/run_katalon_tests.py replays the Katalon test scripts with Playwright (no Self-Healing)
├─ baseline-5.39/pages.yml   proves all 22 objects resolve on 5.39
└─ reference-run/            pages.yml, auth_hook.py, plan.json, report.md, apply.diff, evidence/*.png
```

## What changed in 5.40

| Area | 5.39 | 5.40 | Kind of breakage |
|---|---|---|---|
| Login inputs | `id="username"`, `id="password"` | React `useId` ids (`_r_0_`), `data-testid`, new placeholders | id removed |
| Remember me | `id="remember"` (BASIC object) | generated id, label "Keep me signed in" | BASIC method, generated id |
| Login button | `id="btn-login"`, text "Login" | `data-testid`, text "Sign in" | text relabelled |
| Login error | `.alert.alert-danger` "Invalid credentials" | `role="alert"`, new message | class + text changed |
| Top nav | Orders / Customers / Reports | **Dashboard** inserted first | positional XPaths now hit the **wrong link** (DRIFTED) |
| User menu | inline dropdown, `#logout` "Logout" | portal `role="menu"`, "Sign out" | portal + relabel |
| Search / status filter | `#search`, `#status-filter` | `aria-label`, `data-testid` | old value moved to another attribute |
| Export CSV | button on Orders | **removed** | must be left unresolved |
| New order | `.btn-success` "+ New Order" (BASIC) | `data-testid`, "New order" | BASIC + text change |
| Edit row button | text "Edit" (`${customer}` parameter) | icon ✎ with `title="Edit"` | parameterized locator |
| Edit dialog | inline, `#qty`, `#btn-save-order` | portal `role="dialog"`, no ids; a second "Save" on the page | ambiguous text |
| Toast | `.toast.success` "Order saved" | `role="status"` "Order updated successfully" | class + text changed |
| Customers | `#add-customer` | `data-testid="add-customer-btn"` | id removed |
| Reports iframe | `#dl-pdf` inside iframe | `data-testid` inside iframe | frame child |
| Keyword `OrderHelpers` | `By.xpath("//table[@id='orders-table']…")` | id gone | hardcoded locator outside the repository |

## Try it

```bash
./serve.sh                                   # keep running; open http://localhost:4539 and :4540
```

Then, in Claude with the plugin installed:

```
/migrate-locators http://localhost:4540 ./katalon-project
```

You can also drive the CLI yourself (see `reference-run/` for the inputs Claude produced):

```bash
KLM="python3 <plugin>/skills/migrate-locators/scripts/klm.py --work work"
git -C katalon-project checkout -b my-migration
$KLM scan --project katalon-project
cp reference-run/pages.yml reference-run/auth_hook.py work/   # or let Claude write them
$KLM probe && $KLM show
cp reference-run/plan.json work/                              # or let Claude write it
$KLM validate && $KLM apply && $KLM report
```

Replay the tests (Playwright, no healing):

```bash
python3 tools/run_katalon_tests.py --project katalon-project --url http://localhost:4540
```

Requirements: Python 3.9+, `pip install playwright pyyaml`, `python3 -m playwright install chromium`. Rebuilding the app is optional and needs Node 18+: `cd app && npm install && npm run build`.

## Reference results

| Katalon project | Site | Tests passing |
|---|---|---|
| master (recorded on 5.39) | 5.39 | **7/7** |
| master | 5.40 | **0/7** |
| locator-migration-5.40 (after the plugin) | 5.40 | **5/7** |

Results of the plugin run (`reference-run/report.md`):

- **Before:** of 22 objects, 18 were BROKEN, 2 were DRIFTED (the nav links now matched the wrong element), and 2 were still OK.
- **Applied:** 19 locators were updated. All 19 were validated in the browser first, and each now probes OK.
- **Left unresolved:** 1 object, `button_ExportCSV`, because the feature was removed from that page. TC04 therefore needs a product decision, not a new locator.

The 2 remaining failures are expected:

- **TC04:** fails because Export CSV no longer exists on the Orders page (the unresolved object above).
- **TC05:** fails on the hardcoded XPath in `Keywords/com/acme/OrderHelpers.groovy`. The report flags this but does not change it automatically. The one-line fix is `//table[@data-testid='orders-table']/tbody/tr`.
