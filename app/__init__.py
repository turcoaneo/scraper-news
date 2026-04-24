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
    if APP_ENV in ["local", "docker"]:
        logger.info(f"Starting FastAPI in {APP_ENV} mode")

        # noinspection PyTypeChecker
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],  # Vue dev server
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        logger.info("Starting in AWS mode")

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

    from fastapi.responses import FileResponse

    @app.get("/")
    def root():
        return FileResponse("templates/index.html")

    # @app.get("/", include_in_schema=False)
    # async def index(request: Request):
    #     return templates.TemplateResponse("index.html", {"request": request})
    #
    # @app.get("/debug-request")
    # async def debug_request(request: Request):
    #     return {
    #         "state": str(request.state.__dict__),
    #         "path_params": request.path_params,
    #         "query_params": dict(request.query_params),
    #     }
    #
    # from fastapi import Response
    #
    # @app.get("/__debug_index")
    # async def debug_index():
    #     with open("templates/index.html", "r") as f:
    #         return Response(f.read(), media_type="text/plain")

    from app.routes.cluster import router as cluster_router
    app.include_router(cluster_router)

    from fastapi.responses import FileResponse

    @app.get("/{path_name:path}")
    async def spa_fallback(path_name: str):
        logger.info("Refresh maybe, fallback for: %s", path_name)
        return FileResponse("templates/index.html")

    return app
