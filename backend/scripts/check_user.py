import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine
from app.models.user import User

async def check():
    async with AsyncSession(engine) as s:
        existing = (await s.execute(select(User).where(User.email == "demo123@gmail.com"))).scalar_one_or_none()
        if existing:
            print("USER EXISTS")
        else:
            print("USER DOES NOT EXIST")

if __name__ == "__main__":
    asyncio.run(check())
