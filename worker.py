async def job_worker(site, browser):
    page = await browser.new_page()
    await page.goto(site, wait_until="networkidle")
    content = await page.content()
    print("Content is:", content[:200])
    await page.close()
