from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.utils.env_vars import APP_ENV


def create_app() -> FastAPI:
    from service.util.logger_util import get_logger
    logger = get_logger("fastapi")

    app = FastAPI(
        title="Sports Scraper API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS for local dev
    if APP_ENV in ["local", "docker"]:
        # noinspection PyTypeChecker
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Custom Swagger UI
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui():
        # noinspection PyUnresolvedReferences
        return get_swagger_ui_html(openapi_url=app.openapi_url, title="Custom Swagger UI")

    # STATIC FILES (must be BEFORE fallback)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # ROOT SERVES index.html DIRECTLY
    @app.get("/", include_in_schema=False)
    async def root():
        return FileResponse("templates/index.html")

    # API ROUTES
    from app.routes.cluster import router as cluster_router
    app.include_router(cluster_router)

    # SPA FALLBACK (AFTER static + API)
    @app.get("/{path_name:path}", include_in_schema=False)
    async def spa_fallback(path_name: str):
        logger.info("SPA fallback for: %s", path_name)
        return FileResponse("templates/index.html")

    return app
