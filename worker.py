import re

# List of job titles you want to detect
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

        text = await page.evaluate("() => document.documentElement.innerText")

        matches = []
        for term, pattern in zip(TERMS, PATTERNS):
            if pattern.search(text):
                matches.append(term)
                if term == "intern":
                    print(f"Special term matched: {term} at {site}")

        if matches:
            print(f"found match(es): {', '.join(matches)} at {site}")
        else:
            print(f"found no matching jobs at {site}")
    finally:
        await page.close()
