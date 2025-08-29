# custom_handlers/duo.py


from custom_handlers.common import (
    extract_root_domain,
    extract_root_domain_v2,
    search_terms,
)


async def handle_duo(page, site):
    """
    Custom handler for Duolingo's careers page.
    Instead of scanning for job titles, look for the 'View all jobs' link.
    """
    try:
        # Wait for the anchor containing 'View all jobs'
        locator = page.locator("a:has-text('View all jobs')")
        cleaned_site = extract_root_domain(site)
        cleaned_site_v2 = extract_root_domain_v2(site)
        if await locator.count() > 0:
            href = await locator.first.get_attribute("href")
            url = page.url
            if href and href.startswith("/"):
                from urllib.parse import urljoin

                href = urljoin(url, href)

            print(f"\t[{cleaned_site}] found custom jobs link at {cleaned_site_v2}")
            text = await page.evaluate("() => document.documentElement.innerText")
            await search_terms(site, text)
            return True
        else:
            print(f"\t[{cleaned_site}] no jobs link found at {cleaned_site_v2}")
            return False
    except Exception as e:
        print(f"[{cleaned_site}] error handling {cleaned_site_v2}: {e}")
        return False
