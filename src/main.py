import uvicorn
from fastapi import FastAPI

from src.api.v1 import auth, chat, message, group


def setup_routers(app: FastAPI) -> None:
    app.include_router(auth.router)
    app.include_router(chat.router)
    app.include_router(group.router)
    app.include_router(message.router)


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
