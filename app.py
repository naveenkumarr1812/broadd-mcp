import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from typing import Optional
from playwright.async_api import async_playwright, BrowserContext, Page

app = FastAPI()
mcp = FastApiMCP(app)

playwright = None
browser_context: Optional[BrowserContext] = None
page: Optional[Page] = None

USER_DATA_DIR = os.path.expanduser("~/.playwright-profile")

class BrowserInput(BaseModel):
    browser: Optional[str] = "firefox"  # "chromium", "firefox", or "webkit"

class NavigateInput(BaseModel):
    browser: Optional[str] = "chromium"  # "chromium", "firefox", "webkit", etc.

class ClickInput(BaseModel):
    selector: Optional[str] = None
    text: Optional[str] = None  # Visible text to search for

class FillInput(BaseModel):
    selector: str
    value: str

class ScreenshotInput(BaseModel):
    selector: Optional[str] = None

class EvalInput(BaseModel):
    script: str

class CloseInput(BaseModel):
    pass

async def get_browser_context(browser_name: str) -> Page:
    global playwright, browser_context, page

    # If already opened and valid
    if page and not page.is_closed():
        return page

    playwright = await async_playwright().start()

    browser_name = browser_name.lower()
    if browser_name == "firefox":
        browser_type = playwright.firefox
    elif browser_name == "webkit":
        browser_type = playwright.webkit
    else:
        browser_type = playwright.chromium

    DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
    browser_context = await browser_type.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,
        accept_downloads=True,
        downloads_path=DOWNLOADS_DIR,
    )
    page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
    return page

@app.post("/navigate", operation_id="navigate")
async def navigate(input: NavigateInput):
    try:
        page = await get_browser_context(input.browser)
        await page.goto("about:blank")
        return {"status": "success", "message": f"Opened browser: {input.browser}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/click", operation_id="click")
async def click(input: ClickInput):
    page = await get_browser_context("chromium")
    try:
        if input.selector:
            # Try to click using the selector
            await page.click(input.selector)
            return f"Clicked element {input.selector}"
        elif input.text:
            # Try to click using visible text via JavaScript
            script = f"""
            var el = [...document.querySelectorAll('a,button')].find(e => e.textContent.trim().toLowerCase() === '{input.text.lower()}');
            if (el) el.click();
            """
            await page.evaluate(script)
            return f"Clicked element with text '{input.text}'"
        else:
            raise HTTPException(status_code=400, detail="Either selector or text must be provided.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Click failed: {str(e)}")

@app.post("/fill", operation_id="fill")
async def fill(input: FillInput):
    page = await get_browser_context("chromium")
    await page.fill(input.selector, input.value)
    return f"Filled {input.selector} with '{input.value}'"

@app.post("/screenshot", operation_id="screenshot")
async def screenshot(input: ScreenshotInput):
    page = await get_browser_context("chromium")
    DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
    filename = f"screenshot_{uuid.uuid4().hex[:6]}.png"
    filepath = os.path.join(DOWNLOADS_DIR, filename)
    if input.selector:
        await page.locator(input.selector).screenshot(path=filepath)
    else:
        await page.screenshot(path=filepath)
    return f"Screenshot saved to {filepath}"

@app.post("/eval", operation_id="eval")
async def eval(input: EvalInput):
    page = await get_browser_context("chromium")
    result = await page.evaluate(input.script)
    return result

@app.post("/close", operation_id="close")
async def close(input: CloseInput):
    global browser_context, playwright, page
    if browser_context:
        await browser_context.close()
        if playwright:
            await playwright.stop()
        browser_context = None
        playwright = None
        page = None
        return "Browser closed"
    return "No browser running"

if __name__ == "__main__":
    import uvicorn
    mcp = FastApiMCP(app, include_operations=["navigate", "click", "fill", "screenshot", "eval", "close"])
    mcp.mount()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
