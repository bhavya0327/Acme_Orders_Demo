"""Recreate a Katalon project the way the Web Recorder would have captured it on Acme Orders 5.39.

Every .rs file is generated from the LIVE 5.39 build: properties (tag, id, name, class, text, ...)
and alternative XPaths (xpath:attributes / idRelative / link / position) are read from the real DOM,
so the evidence klm uses later is authentic, not hand-written.

Usage:  python3 tools/record_539.py --url http://localhost:4539 --out katalon-project
"""
import argparse
import os
import uuid
from xml.sax.saxutils import escape

from playwright.sync_api import sync_playwright

LOGIN = [("fill", "#username", "admin"), ("fill", "#password", "secret"), ("click", "#btn-login", None)]
STATES = {
    "login": ("/#/login", []),
    "login_error": ("/#/login", [("click", "#btn-login", None)]),
    "orders": ("/#/login", LOGIN),
    "user_menu": ("/#/login", LOGIN + [("click", "#user-menu-btn", None)]),
    "edit_modal": ("/#/login", LOGIN + [("click", "#orders-table tbody tr:first-child button", None)]),
    "after_save": ("/#/login", LOGIN + [("click", "#orders-table tbody tr:first-child button", None), ("click", "#btn-save-order", None)]),
    "customers": ("/#/login", LOGIN + [("goto", "/#/customers", None)]),
    "reports": ("/#/login", LOGIN + [("goto", "/#/reports", None)]),
}

# (object path, state, how to find it on 5.39, selectorMethod, stored locator or None=xpath:attributes,
#  BASIC-selected property names, frame parent)
OBJECTS = [
    ("Page_Login/input_Username", "login", "#username", "XPATH", None, [], None),
    ("Page_Login/input_Password", "login", "#password", "XPATH", None, [], None),
    ("Page_Login/checkbox_RememberMe", "login", "#remember", "BASIC", None, ["tag", "id"], None),
    ("Page_Login/button_Login", "login", "#btn-login", "XPATH", None, [], None),
    ("Page_Login/div_LoginError", "login_error", ".alert", "XPATH", "//div[@class='alert alert-danger']", [], None),
    ("Page_Header/link_Orders", "orders", "nav a >> nth=0", "XPATH", "//nav/div/ul/li[1]/a", [], None),
    ("Page_Header/link_Customers", "orders", "nav a >> nth=1", "XPATH", "//nav/div/ul/li[2]/a", [], None),
    ("Page_Header/link_Reports", "orders", "nav a >> nth=2", "XPATH", "//a[contains(text(),'Reports')]", [], None),
    ("Page_Header/button_UserMenu", "orders", "#user-menu-btn", "XPATH", None, [], None),
    ("Page_Header/link_Logout", "user_menu", "#logout", "XPATH", None, [], None),
    ("Page_Orders/input_Search", "orders", "#search", "CSS", "#search", [], None),
    ("Page_Orders/select_StatusFilter", "orders", "#status-filter", "XPATH", None, [], None),
    ("Page_Orders/button_ExportCSV", "orders", "#export-btn", "XPATH", None, [], None),
    ("Page_Orders/button_NewOrder", "orders", ".btn-success", "BASIC", None, ["tag", "class", "text"], None),
    ("Page_Orders/table_Orders", "orders", "#orders-table", "XPATH", None, [], None),
    ("Page_Orders/button_EditOrder", "orders", "#orders-table tbody tr:first-child button", "XPATH",
     "//table[@id='orders-table']//tr[td[text()='${customer}']]//button[text()='Edit']", [], None),
    ("Page_EditOrder/input_Quantity", "edit_modal", "#qty", "XPATH", None, [], None),
    ("Page_EditOrder/button_SaveOrder", "edit_modal", "#btn-save-order", "XPATH", None, [], None),
    ("Page_EditOrder/div_ToastSaved", "after_save", ".toast", "XPATH", "//div[@class='toast success']", [], None),
    ("Page_Customers/button_AddCustomer", "customers", "#add-customer", "XPATH", None, [], None),
    ("Page_Reports/iframe_Analytics", "reports", "#analytics-frame", "XPATH", None, [], None),
    ("Page_Reports/button_DownloadPDF", "reports", "#dl-pdf", "XPATH", None, [], "Page_Reports/iframe_Analytics"),
]

CAPTURE_JS = r"""
el => {
  const q = v => v.includes("'") ? `concat('${v.split("'").join("', \"'\", '")}')` : `'${v}'`;
  const tag = el.tagName.toLowerCase();
  const text = (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim();
  const props = {tag};
  for (const a of ['id','name','class','type','placeholder','href','title','aria-label','value','for','role'])
    if (el.getAttribute(a) !== null && el.getAttribute(a) !== '') props[a] = el.getAttribute(a);
  if (text && tag !== 'select' && tag !== 'table') props.text = text.slice(0, 100);
  if (tag === 'select') delete props.value;
  const xp = [];
  if (el.id) xp.push(['xpath:attributes', `//${tag}[@id=${q(el.id)}]`]);
  else if (el.getAttribute('name')) xp.push(['xpath:attributes', `//${tag}[@name=${q(el.getAttribute('name'))}]`]);
  else if (el.getAttribute('class')) xp.push(['xpath:attributes', `//${tag}[@class=${q(el.getAttribute('class'))}]`]);
  // idRelative: nearest ancestor with id + positional tail
  const step = n => { const same = Array.from(n.parentNode.children).filter(c => c.tagName === n.tagName);
    return n.tagName.toLowerCase() + (same.length > 1 ? `[${same.indexOf(n) + 1}]` : ''); };
  let n = el, tail = [];
  while (n.parentElement && n.parentElement !== document.documentElement) {
    tail.unshift(step(n)); n = n.parentElement;
    if (n.id) { xp.push(['xpath:idRelative', `//${n.tagName.toLowerCase()}[@id=${q(n.id)}]/${tail.join('/')}`]); break; }
  }
  if (tag === 'a' && text) xp.push(['xpath:link', `//a[contains(text(),${q(text)})]`]);
  if (tag === 'a' && el.getAttribute('href')) xp.push(['xpath:href', `//a[contains(@href, ${q(el.getAttribute('href'))})]`]);
  // position: shortest positional path Katalon-style (last 3 steps)
  let parts = [], m = el;
  while (m && m.parentElement && parts.length < 3) { parts.unshift(step(m)); m = m.parentElement; }
  xp.push(['xpath:position', '//' + parts.join('/')]);
  if (text && ['button','a','label','div','span','h2','h3'].includes(tag) && text.length < 40)
    xp.push(['xpath:customAttributes', `//${tag}[(text() = ${q(text)} or . = ${q(text)})]`]);
  return {props, xp};
}
"""


def rs_xml(name, method, xpath, css, props, selected, xpaths, parent):
    g = lambda: str(uuid.uuid4())
    basic = ""
    P = ""
    rows = list(props.items())
    if parent:
        rows.append(("ref_element", "Object Repository/" + parent))
    for k, v in rows:
        sel = "true" if (k in selected or k == "ref_element") else "false"
        P += (f"   <webElementProperties>\n      <isSelected>{sel}</isSelected>\n      <matchCondition>equals</matchCondition>\n"
              f"      <name>{escape(k)}</name>\n      <type>Main</type>\n      <value>{escape(v)}</value>\n"
              f"      <webElementGuid>{g()}</webElementGuid>\n   </webElementProperties>\n")
    X = ""
    for i, (k, v) in enumerate(xpaths):
        X += (f"   <webElementXpaths>\n      <isSelected>{'true' if i == 0 else 'false'}</isSelected>\n"
              f"      <matchCondition>equals</matchCondition>\n      <name>{k}</name>\n      <type>Main</type>\n"
              f"      <value>{escape(v)}</value>\n      <webElementGuid>{g()}</webElementGuid>\n   </webElementXpaths>\n")
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<WebElementEntity>\n   <description></description>\n'
            f"   <name>{name}</name>\n   <tag></tag>\n   <elementGuidId>{g()}</elementGuidId>\n"
            f"   <selectorCollection>\n      <entry>\n         <key>XPATH</key>\n         <value>{escape(xpath)}</value>\n      </entry>\n"
            f"      <entry>\n         <key>CSS</key>\n         <value>{escape(css)}</value>\n      </entry>\n"
            f"      <entry>\n         <key>BASIC</key>\n         <value>{escape(basic)}</value>\n      </entry>\n   </selectorCollection>\n"
            f"   <selectorMethod>{method}</selectorMethod>\n   <smartLocatorEnabled>false</smartLocatorEnabled>\n"
            f"   <useRalativeImagePath>true</useRalativeImagePath>\n{P}{X}</WebElementEntity>\n")


def run_actions(page, base, actions):
    for verb, sel, val in actions:
        if verb == "fill":
            page.fill(sel, val)
        elif verb == "click":
            page.click(sel)
        elif verb == "goto":
            page.goto(base + sel)
        page.wait_for_timeout(150)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:4539")
    ap.add_argument("--out", default="katalon-project")
    a = ap.parse_args()
    repo = os.path.join(a.out, "Object Repository")
    with sync_playwright() as p:
        b = p.chromium.launch()
        for path, state, finder, method, stored, selected, parent in OBJECTS:
            url, actions = STATES[state]
            page = b.new_page()
            page.goto(a.url + url)
            page.wait_for_timeout(200)
            run_actions(page, a.url, actions)
            root = page.frame_locator("#analytics-frame") if parent else page
            cap = root.locator(finder).first.evaluate(CAPTURE_JS)
            page.close()
            xpaths = cap["xp"]
            xpath = stored if (stored and method != "CSS") else (xpaths[0][1] if method == "XPATH" else "")
            if stored and method == "XPATH" and stored != xpaths[0][1]:
                xpaths.insert(0, ("xpath:recorded", stored))
            css = stored if method == "CSS" else ""
            out = os.path.join(repo, path + ".rs")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                f.write(rs_xml(path.split("/")[-1], method, xpath, css, cap["props"], selected, xpaths, parent))
            print(f"captured {path:40} {method:5} {xpath or css}")
        b.close()


if __name__ == "__main__":
    main()
