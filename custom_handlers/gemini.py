from custom_handlers.common import search_terms


async def handle_gemini(page, site):
    software_engineering_element = page.locator("#software-engineering")
    await software_engineering_element.click()

    text = await software_engineering_element.inner_text()

    await search_terms(site, text)
