# app/__init__.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html

from app.utils.env_vars import APP_ENV


def create_app() -> FastAPI:
    from service.util.logger_util import get_logger
    logger = get_logger("fastapi")

    app = FastAPI(
        title="Sports Scraper API",
        docs_url="/docs",  # enables Swagger UI at /docs
        redoc_url="/redoc",  # enables ReDoc at /redoc
        openapi_url="/openapi.json",
        # static_folder="/static",
        # template_folder='templates'
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

    from fastapi.templating import Jinja2Templates
    from fastapi import Request

    templates = Jinja2Templates(directory="templates")

    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/", include_in_schema=False)
    async def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    from app.routes.cluster import router as cluster_router
    app.include_router(cluster_router)
    return app
