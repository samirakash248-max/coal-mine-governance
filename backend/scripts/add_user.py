import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Ensure the app module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine
from app.models.hierarchy import Mine
from app.models.user import User, Role
from app.core.security import hash_password

async def add_demo_user():
    async with AsyncSession(engine) as s:
        email = "demo123@gmail.com"
        
        # Check if user already exists
        existing_user = (await s.execute(select(User).where(User.email == email))).scalar_one_or_none()
        if existing_user:
            print(f"User {email} already exists.")
            return

        # Get an existing Mine to attach the user to
        mine = (await s.execute(select(Mine).limit(1))).scalar_one_or_none()
        if not mine:
            print("No mines found in the database. Cannot assign user to a mine.")
            return

        # Create user
        new_user = User(
            email=email,
            hashed_password=hash_password("demo123"),
            full_name="Demo User",
            role=Role.MINE_MANAGER,
            is_active=True,
            organization_id=None,
            subsidiary_id=None,
            region_id=mine.region_id,
            mine_id=mine.id,
            department_id=None
        )
        
        s.add(new_user)
        await s.commit()
        print(f"Successfully added user {email} (Password: demo123) assigned to Mine: {mine.name}")

if __name__ == "__main__":
    asyncio.run(add_demo_user())
