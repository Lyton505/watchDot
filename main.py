import asyncio
from playwright.async_api import async_playwright
import json
from worker import job_worker


async def main():
    with open("sites.json", "r") as f:
        sites = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for i in range(0, len(sites), 3):
            batch = sites[i : i + 3]
            tasks = [job_worker(site, browser) for site in batch]
            await asyncio.gather(*tasks)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
