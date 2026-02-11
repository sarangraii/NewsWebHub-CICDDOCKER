# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from contextlib import asynccontextmanager
# from app.config import settings
# from app.database import connect_to_mongo, close_mongo_connection
# from app.routes import news, notifications
# from app.utils.scheduler import start_scheduler, stop_scheduler
# from app.services.news_fetcher import news_fetcher
# from pathlib import Path
# import os

# # ✅ CRITICAL: Initialize Firebase FIRST, before anything else
# try:
#     import firebase_admin
#     from firebase_admin import credentials
    
#     cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    
#     if os.path.exists(cred_path):
#         cred = credentials.Certificate(cred_path)
#         firebase_admin.initialize_app(cred)
#         print("✅ Firebase initialized for notifications")
#     else:
#         print("⚠️ Firebase credentials not found - notifications disabled")
# except Exception as e:
#     print(f"⚠️ Firebase initialization failed: {e}")

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     await connect_to_mongo()
#     start_scheduler()
    
#     # Create static directory
#     Path("static/audio").mkdir(parents=True, exist_ok=True)
    
#     print("Fetching initial news...")
#     await news_fetcher.fetch_and_store_all_categories()
    
#     yield
    
#     # Shutdown
#     stop_scheduler()
#     await close_mongo_connection()

# app = FastAPI(
#     title="News Aggregation Platform API",
#     description="API for news aggregation with AI summaries",
#     version="2.0.0",
#     lifespan=lifespan
# )

# # ✅ FIXED: CORS middleware with correct port
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",  # ✅ Correct Vite frontend port
#         "http://localhost:5174",  # Backup port
#         "http://127.0.0.1:5173",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Mount static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # Include routers
# app.include_router(news.router)
# app.include_router(notifications.router)

# @app.get("/")
# async def root():
#     return {
#         "message": "News Aggregation Platform API",
#         "version": "2.0.0",
#         "features": ["Hindi Support", "AI Summaries", "Voice Reading", "Push Notifications"],
#         "docs": "/docs"
#     }

# @app.get("/health")
# async def health():
#     return {"status": "healthy"}


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import os
import json

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import news, notifications
from app.utils.scheduler import start_scheduler, stop_scheduler
from app.services.news_fetcher import news_fetcher  # ✅ CRITICAL: Import this

# ======================================================
# 🔥 Firebase Initialization (Render + Local safe)
# ======================================================
try:
    import firebase_admin
    from firebase_admin import credentials

    firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

    if firebase_json:
        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized from environment variable")
    else:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized from file")
        else:
            print("⚠️ Firebase credentials not found — notifications disabled")

except Exception as e:
    print(f"⚠️ Firebase initialization skipped: {e}")

# ======================================================
# 🔁 Application Lifespan - WITH INITIAL FETCH
# ======================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting News Aggregation Platform...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    print("✅ MongoDB connected")
    
    # Ensure static directories exist
    Path("static/audio").mkdir(parents=True, exist_ok=True)
    print("✅ Static directories created")
    
    # ✅ CRITICAL: Fetch initial news on startup (ONLY on first deploy or restart)
    try:
        print("📰 Fetching initial news articles...")
        total = await news_fetcher.fetch_and_store_all_categories()
        print(f"✅ Initial fetch complete: {total} articles saved")
    except Exception as e:
        print(f"❌ Initial news fetch failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Start scheduler for periodic updates
    start_scheduler()

    yield

    # Shutdown
    print("🛑 Shutting down application...")
    stop_scheduler()
    await close_mongo_connection()

# ======================================================
# 🚀 FastAPI App
# ======================================================
app = FastAPI(
    title="News Aggregation Platform API",
    description="API for news aggregation with AI summaries",
    version="2.0.0",
    lifespan=lifespan,
)

# ======================================================
# 🌐 CORS (Vercel + Local) - Fixed for all deployments
# ======================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
    ],
    # ✅ Allow all Vercel preview and production deployments
    allow_origin_regex=r"https://news-web-hub-cicddocker.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# ======================================================
# 📁 Static Files
# ======================================================
app.mount("/static", StaticFiles(directory="static"), name="static")

# ======================================================
# 🧩 Routes
# ======================================================
app.include_router(news.router)
app.include_router(notifications.router)

# ======================================================
# 🏠 Root & Health
# ======================================================
@app.get("/")
async def root():
    return {
        "message": "News Aggregation Platform API",
        "version": "2.0.0",
        "features": [
            "Hindi Support",
            "AI Summaries",
            "Voice Reading",
            "Push Notifications",
        ],
        "docs": "/docs",
    }

@app.get("/health")
async def health():
    from app.database import get_database
    db = get_database()
    
    # Check MongoDB connection
    try:
        await db.command('ping')
        mongo_status = "connected"
    except Exception as e:
        mongo_status = f"error: {str(e)}"
    
    # Check news count
    try:
        collection = db["news"]
        news_count = await collection.count_documents({})
    except:
        news_count = 0
    
    return {
        "status": "healthy",
        "mongodb": mongo_status,
        "total_articles": news_count,
        "scheduler": "running" if scheduler.running else "stopped"
    }

# ======================================================
# 🔧 Admin Endpoints (for debugging)
# ======================================================
@app.post("/api/admin/fetch-news")
async def manual_fetch_news():
    """Manual trigger for fetching news - for testing"""
    try:
        print("📰 Manual fetch triggered...")
        total = await news_fetcher.fetch_and_store_all_categories()
        return {
            "success": True, 
            "message": f"Successfully fetched and saved {total} articles",
            "articles_saved": total
        }
    except Exception as e:
        import traceback
        return {
            "success": False, 
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/api/admin/stats")
async def get_stats():
    """Get database statistics"""
    try:
        from app.database import get_database
        db = get_database()
        collection = db["news"]
        
        total = await collection.count_documents({})
        en_count = await collection.count_documents({"language": "en"})
        hi_count = await collection.count_documents({"language": "hi"})
        
        # Get articles by category
        categories = {}
        for cat in ["general", "technology", "business", "sports", "entertainment"]:
            count = await collection.count_documents({"category": cat})
            categories[cat] = count
        
        return {
            "total_articles": total,
            "by_language": {
                "english": en_count,
                "hindi": hi_count
            },
            "by_category": categories
        }
    except Exception as e:
        return {"error": str(e)}