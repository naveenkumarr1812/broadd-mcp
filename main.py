from selenium import webdriver
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

# Define a root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the FLOCARD server!"}


# Fetch Data
@app.get("/fetch/{query}", operation_id="fetch_data")
async def fetch_data(query: str):
    driver = webdriver.Chrome()
    driver.get(f"http://google.com/{query}")
    time.sleep(5)
    driver.quit()
    return {"message": "Data fetched successfully!"}


# Run the FastAPI application
if __name__ == "__main__":
    mcp = FastApiMCP(app, include_operations=["fetch_data"])
    mcp.mount()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)