"""Mini replay runner: executes the project's Katalon test scripts with Playwright.

Not Katalon Studio - just enough of WebUI.* to prove (with no Self-Healing) whether the
Object Repository locators drive the real flows. Locators are resolved exactly like Katalon:
the object's active <selectorMethod> locator, ${variables} substituted, ref_element parent = iframe.

Usage: python3 tools/run_katalon_tests.py --project katalon-project --url http://localhost:4540
"""
import argparse
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright

TIMEOUT = 4000


def load_object(project, oid):
    oid = oid if oid.startswith("Object Repository/") else "Object Repository/" + oid
    root = ET.parse(os.path.join(project, oid + ".rs")).getroot()
    sel = {e.findtext("key"): (e.findtext("value") or "") for e in root.iter("entry")}
    method = (root.findtext("selectorMethod") or "BASIC").upper()
    props = [(p.findtext("name"), p.findtext("value") or "", p.findtext("isSelected") == "true")
             for p in root.findall("webElementProperties")]
    if method == "CSS":
        loc = "css=" + sel.get("CSS", "")
    elif method == "XPATH":
        loc = "xpath=" + sel.get("XPATH", "")
    else:  # BASIC: build from selected properties (equals only - enough for this project)
        chosen = [(n, v) for n, v, s in props if s and n not in ("ref_element",)]
        tag = next((v for n, v in chosen if n == "tag"), "*")
        conds = [f"normalize-space(.)='{v}'" if n == "text" else f"@{n}='{v}'" for n, v in chosen if n != "tag"]
        loc = "xpath=//" + tag + (f"[{' and '.join(conds)}]" if conds else "")
    parent = next((v for n, v, s in props if n == "ref_element" and s), None)
    return loc, parent


def parse_vars(s):
    return dict(re.findall(r"\(\s*'([^']+)'\s*\)\s*:\s*'([^']*)'", s or ""))


class Runner:
    def __init__(self, page, project, base):
        self.page, self.project, self.base, self.frame = page, project, base, None

    def locate(self, oid, vars_):
        loc, parent = load_object(self.project, oid)
        for k, v in vars_.items():
            loc = loc.replace("${" + k + "}", v)
        scope = self.page
        if parent:
            ploc, _ = load_object(self.project, parent)
            scope = self.page.frame_locator(ploc)
        elif self.frame is not None:
            scope = self.frame
        return scope.locator(loc).first, loc

    def keyword(self, line):
        m = re.search(r"CustomKeywords\.'([\w.]+)\.(\w+)'\(([^)]*)\)", line)
        cls, fn, arg = m.groups()
        src = open(os.path.join(self.project, "Keywords", *cls.split(".")) + ".groovy").read()
        xp = re.search(r'By\.xpath\("([^"]+)"\)', src).group(1)
        n = self.page.locator("xpath=" + xp).count()
        if n != int(arg):
            raise AssertionError(f"keyword {fn}: hardcoded By.xpath(\"{xp}\") found {n}, expected {arg}")

    def step(self, line):
        line = line.strip()
        if not line.startswith(("WebUI.", "CustomKeywords")):
            return
        if line.startswith("CustomKeywords"):
            return self.keyword(line)
        m = re.match(r"WebUI\.(\w+)\((.*)\)\s*$", line)
        kw, args = m.groups()
        fo = re.search(r"findTestObject\('([^']+)'(?:,\s*(\[.*?\]))?\)", args)
        rest = args[fo.end():] if fo else args
        lits = re.findall(r"'([^']*)'", rest)
        if kw in ("openBrowser", "closeBrowser"):
            return
        if kw == "navigateToUrl":
            return self.page.goto(self.base + re.search(r"'([^']*)'", args).group(1))
        if kw == "switchToDefaultContent":
            self.frame = None
            return
        el, loc = self.locate(fo.group(1), parse_vars(fo.group(2)))
        try:
            if kw == "setText":
                el.fill(lits[0], timeout=TIMEOUT)
            elif kw == "click":
                el.click(timeout=TIMEOUT)
            elif kw in ("verifyElementPresent",):
                el.wait_for(state="attached", timeout=TIMEOUT)
            elif kw in ("verifyElementVisible", "verifyElementClickable"):
                el.wait_for(state="visible", timeout=TIMEOUT)
            elif kw == "selectOptionByLabel":
                el.select_option(label=lits[0], timeout=TIMEOUT)
            elif kw == "switchToFrame":
                el.wait_for(state="attached", timeout=TIMEOUT)
                self.frame = self.page.frame_locator(loc)
            else:
                raise NotImplementedError(kw)
        except Exception as e:
            raise AssertionError(f"{kw}({fo.group(1)}) via {loc}: {str(e).splitlines()[0][:110]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    scripts = sorted(glob.glob(os.path.join(a.project, "Scripts", "*", "*.groovy")))
    passed = 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        for sc in scripts:
            tc = os.path.basename(os.path.dirname(sc))
            if a.only and tc not in a.only:
                continue
            page = b.new_page()
            r = Runner(page, a.project, a.url)
            try:
                for line in open(sc, encoding="utf-8"):
                    r.step(line)
                print(f"PASS  {tc}")
                passed += 1
            except AssertionError as e:
                print(f"FAIL  {tc}  ->  {e}")
            page.close()
        b.close()
    total = len([s for s in scripts if not a.only or os.path.basename(os.path.dirname(s)) in a.only])
    print(f"{passed}/{total} passed against {a.url}")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
