# app/routes/cluster.py
import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.routes.cluster_filter_request import ClusterFilterRequest
from service.cluster_buffer_service import ClusterBufferService
from service.cluster_service import ClusterService
from service.scraper_service import ScraperService
from service.util.path_util import PROJECT_ROOT

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


@router.get("/sites")
async def list_sites():
    config_path = PROJECT_ROOT / "app" / "config" / "sites_config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            sites_config = json.load(f)
            # Extract only display_name values
            sites = [site.get("display_name") for site in sites_config if "display_name" in site]
    except Exception as e:
        sites = []
        print(f"Failed to load sites_config.json: {e}")
    return JSONResponse(content=sites)


@router.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})
