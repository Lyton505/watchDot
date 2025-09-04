from playwright.async_api import expect
import re
import asyncio
from custom_handlers.common import search_terms


async def handle_bloomberg(page, site):
    print("Handling Bloomberg...")

    # handle search for internships
    await page.get_by_role("combobox", name="Experience Level").click()
    await page.get_by_role("searchbox", name="Experience Level").fill("intern")
    option = page.get_by_role("option", name=re.compile(r"\bInternships\b", re.I))
    await expect(option).to_be_visible(timeout=5000)
    await option.first.click()

    # handle search for business area
    await ensure_business_area(page, "Engineering and CTO")

    # submit form
    await page.get_by_role("button", name="Submit").click()

    await asyncio.sleep(2)

    text = await page.evaluate("() => document.documentElement.innerText")
    await search_terms(site, text)


async def ensure_business_area(
    page, value_text="Engineering and CTO", must_be_only=False
):
    label = "Business Area"
    container = page.locator("label:has-text('%s')" % label).locator("xpath=..").first

    # If you require ONLY this value, clear existing selections (uses Select2's clear '×')
    if must_be_only:
        clear_btn = container.locator(".select2-selection__clear")
        if await clear_btn.is_visible():
            await clear_btn.click()

    # If the chip is already present, we're done
    chip = container.locator(".select2-selection__choice", has_text=value_text).first
    if await chip.count() > 0:
        return

    # Open the combobox and type
    await container.locator(".select2-selection").click()
    sb = container.get_by_role("searchbox")
    await sb.fill(value_text)

    # Wait for results and pick the match
    results = page.locator(".select2-results__option")
    await expect(results.first).to_be_visible(timeout=7000)

    target = results.filter(
        has_text=re.compile(rf"\b{re.escape(value_text)}\b", re.I)
    ).first
    if await target.count() == 0:
        target = results.filter(has_text=re.compile(re.escape(value_text), re.I)).first

    await target.scroll_into_view_if_needed()
    await target.click()
