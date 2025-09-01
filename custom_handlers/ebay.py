import asyncio
from custom_handlers.common import search_terms
from playwright.async_api import expect, TimeoutError
import re


async def handle_ebay(page, site):
    await handle_cookie_popup(page)

    try:
        await select_first_country_result(page)
        jobs_text = await page.evaluate(
            """
    () => {
        const jobsList = document.querySelector('.phs-jobs-list');
        return jobsList ? jobsList.innerText : '';
    }
"""
        )

        await search_terms(site, jobs_text)
    except Exception:
        pass

    return


async def handle_cookie_popup(page):
    try:
        cookie_selectors = [
            '[aria-label="cookies message"] button[aria-label*="accept"]',
            ".phs-cookie-popup-area button",
            'button:has-text("Accept")',
            'button:has-text("Accept All")',
            'button:has-text("I Accept")',
            'button:has-text("Allow")',
            'button:has-text("Agree")',
            'button[id*="cookie"][id*="accept"]',
            ".cookie-banner button",
            "#cookie-banner button",
            '[data-ph-id*="cookie"] button',
        ]

        for selector in cookie_selectors:
            cookie_btn = page.locator(selector).first
            if await cookie_btn.count() > 0:
                await cookie_btn.click(timeout=5000)
                await page.wait_for_timeout(1000)
                return True

        return False
    except Exception:
        return False


async def select_first_country_result(page, query="United States Of America"):
    toggle = page.locator("#CountryAccordion")

    if await toggle.count() > 0:
        if (await toggle.get_attribute("aria-expanded") or "").lower() != "true":
            await toggle.click()
            await expect(toggle).to_have_attribute(
                "aria-expanded", "true", timeout=5000
            )

        await page.wait_for_timeout(1000)

        facet_input = page.locator("#facetInput_1")

        if await facet_input.count() > 0:
            await facet_input.fill("")
            await facet_input.fill("United States Of America")

            await page.wait_for_timeout(1000)

            results_list = page.locator('[data-ph-at-id="facet-results-list"]')

            if await results_list.count() > 0:
                try:
                    usa_label = results_list.locator(
                        'label:has-text("United States")'
                    ).first
                    if await usa_label.count() > 0:
                        await usa_label.click(force=True)

                        await asyncio.sleep(5)
                        return True
                except Exception:
                    pass

                try:
                    usa_checkbox = results_list.locator(
                        'input[data-ph-at-text*="United States"]'
                    )
                    if await usa_checkbox.count() > 0:
                        await usa_checkbox.evaluate("node => node.checked = true")
                        return True
                except Exception:
                    pass

                try:
                    usa_text = results_list.get_by_text(
                        re.compile(r"United States", re.I)
                    )
                    if await usa_text.count() > 0:
                        await usa_text.click(force=True)
                        return True
                except Exception:
                    pass

    return False
