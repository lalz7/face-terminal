from sqlmodel import select, desc
from app.models.event_model import Event, EventCreate
from app.core.db import AsyncSessionLocal
from datetime import datetime, timedelta

# 🔹 Ambil semua event terbaru (misalnya untuk dashboard)
async def get_recent_events(limit: int = 20):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Event).order_by(desc(Event.event_time)).limit(limit)
        )
        return result.all()

# 🔹 Tambah event baru (biasanya dipanggil saat ada notifikasi dari perangkat)
async def create_event(data: EventCreate):
    async with AsyncSessionLocal() as session:
        event = Event.from_orm(data)
        event.event_time = datetime.utcnow()
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event

# 🔹 Update status sinkronisasi (misal setelah sukses dikirim ke API eksternal)
async def mark_event_synced(event_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Event).where(Event.id == event_id))
        event = result.first()
        if event:
            event.synced = True
            await session.commit()
            await session.refresh(event)
            return event
        return None

# 🔹 Hapus event lama (misal > 30 hari)
async def cleanup_old_events(days: int = 30):
    async with AsyncSessionLocal() as session:
        threshold = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(select(Event).where(Event.event_time < threshold))
        old_events = result.all()
        for ev in old_events:
            await session.delete(ev)
        await session.commit()
        return len(old_events)
