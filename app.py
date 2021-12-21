from pathlib import Path

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from controllers.boards.board_controller import boards_router
from controllers.pipelines.pipelines_controller import pipelines_router
from controllers.registration.login_controller import auth_router
from controllers.tags.tag_controller import tags_router
from controllers.tasks.task_controller import api_router

application = FastAPI(
    title="Task manager",
    description="Author - https://github.com/olegggatttor",
    version="1.0.0",
)

application.include_router(api_router)
application.include_router(auth_router)
application.include_router(boards_router)
application.include_router(pipelines_router)
application.include_router(tags_router)
application.mount('/static', StaticFiles(directory=Path(__file__).parent.resolve() / 'resources/static'), name="static")


if __name__ == '__main__':
    uvicorn.run(app='app:application', port=2390)
