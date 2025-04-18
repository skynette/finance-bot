import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize Django FIRST
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings")
import django
django.setup()

# Now import your routers
# from api.routers import finance
from api.routers import telegram
from api.routers.telegram import lifespan

app = FastAPI(
    title="Finance Bot API",
    description="API for the Finance Bot Telegram application",
    version="1.1.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(telegram.router, prefix="/api", tags=["telegram"])
# app.include_router(finance.router)