import asyncio
from custom_handlers.common import search_terms
from playwright.async_api import expect, TimeoutError
import re
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_ebay(page, site):
    # First handle cookie popup if it exists
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
    except Exception as e:
        logger.error(f"Error in country selection: {str(e)}")

    return


async def handle_cookie_popup(page):
    """Handle any cookie consent popups that might block interactions"""
    try:
        # Common cookie accept button selectors
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
                logger.info(f"Found cookie consent button with selector: {selector}")
                await cookie_btn.click(timeout=5000)
                logger.info("Clicked cookie consent button")
                await page.wait_for_timeout(1000)  # Wait for popup to disappear
                return True

        logger.info("No cookie popup detected or it was already handled")
        return False
    except Exception as e:
        logger.warning(f"Error handling cookie popup: {str(e)}")
        return False


async def select_first_country_result(page, query="United States Of America"):
    # Find the country filter button
    toggle = page.locator("#CountryAccordion")

    # Check if the toggle exists and is visible
    if await toggle.count() > 0:
        logger.info("Found country accordion")

        # Open only if collapsed
        if (await toggle.get_attribute("aria-expanded") or "").lower() != "true":
            logger.info("Expanding country accordion")
            await toggle.click()
            await expect(toggle).to_have_attribute(
                "aria-expanded", "true", timeout=5000
            )

        # Wait a moment for animations to complete
        await page.wait_for_timeout(1000)

        # Look for the search input - based on the HTML, the ID is "facetInput_1"
        facet_input = page.locator("#facetInput_1")

        if await facet_input.count() > 0:
            logger.info("Found country search input")
            # Clear any existing text first
            await facet_input.fill("")
            await facet_input.fill("United States Of America")

            # Wait for search results to appear
            await page.wait_for_timeout(1000)

            # The results list has a specific attribute data-ph-at-id="facet-results-list"
            results_list = page.locator('[data-ph-at-id="facet-results-list"]')

            if await results_list.count() > 0:
                logger.info("Found results list")

                # Instead of trying to click the checkbox directly, try clicking the label first
                # The <span class="checkbox"> is intercepting clicks
                try:
                    # Try clicking the label containing the text "United States" (more reliable)
                    usa_label = results_list.locator(
                        'label:has-text("United States")'
                    ).first
                    if await usa_label.count() > 0:
                        logger.info("Found USA label, clicking it")
                        await usa_label.click(
                            force=True
                        )  # Use force to bypass intercepting elements

                        await asyncio.sleep(5)
                        return True
                except Exception as e:
                    logger.warning(f"Error clicking label: {str(e)}")

                # If label click fails, try other approaches
                try:
                    usa_checkbox = results_list.locator(
                        'input[data-ph-at-text*="United States"]'
                    )
                    if await usa_checkbox.count() > 0:
                        logger.info("Found USA checkbox")
                        await usa_checkbox.evaluate(
                            "node => node.checked = true"
                        )  # Using JavaScript to check
                        return True
                except Exception as e:
                    logger.warning(f"Error checking checkbox: {str(e)}")

                # Final attempt using text
                try:
                    usa_text = results_list.get_by_text(
                        re.compile(r"United States", re.I)
                    )
                    if await usa_text.count() > 0:
                        logger.info("Found USA by text, trying to click it")
                        await usa_text.click(force=True)
                        return True
                except Exception as e:
                    logger.warning(f"Error clicking text: {str(e)}")
            else:
                logger.warning("No results list found")
    else:
        logger.warning("Country accordion not found")

    logger.warning("Could not select USA country")
    return False
