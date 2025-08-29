import asyncio
from playwright.async_api import async_playwright
import json
from worker import job_worker


async def main():
    with open("sites.json", "r") as f:
        sites = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        sem = asyncio.Semaphore(3)

        async def wrapped(site):
            async with sem:
                await job_worker(site, browser)

        await asyncio.gather(*(wrapped(s) for s in sites))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
