# app/routes/cluster.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.routes.cluster_filter_request import ClusterFilterRequest
from service.cluster_buffer_service import ClusterBufferService
from service.cluster_service import ClusterService
from service.scraper_service import ScraperService

router = APIRouter()


@router.post("/cluster-cached-filtered")
async def cluster_cached_filtered_news(request_filter: ClusterFilterRequest):
    result = ClusterBufferService.get_cached_filtered_clusters(request_filter)
    return JSONResponse(content=result)


@router.get("/cluster")
async def cluster_news():
    result = ClusterService.cluster_news()
    return JSONResponse(content=result)


@router.get("/cluster-cached")
async def cluster_cached_news():
    result = ClusterBufferService.get_cached_clusters()
    return JSONResponse(content=result)


@router.delete("/delete-old-csvs")
async def delete_old_csvs():
    deleted = ClusterService.delete_old_csvs()
    return JSONResponse(content={"deleted_files": deleted})


@router.post("/scrape-sites")
async def scrape_sites_async():
    ScraperService.scrape_sites_async()
    return JSONResponse(content={"status": "Scraping started in background"})


@router.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})
