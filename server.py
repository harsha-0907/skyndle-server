
import logging
from fastapi import FastAPI
from utils.lifespan import initialize_server, shutdown_server
from contextlib import asynccontextmanager
from routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Lifespan events for the Skyndle Server """

    logger.info("Starting Skyndle server initialization")
    try:
        print("Initializing the Server")
        var = initialize_server()
        app.state.var = var
        logger.info("Skyndle server initialized successfully")

        yield

        logger.info("Skyndle server shutdown started")
        shutdown_server(app.state.var)  # use await if async
        logger.info("Skyndle server shutdown completed")

    except Exception:
        logger.exception("Critical failure during application lifespan")
        raise

logger = logging.getLogger(__name__)
app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Hello World"}

