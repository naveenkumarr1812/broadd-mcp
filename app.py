import os
import uuid
import platform
from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from typing import Optional
from playwright.async_api import async_playwright, BrowserContext, Page

app = FastAPI()
mcp = FastApiMCP(app)

playwright = None
browser: Optional[BrowserContext] = None
page: Optional[Page] = None

USER_DATA_DIR = os.path.expanduser("~/.playwright-profile")

def detect_default_browser_path() -> Optional[str]:
    system = platform.system()
    possible_paths = []

    if system == "Windows":
        # Brave, Chrome, Edge (priority order)
        possible_paths += [
            "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        ]
    elif system == "Linux":
        possible_paths += [
            "/usr/bin/brave-browser",
            "/usr/bin/google-chrome",
            "/usr/bin/microsoft-edge",
            "/usr/bin/firefox",
        ]
    elif system == "Darwin":  # macOS
        possible_paths += [
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Firefox.app/Contents/MacOS/firefox",
        ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None

class NavigateInput(BaseModel):
    query: str

class ClickInput(BaseModel):
    selector: str

class FillInput(BaseModel):
    selector: str
    value: str

class ScreenshotInput(BaseModel):
    selector: Optional[str] = None

class EvalInput(BaseModel):
    script: str

class CloseInput(BaseModel):
    pass

async def get_browser() -> Page:
    global playwright, browser, page
    if page and not page.is_closed():
        return page

    browser_path = detect_default_browser_path()
    if not browser_path:
        raise HTTPException(status_code=500, detail="Could not detect any supported browser path.")

    playwright = await async_playwright().start()

    # Determine browser type based on path
    if "firefox" in browser_path.lower():
        browser_type = playwright.firefox
    else:
        browser_type = playwright.chromium

    browser = await browser_type.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,
        executable_path=browser_path,
    )
    page = browser.pages[0] if browser.pages else await browser.new_page()
    return page

@app.post("/navigate", operation_id="navigate")
async def navigate(input: NavigateInput):
    try:
        page = await get_browser()
        await page.goto("https://www.google.com")
        await page.fill("input[name='q']", input.query)
        await page.keyboard.press("Enter")
        return {"status": "success", "message": f"Searched for '{input.query}' on Google"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/click", operation_id="click")
async def click(input: ClickInput):
    page = await get_browser()
    await page.click(input.selector)
    return f"Clicked element {input.selector}"

@app.post("/fill", operation_id="fill")
async def fill(input: FillInput):
    page = await get_browser()
    await page.fill(input.selector, input.value)
    return f"Filled {input.selector} with '{input.value}'"

@app.post("/screenshot", operation_id="screenshot")
async def screenshot(input: ScreenshotInput):
    page = await get_browser()
    filename = f"screenshot_{uuid.uuid4().hex[:6]}.png"
    filepath = os.path.join(os.getcwd(), filename)
    if input.selector:
        await page.locator(input.selector).screenshot(path=filepath)
    else:
        await page.screenshot(path=filepath)
    return f"Screenshot saved to {filename}"

@app.post("/eval", operation_id="eval")
async def eval(input: EvalInput):
    page = await get_browser()
    result = await page.evaluate(input.script)
    return result

@app.post("/close", operation_id="close")
async def close(input: CloseInput):
    global browser, playwright, page
    if browser:
        await browser.close()
        if playwright:
            await playwright.stop()
        browser = None
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
