# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from app.services.news_fetcher import news_fetcher

# scheduler = AsyncIOScheduler()

# async def scheduled_news_fetch():
#     """Scheduled task to fetch news"""
#     print("Running scheduled news fetch...")
#     await news_fetcher.fetch_and_store_all_categories()
#     await news_fetcher.cleanup_old_articles()

# def start_scheduler():
#     """Start the background scheduler"""
#     # Fetch news every 6 hours
#     scheduler.add_job(scheduled_news_fetch, 'interval', hours=6, id='fetch_news')
    
#     # Cleanup old articles daily
#     scheduler.add_job(news_fetcher.cleanup_old_articles, 'interval', days=1, id='cleanup_articles')
    
#     scheduler.start()
#     print("Scheduler started")

# def stop_scheduler():
#     """Stop the scheduler"""
#     scheduler.shutdown()
#     print("Scheduler stopped")


from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.news_fetcher import news_fetcher

scheduler = AsyncIOScheduler()

async def scheduled_news_fetch():
    """Scheduled task to fetch news"""
    print("⏰ Running scheduled news fetch...")
    try:
        total = await news_fetcher.fetch_and_store_all_categories()
        print(f"✅ Scheduled fetch complete: {total} articles saved")
    except Exception as e:
        print(f"❌ Scheduled fetch failed: {e}")

async def scheduled_cleanup():
    """Scheduled task to cleanup old articles"""
    print("🗑️ Running scheduled cleanup...")
    try:
        deleted = await news_fetcher.cleanup_old_articles()
        print(f"✅ Cleanup complete: {deleted} old articles removed")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def start_scheduler():
    """Start the background scheduler"""
    # Fetch news every 6 hours
    scheduler.add_job(
        scheduled_news_fetch, 
        'interval', 
        hours=6, 
        id='fetch_news',
        replace_existing=True
    )
    
    # Cleanup old articles daily at 2 AM
    scheduler.add_job(
        scheduled_cleanup, 
        'cron',
        hour=2,
        minute=0,
        id='cleanup_articles',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Scheduler started - News updates every 6 hours, cleanup daily at 2 AM")

def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler stopped")
