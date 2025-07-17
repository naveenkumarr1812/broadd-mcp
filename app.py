from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import httpx
from fastapi import FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
import os
import json
from typing import Optional
import traceback
import time

# Initialize FastAPI app
app = FastAPI()

# Initialize MCP


# Define a root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the FLOCARD server!"}


# MCP tool: navigate and search on Google
class SearchRequest(BaseModel):
    query: str


# Optional normal route
@app.get("/fetch/{query}", operation_id="fetch_data")
def navigate_and_search(query: str):
    try:
        driver = webdriver.Chrome()
        driver.get("https://www.google.com")
        time.sleep(2)
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(15)
        return {"message": f"Successfully searched '{query}' on Google"}
    except Exception as e:
        return {"error": str(e)}


# Run the FastAPI application
if __name__ == "__main__":
    mcp = FastApiMCP(app, include_operations=["fetch_data"])
    mcp.mount()
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

