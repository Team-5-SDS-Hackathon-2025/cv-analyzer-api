import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# --- Load Environment Variables ---
# This line loads the .env file at the very start, making os.getenv()
# available to the entire application, including any imported modules.
load_dotenv()

from app.api import analyze as analyze_module

app = FastAPI(title="CV Analysis Advisor")

app.include_router(analyze_module.router, prefix="/api")

# serve static frontend (index.html)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

