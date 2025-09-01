import asyncio
from playwright.async_api import async_playwright
import json
from custom_handlers.db_manager import init_db
from worker import job_worker
from custom_handlers.common import extract_root_domain


async def main():
    print("\n\n ### New run: Loading sites from sites.json...")
    with open("sites.json", "r") as f:
        sites = json.load(f)

    print("Initializing database...")
    await init_db()

    print(f"Loaded {len(sites)} sites. Initializing browser...\n")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, args=["--disable-gpu", "--use-gl=swiftshader"]
        )

        context_browser = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/140.0.7339.16 Safari/537.36",
            locale="en-US",
            viewport={"width": 1280, "height": 800},
        )

        sem = asyncio.Semaphore(3)

        async def wrapped(site):
            async with sem:
                print(f"Processing {extract_root_domain(site)}...")
                await job_worker(site, context_browser)

        await asyncio.gather(*(wrapped(s) for s in sites))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
