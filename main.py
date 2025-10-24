# main.py

from app import create_app
from cron_jobs.scraper_job import start_scraper_loop

app = create_app()

if __name__ == "__main__":
    # Optional: start scraper loop alongside FastAPI
    start_scraper_loop(interval_sec=1, is_looped=True)

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
