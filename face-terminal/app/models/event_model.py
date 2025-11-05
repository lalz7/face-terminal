from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import datetime

class EventBase(SQLModel):
    event_type: str = Field(description="Jenis event yang diterima dari perangkat")
    event_time: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        description="Waktu event terjadi"
    )
    picture_url: Optional[str] = Field(
        default=None,
        description="URL gambar event (jika tersedia)"
    )
    synced: bool = Field(default=False, description="Status sinkronisasi ke API eksternal")

class Event(EventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: Optional[int] = Field(
        default=None, foreign_key="device.id", description="ID perangkat sumber event"
    )

class EventCreate(EventBase):
    """Schema input untuk menambah event"""
    device_id: int

class EventRead(EventBase):
    """Schema output untuk menampilkan event"""
    id: int
    device_id: int
