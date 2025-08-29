import re

from custom_handlers.common import extract_root_domain, extract_root_domain_v2
from custom_handlers.duo import handle_duo

TERMS = [
    "staff ai research engineer",
    "intern",
]

PATTERNS = [re.compile(rf"\b{re.escape(term)}\b", re.I) for term in TERMS]


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

            cleaned_site = extract_root_domain(site)
            cleaned_site_v2 = extract_root_domain_v2(site)

            matches = []
            for term, pattern in zip(TERMS, PATTERNS):
                if pattern.search(text):
                    matches.append(term)
                    if term == "intern":
                        print(
                            f"\t[{cleaned_site}] Special term matched: {term} at {cleaned_site_v2}"
                        )

            if matches:
                print(
                    f"\t[{cleaned_site}] found match(es): {', '.join(matches)} at {cleaned_site_v2}\n"
                )
            else:
                print(
                    f"\t[{cleaned_site}] found no matching jobs at {cleaned_site_v2}\n"
                )
    finally:
        await page.close()
