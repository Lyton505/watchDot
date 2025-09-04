from custom_handlers.common import (
    search_terms,
)
from custom_handlers.duo import handle_duo
from custom_handlers.bloom import handle_bloomberg
from custom_handlers.intuit import handle_intuit
from custom_handlers.ebay import handle_ebay
from custom_handlers.gemini import handle_gemini


async def job_worker(site, browser):

    page = await browser.new_page()
    try:
        await page.goto(site, wait_until="domcontentloaded", timeout=45000)
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

        print("\nResults:")

        try:
            # we never want to miss intern
            await page.locator(r"text=/\bintern\b/i").first.wait_for(timeout=5000)
        except Exception:
            pass

        if "duolingo.com" in site:
            await handle_duo(page, site, search_terms)
            return

        if "bloomberg" in site:
            await handle_bloomberg(page, site)
            return

        if "intuit.com" in site:
            await handle_intuit(page, site)
            return

        if "ebayinc.com" in site:
            await handle_ebay(page, site)
            return

        if "gemini.com" in site:
            await handle_gemini(page, site)
            return

        text = await page.evaluate("() => document.documentElement.innerText")
        await search_terms(site, text)
    finally:
        await page.close()
