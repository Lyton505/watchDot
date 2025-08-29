# custom_handlers/duo.py
import re
from urllib.parse import urljoin, urlparse

JOBS_TXT = re.compile(r"view\s+all\s+jobs", re.I)
FREELANCE_TXT = re.compile(r"view\s+freelance\s+jobs", re.I)


async def _text_of(page):
    return await page.evaluate("() => document.documentElement.innerText")


async def _wait_jobs_ui(page):
    # Prefer concrete DOM waits over networkidle (SPA)
    selectors = [
        "#careers",
        "[id*=career]",
        "[class*=career]",
        "[data-testid*=job]",
        "[class*=job-card]",
        "a[href*='greenhouse.io']",
        "a[href*='lever.co']",
        "a[href*='ashbyhq.com']",
    ]
    for sel in selectors:
        try:
            await page.wait_for_selector(sel, timeout=6000)
            return True
        except Exception:
            continue
    # As a fallback, accept URL hint
    try:
        await page.wait_for_function(
            "() => /career|job/i.test(location.href)", timeout=4000
        )
        return True
    except Exception:
        return False


async def _click_maybe_new_tab(page, locator):
    """Click and return the page that now shows the jobs (same page or new tab)."""
    target = await locator.get_attribute("target")
    href = await locator.get_attribute("href")
    # Pre-resolve absolute URL to decide whether cross-origin likely opens new tab
    abs_url = urljoin(page.url, href) if href else None
    same_origin = False
    if abs_url:
        try:
            same_origin = urlparse(abs_url).netloc == urlparse(page.url).netloc
        except Exception:
            pass

    # If target=_blank or cross-origin, expect a new page
    if target == "_blank" or (abs_url and not same_origin):
        async with page.context.expect_page() as pinfo:
            await locator.click(force=True)
        newp = await pinfo.value
        await newp.wait_for_load_state("domcontentloaded")
        return newp

    # Otherwise assume same tab / hash / SPA
    await locator.click(force=True)
    return page


async def handle_duo(page, site, search_terms_fn):
    # Prefer accessible-name matching (robust to class changes)
    jobs_link = page.get_by_role("link", name=JOBS_TXT)
    # freelance_link = page.get_by_role("link", name=FREELANCE_TXT)

    # 1) Try "View all jobs" first (hash or internal route)
    if await jobs_link.count():
        dest_page = await _click_maybe_new_tab(page, jobs_link.first)
        # Hash case: wait for hash or careers section
        try:
            await dest_page.wait_for_function(
                "() => location.hash && location.hash.toLowerCase().includes('career')",
                timeout=3000,
            )
        except Exception:
            pass
        await _wait_jobs_ui(dest_page)
        text = await _text_of(dest_page)
        await search_terms_fn(site, text)
        return True

    # # 2) Fall back to "View freelance jobs" (external Breezy)
    # if await freelance_link.count():
    #     dest_page = await _click_maybe_new_tab(page, freelance_link.first)
    #     await _wait_jobs_ui(dest_page)
    #     text = await _text_of(dest_page)
    #     await search_terms_fn(site, text)
    #     return True

    # 3) Nothing matched
    print("\t[duolingo.com] no recognized jobs links found")
    return False
