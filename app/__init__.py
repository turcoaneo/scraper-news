# app/__init__.py


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html

from app.utils.env_vars import APP_ENV
from service.util.logger_util import get_logger

logger = get_logger("fastapi")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Sports Scraper API",
        docs_url="/docs",  # enables Swagger UI at /docs
        redoc_url="/redoc",  # enables ReDoc at /redoc
        openapi_url="/openapi.json"
    )

    # Enable CORS for local development
    if APP_ENV == "local":
        logger.info("Starting FastAPI in local mode")

        # noinspection PyTypeChecker
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],  # Vue dev server
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Swagger UI customization (optional)
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui():
        # noinspection PyUnresolvedReferences
        return get_swagger_ui_html(openapi_url=app.openapi_url, title="Custom Swagger UI")

    from app.routes.cluster import router as cluster_router
    app.include_router(cluster_router)
    return app
