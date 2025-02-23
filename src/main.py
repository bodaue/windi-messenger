from pathlib import Path

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.api.v1 import auth, chat, message, group, ws


def setup_routers(app: FastAPI) -> None:
    app.include_router(auth.router)
    app.include_router(chat.router)
    app.include_router(group.router)
    app.include_router(message.router)
    app.include_router(ws.router)

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def create_application() -> FastAPI:
    app = FastAPI(
        title="Windi Messenger",
        debug=True,
        root_path="/api/v1",
    )

    setup_routers(app)
    return app


if __name__ == "__main__":
    uvicorn.run("src.main:create_application", factory=True, reload=True)
