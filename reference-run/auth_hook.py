import os
def login(page, base_url):
    page.goto(base_url + "/#/login")
    page.fill("input[name=username]", os.environ.get("ACME_USER", "admin"))
    page.fill("input[name=password]", os.environ.get("ACME_PASSWORD", "secret"))
    page.click("button[type=submit]")
    page.wait_for_url("**/#/orders")
