import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

# --- Load Environment Variables ---
# This line loads the .env file at the very start, making os.getenv()
# available to the entire application, including any imported modules.
load_dotenv()

from app.api import analyze as analyze_module

app = FastAPI(
    title="CV Analysis Advisor",
    description=""
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(analyze_module.router, prefix="/api")

# serve static frontend (index.html)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

