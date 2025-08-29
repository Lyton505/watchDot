import re
from custom_handlers.common import search_terms
from custom_handlers.duo import handle_duo


async def job_worker(site, browser):
    page = await browser.new_page()
    try:
        await page.goto(site, wait_until="domcontentloaded", timeout=45000)
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

        print("\nResults:")

        if "duolingo.com" in site:
            await handle_duo(page, site)
            return
        else:
            text = await page.evaluate("() => document.documentElement.innerText")
            await search_terms(site, text)
    finally:
        await page.close()
