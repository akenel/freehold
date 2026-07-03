"""Freehold — profile service (all DB access for user profiles)."""
from sqlalchemy import select

from db import async_session
from models import Profile


async def get(username: str) -> Profile | None:
    async with async_session() as s:
        return (await s.execute(
            select(Profile).where(Profile.username == username)
        )).scalar_one_or_none()


async def upsert(username: str, **fields) -> Profile:
    """Create the profile if missing, then apply only the fields that were given
    (None means 'leave unchanged' — so not uploading a new avatar keeps the old)."""
    async with async_session() as s:
        profile = (await s.execute(
            select(Profile).where(Profile.username == username)
        )).scalar_one_or_none()
        if profile is None:
            profile = Profile(username=username)
            s.add(profile)
        for key, value in fields.items():
            if value is not None:
                setattr(profile, key, value)
        await s.commit()
        await s.refresh(profile)
        return profile
