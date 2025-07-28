import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from typing import Optional, List
from playwright.async_api import async_playwright, BrowserContext, Page

"""
MCP Browser Automation Server - Comprehensive Tool Guide

This server provides a complete browser automation toolkit with the following tools:

WORKFLOW:
1. navigate() - Initialize browser session
2. navigate_to_url() - Go to specific website
3. click() / fill() - Interact with page elements
4. screenshot() - Capture visual evidence
5. eval() - Execute custom JavaScript
6. close() - Clean up resources

TOOL PURPOSES:

NAVIGATION TOOLS:
- navigate(): Browser initialization and switching
- navigate_to_url(): Advanced navigation with options

INTERACTION TOOLS:
- click(): Click buttons, links, and interactive elements
- fill(): Fill forms and input fields

UTILITY TOOLS:
- screenshot(): Visual documentation and evidence
- eval(): Custom JavaScript execution
- close(): Resource cleanup

BROWSER SUPPORT:
- Chrome (chromium): Fast, good compatibility
- Firefox: Privacy-focused, good for testing
- WebKit (Safari): iOS/macOS compatibility

BEST PRACTICES:
1. Always start with navigate() to initialize browser
2. Use navigate_to_url() for reliable page loading
3. Use click() with text for flexible element targeting
4. Use fill() for form automation
5. Use screenshot() for documentation
6. Always close() when done

COMMON USE CASES:
- Web scraping and data extraction
- Form automation and testing
- Website testing and validation
- Visual documentation
- API testing with browser automation
- E-commerce automation
- Social media automation

EXAMPLE USAGE PATTERNS:

1. BASIC WEBSITE VISIT:
   navigate({"browser": "chromium"})
   navigate_to_url({"url": "https://example.com"})
   screenshot({"selector": "body"})
   close({"dummy": "done"})

2. FORM AUTOMATION:
   navigate({"browser": "firefox"})
   navigate_to_url({"url": "https://example.com/login"})
   fill({"selector": "input[name='username']", "value": "user@example.com"})
   fill({"selector": "input[name='password']", "value": "password123"})
   click({"text": "Login"})
   screenshot({"selector": ".dashboard"})

3. E-COMMERCE AUTOMATION:
   navigate({"browser": "chromium"})
   navigate_to_url({"url": "https://shop.example.com"})
   click({"text": "Search"})
   fill({"selector": "#search-input", "value": "laptop"})
   click({"text": "Add to Cart"})
   screenshot({"selector": ".cart-summary"})

4. DATA EXTRACTION:
   navigate({"browser": "webkit"})
   navigate_to_url({"url": "https://data.example.com"})
   eval({"script": "return document.querySelectorAll('.item').length"})
   screenshot({"selector": ".data-table"})

5. API TESTING WITH BROWSER:
   navigate({"browser": "chromium"})
   navigate_to_url({
       "url": "https://api.example.com/data",
       "extra_http_headers": {"Authorization": "Bearer token123"}
   })
   eval({"script": "return JSON.parse(document.body.textContent)"})

6. SLOW-LOADING PAGE:
   navigate({"browser": "firefox"})
   navigate_to_url({
       "url": "https://slow-site.com",
       "timeout": 60000,
       "wait_until": "networkidle",
       "wait_for_selector": "#content-loaded"
   })
   screenshot({"selector": "body"})

7. DYNAMIC CONTENT:
   navigate({"browser": "chromium"})
   navigate_to_url({
       "url": "https://spa.example.com",
       "wait_for_text": "Content Loaded"
   })
   click({"text": "Load More"})
   screenshot({"selector": ".content-area"})

COMMON SELECTORS:
- Buttons: "button", "input[type='submit']", ".btn"
- Links: "a", "a[href*='login']"
- Forms: "input[name='username']", "#email", ".search-input"
- Content: ".content", "#main", "article"
- Navigation: "nav", ".menu", "#header"

ERROR HANDLING:
- Element not found: Use different selector or text-based clicking
- Timeout: Increase timeout or use different wait condition
- Browser issues: Try different browser engine
- JavaScript errors: Check script syntax and browser compatibility
"""

app = FastAPI()
mcp = FastApiMCP(app)

playwright = None
browser_context: Optional[BrowserContext] = None
page: Optional[Page] = None
current_browser: str = "chromium"  # Track current browser

USER_DATA_DIR = os.path.expanduser("~/.playwright-profile")

class BrowserInput(BaseModel):
    """
    Input model for browser initialization.
    
    Use this to specify which browser engine to use for automation.
    Each browser has different characteristics:
    - chromium: Fast, good compatibility, Chrome-based
    - firefox: Privacy-focused, good for testing
    - webkit: Safari engine, good for iOS/macOS testing
    """
    browser: Optional[str] = "firefox"  # "chromium", "firefox", or "webkit"

class NavigateInput(BaseModel):
    """
    Input model for basic browser navigation.
    
    Use this to initialize a browser session and prepare for automation.
    """
    browser: Optional[str] = "chromium"  # "chromium", "firefox", "webkit", etc.

class ClickInput(BaseModel):
    """
    Input model for clicking elements on web pages.
    
    You can click elements using either:
    - selector: CSS selector for precise targeting
    - text: Visible text content for flexible targeting
    
    Examples:
    - selector: "button.submit", "#login-btn", "a[href*='login']"
    - text: "Login", "Submit", "Next", "Add to Cart"
    """
    selector: Optional[str] = None
    text: Optional[str] = None  # Visible text to search for

class FillInput(BaseModel):
    """
    Input model for filling form fields.
    
    Use CSS selectors to target specific input fields:
    - input[name='username'] - targets input with name="username"
    - #email - targets element with id="email"
    - .search-input - targets element with class="search-input"
    """
    selector: str
    value: str

class ScreenshotInput(BaseModel):
    """
    Input model for taking screenshots.
    
    Leave selector empty to capture entire page, or specify a selector
    to capture only a specific element or section.
    """
    selector: Optional[str] = None

class EvalInput(BaseModel):
    """
    Input model for executing JavaScript code.
    
    Use this for custom automation tasks, data extraction, or
    complex interactions that require JavaScript execution.
    """
    script: str

class CloseInput(BaseModel):
    """
    Input model for closing browser sessions.
    
    This is a simple model with a dummy parameter for MCP compatibility.
    """
    dummy: Optional[str] = None  # Dummy parameter for MCP compatibility

class NavigateToUrlInput(BaseModel):
    """
    Input model for advanced URL navigation with options.
    
    This provides comprehensive control over navigation behavior:
    - Custom timeouts for slow pages
    - Wait conditions for dynamic content
    - Custom headers for APIs or authentication
    - Element/text waiting for better reliability
    
    Wait conditions:
    - "load": Wait for load event (default)
    - "domcontentloaded": Wait for DOM ready
    - "networkidle": Wait for network to be idle
    
    Examples:
    - Basic: {"url": "https://example.com"}
    - With timeout: {"url": "https://slow-site.com", "timeout": 60000}
    - With headers: {"url": "https://api.example.com", "extra_http_headers": {"Authorization": "Bearer token"}}
    - With wait: {"url": "https://spa.example.com", "wait_for_selector": "#content-loaded"}
    """
    url: str
    browser: Optional[str] = "chromium"
    timeout: Optional[int] = 30000  # milliseconds
    wait_until: Optional[str] = "load"  # "load", "domcontentloaded", "networkidle"
    headers: Optional[dict] = None
    extra_http_headers: Optional[dict] = None
    wait_for_selector: Optional[str] = None
    wait_for_text: Optional[str] = None

async def get_browser_context(browser_name: str = None) -> Page:
    global playwright, browser_context, page, current_browser
    
    # Use current browser if no specific browser requested
    if browser_name is None:
        browser_name = current_browser
    
    # If already opened and valid with the same browser
    if page and not page.is_closed() and current_browser == browser_name:
        return page
    
    # Close existing browser if different browser requested
    if browser_context and current_browser != browser_name:
        await browser_context.close()
        if playwright:
            await playwright.stop()
        browser_context = None
        playwright = None
        page = None
    
    # Start new browser if needed
    if not playwright:
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
    current_browser = browser_name
    return page

@app.post("/navigate", operation_id="navigate")
async def navigate(input: NavigateInput):
    """
    Initialize and open a specific browser instance.
    
    Use this tool when you need to:
    - Start a fresh browser session
    - Switch between different browsers (Chrome, Firefox, WebKit)
    - Prepare for web automation tasks
    
    Parameters:
    - browser: Choose between "chromium" (Chrome), "firefox", or "webkit" (Safari)
    
    Returns: Browser initialization status
    """
    try:
        page = await get_browser_context(input.browser)
        await page.goto("about:blank")
        return {"status": "success", "message": f"Opened browser: {input.browser}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/click", operation_id="click")
async def click(input: ClickInput):
    """
    Click on elements on the current web page.
    
    Use this tool when you need to:
    - Click on buttons, links, or interactive elements
    - Navigate through website menus and navigation
    - Submit forms
    - Interact with web applications
    - Click on elements by their text content when selectors are unknown
    
    Parameters:
    - selector: CSS selector to target specific element (e.g., "button.submit", "#login-btn")
    - text: Visible text to search for and click (e.g., "Login", "Submit", "Next")
    
    Note: If multiple elements match, the first one will be clicked.
    Returns: Confirmation of click action
    """
    try:
        # Use the current browser context (works with any browser)
        page = await get_browser_context()  # This will use existing context if available
        
        if input.selector:
            # Check if element exists before clicking
            element = page.locator(input.selector)
            count = await element.count()
            
            if count == 0:
                raise HTTPException(status_code=400, detail=f"Element with selector '{input.selector}' not found on the page.")
            
            # Click the first element if multiple found
            await element.first.click()
            return f"Clicked first element matching {input.selector}"
        elif input.text:
            # Try to click using visible text via JavaScript
            script = f"""
            (function() {{
                var el = [...document.querySelectorAll('a,button,input[type="button"],input[type="submit"]')].find(e => 
                    e.textContent && e.textContent.trim().toLowerCase().includes('{input.text.lower()}')
                );
                if (el) {{
                    el.click();
                    return "Clicked: " + el.textContent.trim();
                }} else {{
                    return "No element found with text: " + "{input.text}";
                }}
            }})();
            """
            result = await page.evaluate(script)
            return result
        else:
            raise HTTPException(status_code=400, detail="Either selector or text must be provided.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Click failed: {str(e)}")

@app.post("/fill", operation_id="fill")
async def fill(input: FillInput):
    """
    Fill form fields with text input.
    
    Use this tool when you need to:
    - Fill out login forms
    - Enter data in search boxes
    - Complete registration forms
    - Input text in any form field
    - Automate form submissions
    
    Parameters:
    - selector: CSS selector for the input field (e.g., "input[name='username']", "#email")
    - value: Text to enter in the field
    
    Returns: Confirmation of fill action
    """
    try:
        page = await get_browser_context()  # Use current browser context
        
        # Check if element exists before filling
        element = page.locator(input.selector)
        count = await element.count()
        
        if count == 0:
            raise HTTPException(status_code=400, detail=f"Element with selector '{input.selector}' not found on the page.")
        
        # Fill the element
        await element.fill(input.value)
        return f"Filled {input.selector} with '{input.value}'"
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fill failed: {str(e)}")

@app.post("/screenshot", operation_id="screenshot")
async def screenshot(input: ScreenshotInput):
    """
    Take screenshots of the current web page or specific elements.
    
    Use this tool when you need to:
    - Capture visual evidence of web pages
    - Document website states or errors
    - Save visual content for analysis
    - Capture specific elements (forms, products, etc.)
    - Create visual documentation
    
    Parameters:
    - selector: Optional CSS selector to screenshot specific element (e.g., ".product-image", "#content")
    
    Returns: File path where screenshot is saved
    """
    page = await get_browser_context()  # Use current browser context
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
    """
    Execute custom JavaScript code on the current web page.
    
    Use this tool when you need to:
    - Extract data from web pages
    - Manipulate page content dynamically
    - Get page information (title, URL, etc.)
    - Perform complex interactions not covered by other tools
    - Access browser APIs and DOM elements
    - Execute custom automation scripts
    
    Parameters:
    - script: JavaScript code to execute
    
    Returns: Result of JavaScript execution
    """
    page = await get_browser_context()  # Use current browser context
    result = await page.evaluate(input.script)
    return result

@app.post("/close", operation_id="close")
async def close(input: CloseInput):
    """
    Close the current browser and clean up resources.
    
    Use this tool when you need to:
    - End a browser automation session
    - Free up system resources
    - Prepare for a new browser session
    - Clean up after completing tasks
    
    Parameters:
    - dummy: Dummy parameter for MCP compatibility
    
    Returns: Confirmation of browser closure
    """
    global browser_context, playwright, page, current_browser
    if browser_context:
        await browser_context.close()
        if playwright:
            await playwright.stop()
        browser_context = None
        playwright = None
        page = None
        current_browser = "chromium"  # Reset to default
        return "Browser closed"
    return "No browser running"

@app.post("/navigate_to_url", operation_id="navigate_to_url")
async def navigate_to_url(input: NavigateToUrlInput):
    """
    Navigate to a specific URL with advanced options for web automation.
    
    Use this tool when you need to:
    - Visit a specific website or page
    - Navigate with custom headers (for APIs, authentication)
    - Wait for specific elements to load
    - Handle slow-loading pages with custom timeouts
    - Navigate to pages that require specific load conditions
    
    Parameters:
    - url: The target URL to navigate to
    - browser: Browser type (chromium, firefox, webkit)
    - timeout: Custom timeout in milliseconds (default: 30000ms)
    - wait_until: Page load condition ("load", "domcontentloaded", "networkidle")
    - extra_http_headers: Custom headers for the request
    - wait_for_selector: Wait for specific element to appear
    - wait_for_text: Wait for specific text to appear on page
    
    Returns: Navigation details including URL, title, and status
    """
    try:
        page = await get_browser_context(input.browser)
        
        # Set extra headers if provided
        if input.extra_http_headers:
            await page.set_extra_http_headers(input.extra_http_headers)
        
        # Determine wait until condition
        wait_until_map = {
            "load": "load",
            "domcontentloaded": "domcontentloaded", 
            "networkidle": "networkidle"
        }
        wait_until = wait_until_map.get(input.wait_until, "load")
        
        # Navigate to URL with timeout and wait condition
        response = await page.goto(
            input.url,
            timeout=input.timeout,
            wait_until=wait_until
        )
        
        # Wait for specific selector if provided
        if input.wait_for_selector:
            await page.wait_for_selector(input.wait_for_selector, timeout=input.timeout)
        
        # Wait for specific text if provided
        if input.wait_for_text:
            await page.wait_for_function(
                f'document.body.textContent.includes("{input.wait_for_text}")',
                timeout=input.timeout
            )
        
        # Get page information
        title = await page.title()
        current_url = page.url
        
        return {
            "status": "success",
            "url": current_url,
            "title": title,
            "response_status": response.status if response else None,
            "wait_until": wait_until,
            "timeout_used": input.timeout
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Navigation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    mcp = FastApiMCP(app, include_operations=["navigate", "navigate_to_url", "click", "fill", "screenshot", "eval", "close"])
    mcp.mount()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
