# Broadd MCP Server

A powerful Model Context Protocol (MCP) server for browser automation and web interaction. This server provides comprehensive tools for web scraping, form automation, testing, and general web interaction tasks.

## Features

- 🌐 **Browser Control**: Initialize and manage browser instances (Chromium, Firefox, WebKit)
- 🔗 **Advanced Navigation**: Navigate to URLs with custom headers, timeouts, and wait conditions
- 🖱️ **Element Interaction**: Click buttons, links, and interactive elements
- 📝 **Form Automation**: Fill form fields with text input
- 📸 **Screenshot Capture**: Take screenshots of pages or specific elements
- 💻 **JavaScript Execution**: Execute custom JavaScript code on web pages
- 🧹 **Resource Management**: Clean browser sessions and resources

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `click` | Click on elements using CSS selectors or text | `selector`, `text` |
| `close` | Close browser and clean up resources | `dummy` |
| `eval` | Execute JavaScript code on the current page | `script` |
| `fill` | Fill form fields with text input | `selector`, `value` |
| `navigate` | Initialize browser instance | `browser` |
| `navigate_to_url` | Navigate to URL with advanced options | `url`, `browser`, `timeout`, `wait_until`, `extra_http_headers`, `wait_for_selector`, `wait_for_text` |
| `screenshot` | Take screenshots of page or elements | `selector` |

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install from GitHub

1. **Clone the repository:**
   ```bash
   git clone https://github.com/naveenkumarr1812/broadd-mcp.git
   cd broadd-mcp
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

### Quick Start

1. **Start the MCP server:**
   ```bash
   python app.py
   ```

2. **Configure your MCP client** by adding the server to your `mcp_config.json` file:
   ```json
   {
       "mcpServers": {
         "broadd": {
           "serverUrl": "http://localhost:8000/mcp"
         }
       }
   }
   ```


3. **Restart your MCP client** (e.g., Windsurf) to load the new server configuration

## Usage Examples

Here are real-world examples showing what users ask and how the system responds using broadd MCP tools:

### 1. Browser Initialization

**User Prompt:** *"Open a Chrome browser for me"*

**System Response:** Uses `navigate` tool
```json
{
  "tool": "navigate",
  "parameters": {"browser": "chromium"}
}
```
**Result:** Browser opens successfully

---

### 2. Website Navigation

**User Prompt:** *"Go to example.com and wait for it to fully load"*

**System Response:** Uses `navigate_to_url` tool
```json
{
  "tool": "navigate_to_url",
  "parameters": {
    "url": "https://example.com",
    "timeout": 10000,
    "wait_until": "load"
  }
}
```
**Result:** Navigates to the website and waits for complete loading

---

### 3. Form Filling

**User Prompt:** *"Fill out the login form with username 'john_doe' and email 'john@example.com'"*

**System Response:** Uses `fill` tool multiple times
```json
[
  {
    "tool": "fill",
    "parameters": {
      "selector": "input[name='username']",
      "value": "john_doe"
    }
  },
  {
    "tool": "fill",
    "parameters": {
      "selector": "input[name='email']",
      "value": "john@example.com"
    }
  }
]
```
**Result:** Form fields are automatically filled with the specified values

---

### 4. Button Clicking

**User Prompt:** *"Click the Login button to submit the form"*

**System Response:** Uses `click` tool
```json
{
  "tool": "click",
  "parameters": {"text": "Login"}
}
```
**Result:** Clicks the button with "Login" text

---

### 5. Screenshot Capture

**User Prompt:** *"Take a screenshot of the current page"*

**System Response:** Uses `screenshot` tool
```json
{
  "tool": "screenshot",
  "parameters": {"selector": "body"}
}
```
**Result:** Captures and saves a screenshot of the entire page

---

### 6. Data Extraction

**User Prompt:** *"Extract all product names and prices from this e-commerce page"*

**System Response:** Uses `eval` tool with JavaScript
```json
{
  "tool": "eval",
  "parameters": {
    "script": "const products = []; document.querySelectorAll('.product').forEach(product => { products.push({ name: product.querySelector('.name').textContent, price: product.querySelector('.price').textContent }); }); JSON.stringify(products);"
  }
}
```
**Result:** Returns JSON data with all product information

---

### 7. Advanced Navigation with Headers

**User Prompt:** *"Navigate to the API dashboard with my authentication token"*

**System Response:** Uses `navigate_to_url` with custom headers
```json
{
  "tool": "navigate_to_url",
  "parameters": {
    "url": "https://api.example.com/dashboard",
    "extra_http_headers": {
      "Authorization": "Bearer your-token",
      "User-Agent": "Custom Bot 1.0"
    },
    "wait_for_selector": ".dashboard-loaded",
    "timeout": 15000
  }
}
```
**Result:** Navigates with authentication and waits for dashboard to load

---

### 8. Element-Specific Screenshot

**User Prompt:** *"Take a screenshot of just the product gallery section"*

**System Response:** Uses `screenshot` with specific selector
```json
{
  "tool": "screenshot",
  "parameters": {"selector": ".product-gallery"}
}
```
**Result:** Captures screenshot of only the specified element

---

### 9. Session Cleanup

**User Prompt:** *"Close the browser and clean up"*

**System Response:** Uses `close` tool
```json
{
  "tool": "close",
  "parameters": {"dummy": "cleanup"}
}
```
**Result:** Browser closes and resources are freed

---

## Configuration

### Browser Options

Supported browsers:
- `chromium` (default) - Google Chrome/Chromium
- `firefox` - Mozilla Firefox
- `webkit` - Safari WebKit

### Wait Conditions

- `load` - Wait for the load event (default)
- `domcontentloaded` - Wait for DOM to be ready
- `networkidle` - Wait for network to be idle

### Timeout Settings

- Default timeout: 30,000ms (30 seconds)
- Configurable per navigation request
- Recommended: 10,000-15,000ms for most sites

## Error Handling

The server provides detailed error messages for common scenarios:

- **Element not found**: When selectors don't match any elements
- **Timeout errors**: When pages take too long to load
- **Navigation failures**: When URLs are unreachable
- **JavaScript errors**: When eval scripts fail


### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Testing

To test the server functionality:

```bash
# Start the server
python app.py

# Test with your MCP client or use the examples above
```

## Troubleshooting

### Common Issues

1. **Browser not found**: Ensure Playwright browsers are installed
   ```bash
   playwright install
   ```

2. **Permission errors**: Make sure you have write permissions for screenshots

3. **Timeout issues**: Increase timeout values for slow-loading sites

4. **Element not found**: Verify CSS selectors are correct and elements exist

## License

This project is licensed under the MIT License - see the LICENSE file for details. [MIT License](LICENSE)

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing issues for solutions
- Review the documentation above

## Changelog

### v1.0.0
- Initial release
- Basic browser automation tools
- Form filling capabilities
- Screenshot functionality
- JavaScript execution support

---

**Happy automating! 🚀**