# app/routes/cluster.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from service.cluster_service import ClusterService
from service.scraper_service import ScraperService

router = APIRouter()


@router.get("/cluster")
async def cluster_news():
    result = ClusterService.cluster_news()
    return JSONResponse(content=result)


@router.delete("/delete-old-csvs")
async def delete_old_csvs():
    deleted = ClusterService.delete_old_csvs()
    return JSONResponse(content={"deleted_files": deleted})


@router.post("/scrape-sites")
async def scrape_sites_async():
    ScraperService.scrape_sites_async()
    return JSONResponse(content={"status": "Scraping started in background"})
