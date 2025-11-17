# main.py

from app import create_app
from app.utils.env_vars import APP_ENV
from cron_jobs.scraper_job import start_scraper_loop
from service.monitor_resources import monitor_resources

app = create_app()

if __name__ == "__main__":
    # Optional: start scraper loop alongside FastAPI
    start_scraper_loop(interval_sec=150, is_looped=True)

    # Monitor resources
    monitor_resources()

    import uvicorn

    exposed_port = 80 if APP_ENV in ["uat", "prod"] else 8000

    uvicorn.run(app, host="0.0.0.0", port=exposed_port)
