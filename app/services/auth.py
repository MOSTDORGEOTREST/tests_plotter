from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status
from sqlalchemy.future import select
from passlib.hash import bcrypt

from db.database import async_session
from db import tables

security = HTTPBasic()

async def get_current_username(
    credentials: HTTPBasicCredentials = Depends(security),
):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(tables.Users).filter_by(username=credentials.username))
            user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not bcrypt.verify(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user.username