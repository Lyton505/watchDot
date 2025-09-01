from custom_handlers.common import search_terms


async def handle_intuit(page, site):
    search_box = page.locator("input.search-keyword")

    await search_box.fill("intern")
    await search_box.press("Enter")

    await page.get_by_role("button", name="Country").click()

    await page.get_by_label("United States").click()

    await page.wait_for_selector("#search-results-list")

    # Extract text from the specific section
    section = page.locator("#search-results-list")
    text = await section.inner_text()

    await search_terms(site, text)
