# Katalon locator migration report

Objects: 22  |  APPLIED: 19  |  UNCHANGED: 2  |  UNRESOLVED: 1

| Object | Before | Old locator | New locator | Validation | After | Outcome | Evidence / note |
|---|---|---|---|---|---|---|---|
| `Page_Customers/button_AddCustomer` | BROKEN | `//button[@id='add-customer']` | `CSS: [data-testid="add-customer-btn"]` | VALIDATED  | OK | **APPLIED** | same label (case only); id add-customer -> data-testid add-customer-btn |
| `Page_EditOrder/button_SaveOrder` | BROKEN | `//button[@id='btn-save-order']` | `XPATH: //div[@role='dialog']//button[normalize-space(.)='Save']` | VALIDATED  | OK | **APPLIED** | 'Save' is now ambiguous (new toolbar 'Save' view button); scoped to the edit dialog, which is where btn-save-order lived |
| `Page_EditOrder/div_ToastSaved` | BROKEN | `//div[@class='toast success']` | `XPATH: //div[@role='status']` | VALIDATED  | OK | **APPLIED** | only status region shown after saving the order (same trigger as TC05); text 'Order saved' -> 'Order updated successfully' - confirm wording change is intended |
| `Page_EditOrder/input_Quantity` | BROKEN | `//input[@id='qty']` | `XPATH: //div[@role='dialog']//input[@name='quantity']` | VALIDATED  | OK | **APPLIED** | only number input in the edit dialog, labelled Quantity; id qty -> generated |
| `Page_Header/button_UserMenu` | BROKEN | `//button[@id='user-menu-btn']` | `CSS: [data-testid="user-menu"]` | VALIDATED  | OK | **APPLIED** | same 'admin' menu toggle; id user-menu-btn -> data-testid user-menu |
| `Page_Header/link_Customers` | DRIFTED | `//nav/div/ul/li[2]/a` | `XPATH: //nav//a[@href='#/customers']` | VALIDATED  | OK | **APPLIED** | DRIFT: old //li[2] now hits 'Orders'; href #/customers + text unchanged |
| `Page_Header/link_Logout` | BROKEN | `//a[@id='logout']` | `CSS: [data-testid="menu-signout"]` | VALIDATED  | OK | **APPLIED** | href #/login unchanged; text Logout -> Sign out; menu now rendered in a portal (role=menu) |
| `Page_Header/link_Orders` | DRIFTED | `//nav/div/ul/li[1]/a` | `XPATH: //nav//a[@href='#/orders']` | VALIDATED  | OK | **APPLIED** | DRIFT: old //li[1] now hits 'Dashboard' (new first nav item); href #/orders + text Orders unchanged |
| `Page_Login/button_Login` | BROKEN | `//button[@id='btn-login']` | `CSS: [data-testid="login-submit"]` | VALIDATED  | OK | **APPLIED** | only submit button of the login form; label 'Login' -> 'Sign in'; id btn-login removed |
| `Page_Login/checkbox_RememberMe` | BROKEN | `//input[@id = 'remember']` | `CSS: input[type="checkbox"][name="remember"]` | VALIDATED  | OK | **APPLIED** | BASIC id=remember gone (now _r_2_); name=remember + type=checkbox unchanged; label reworded to 'Keep me signed in' |
| `Page_Login/div_LoginError` | BROKEN | `//div[@class='alert alert-danger']` | `XPATH: //div[@role='alert']` | VALIDATED  | OK | **APPLIED** | only alert after submitting empty form (same trigger as TC02); class alert-danger -> role=alert; message reworded - confirm wording change is intended |
| `Page_Login/input_Password` | BROKEN | `//input[@id='password']` | `CSS: [data-testid="login-password"]` | VALIDATED  | OK | **APPLIED** | name=password, type=password unchanged; id now generated |
| `Page_Login/input_Username` | BROKEN | `//input[@id='username']` | `CSS: [data-testid="login-username"]` | VALIDATED  | OK | **APPLIED** | name=username unchanged; id is now React useId (_r_0_); new data-testid added |
| `Page_Orders/button_EditOrder` | BROKEN | `//table[@id='orders-table']//tr[td[text()='${customer}']]//button[text()='Edit']` | `XPATH: //table[@data-testid='orders-table']//tr[td[normalize-space(.)='${customer}']]//button[@title='Edit']` | VALIDATED  | OK | **APPLIED** | row-scoped by ${customer} as before; text button 'Edit' became icon button with title=Edit; validated with customer=Alice Smith |
| `Page_Orders/button_ExportCSV` | BROKEN | `//button[@id='export-btn']` |  |   |  | **UNRESOLVED** | No Export CSV control on Orders in 5.40 (closest is 'Download Excel' inside the Reports iframe - different page and format). TC04 needs a product decision, not  |
| `Page_Orders/button_NewOrder` | BROKEN | `//button[@class = 'btn btn-success' and (text() = '+ New Order' or . = '+ New Order')]` | `CSS: [data-testid="new-order"]` | VALIDATED  | OK | **APPLIED** | text '+ New Order' -> 'New order' (same words); BASIC class btn-success gone |
| `Page_Orders/input_Search` | BROKEN | `#search` | `CSS: input[aria-label="Search orders"]` | VALIDATED  | OK | **APPLIED** | old placeholder 'Search orders' is now the aria-label; only search box on page |
| `Page_Orders/select_StatusFilter` | BROKEN | `//select[@id='status-filter']` | `CSS: [data-testid="status-filter"]` | VALIDATED  | OK | **APPLIED** | old id status-filter is now data-testid; same options |
| `Page_Orders/table_Orders` | BROKEN | `//table[@id='orders-table']` | `CSS: [data-testid="orders-table"]` | VALIDATED  | OK | **APPLIED** | old id orders-table is now data-testid |
| `Page_Reports/button_DownloadPDF` | BROKEN | `//button[@id='dl-pdf']` | `XPATH: //button[@data-testid='download-pdf']` | VALIDATED  | OK | **APPLIED** | inside iframe_Analytics (parent kept); text unchanged; id dl-pdf -> data-testid |

## Hardcoded locators outside the Object Repository (1)

Not edited automatically - review each one.

- `Keywords/com/acme/OrderHelpers.groovy:14` - `int n = driver.findElements(By.xpath("//table[@id='orders-table']/tbody/tr")).size()`

## Next steps

1. Review `apply.diff` / `git diff` on the migration branch.
2. Run affected suites with Self-Healing **disabled** so a green run proves the new locators, not the healer.
3. Spot-check in Studio: Object Repository → object → *Add to Web Object Spy* → *Verify and Highlight*.
4. Unresolved items stay as-is: capture more page states or decide manually.
