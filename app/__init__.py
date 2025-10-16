# app/__init__.py

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html


def create_app() -> FastAPI:
    app = FastAPI(
        title="Sports Scraper API",
        docs_url="/docs",  # enables Swagger UI at /docs
        redoc_url="/redoc",  # enables ReDoc at /redoc
        openapi_url="/openapi.json"
    )

    # Swagger UI customization (optional)
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui():
        return get_swagger_ui_html(openapi_url=app.openapi_url, title="Custom Swagger UI")

    from app.routes.cluster import router as cluster_router
    app.include_router(cluster_router)
    return app
