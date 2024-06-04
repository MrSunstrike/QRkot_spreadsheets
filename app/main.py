from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings
from app.core.google_client import cred
from app.core.init_db import create_first_superuser

app = FastAPI(
    title=settings.app_title,
    description=settings.description,
)
app.include_router(main_router)


@app.on_event('startup')
async def startup():

    print('*' * 30)
    print(settings.private_key)
    print('*' * 30)

    print('1' * 30)
    print(cred)
    print('1' * 30)

    await create_first_superuser()
