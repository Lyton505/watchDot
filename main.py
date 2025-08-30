import asyncio
from playwright.async_api import async_playwright
import json
from custom_handlers.db_manager import init_db
from worker import job_worker
from custom_handlers.common import extract_root_domain


async def main():
    print("Loading sites from sites.json...")
    with open("sites.json", "r") as f:
        sites = json.load(f)

    print("Initializing database...")
    await init_db()

    print(f"Loaded {len(sites)} sites. Initializing browser...\n")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        sem = asyncio.Semaphore(3)

        async def wrapped(site):
            async with sem:
                print(f"Processing {extract_root_domain(site)}...")
                await job_worker(site, browser)

        await asyncio.gather(*(wrapped(s) for s in sites))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
