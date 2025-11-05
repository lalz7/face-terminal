from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 🔹 1. Buat engine async
#    create_async_engine memungkinkan query ke database berjalan non-blocking
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,              # True kalau ingin lihat log SQL
    future=True,             # Gunakan API terbaru SQLAlchemy
)

# 🔹 2. Buat session async
#    AsyncSession menggantikan Session biasa (sync)
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 🔹 3. Fungsi untuk inisialisasi tabel (dipanggil saat startup)
async def init_db():
    """Inisialisasi tabel-tabel dari model SQLModel"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
