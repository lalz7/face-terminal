from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models.event_model import EventRead, EventCreate
from app.services.event_service import (
    get_recent_events,
    create_event,
    mark_event_synced,
)

router = APIRouter(prefix="/events", tags=["Events"])


# ======================================================
# 1️⃣ Ambil daftar event terbaru
# ======================================================
@router.get("/", response_model=List[EventRead])
async def list_events(limit: int = Query(20, ge=1, le=100)):
    """
    Ambil daftar event terbaru dari database.
    Default: 20 event terakhir.
    """
    events = await get_recent_events(limit=limit)
    if not events:
        raise HTTPException(status_code=404, detail="Belum ada event tercatat.")
    return events


# ======================================================
# 2️⃣ Tambah event secara manual (opsional, testing)
# ======================================================
@router.post("/", response_model=EventRead)
async def add_event(event_data: EventCreate):
    """
    Tambah event secara manual (biasanya otomatis dari Hikvision).
    """
    return await create_event(event_data)


# ======================================================
# 3️⃣ Tandai event sudah tersinkronisasi
# ======================================================
@router.put("/{event_id}/synced", response_model=EventRead)
async def mark_synced(event_id: int):
    """
    Tandai event tertentu sudah dikirim/sinkron ke API eksternal.
    """
    updated = await mark_event_synced(event_id)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Event ID {event_id} tidak ditemukan.")
    return updated
