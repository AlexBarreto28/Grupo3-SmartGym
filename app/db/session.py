from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.database_url, 
                            echo=True,
                            pool_size=20,
                            max_overflow=30,
                            pool_timeout=30,
                            pool_pre_ping=True,
                            )

SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as db:
        yield db