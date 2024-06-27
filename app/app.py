from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.future import select
from passlib.hash import bcrypt

from db.database import Base, engine, async_session
from db import tables
from config import configs


app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )

@app.on_event("startup")
async def startup_event():

    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async def create_users():
        async with async_session() as session:
            async with session.begin():

                for i in range(10):
                    user_name = await session.execute(
                        select(tables.Users).
                        filter_by(username=f'{configs.base_user_name}_{str(i + 1)}')
                    )
                    user_name = user_name.scalars().first()

                    if not user_name:
                        try:
                            user = tables.Users(
                                username=f'{configs.base_user_name}_{str(i + 1)}',
                                password_hash=bcrypt.hash(f'{configs.base_user_password}_{str(i + 1)}')
                            )

                            session.add(user)

                            print(f'Создан пользователь {str(i + 1)}')
                        except Exception as err:
                            print(f'Ошибка создания пользователя {str(i + 1)}', str(err))
                await session.commit()

    await create_users()