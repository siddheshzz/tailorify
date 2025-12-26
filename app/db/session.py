from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",  # Auto-toggle logging
    pool_pre_ping=True,  # Health check for connections
    pool_size=10,  # Number of permanent connections
    max_overflow=20,
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_session():
    """
    Asynchronous Dependency Injection for FastAPI.
    Used in routes as: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Note: We usually commit inside the service layer,
            # but we use 'async with' here to ensure the session is
            # closed even if an error occurs.
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
