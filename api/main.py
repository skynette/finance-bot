import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize Django FIRST
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings")
import django
django.setup()

# Now import your routers
from api.routers import telegram, finance

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(telegram.router)
# app.include_router(finance.router)