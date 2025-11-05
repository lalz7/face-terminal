from sqlmodel import SQLModel, Field
from typing import Optional
import datetime

class DeviceBase(SQLModel):
    ip: str = Field(index=True, description="Alamat IP perangkat")
    name: str = Field(default="Unknown", description="Nama perangkat")
    username: str = Field(default="admin", description="Username perangkat")
    password: str = Field(default="", description="Password perangkat")
    location: Optional[str] = None
    status: str = Field(default="offline")
    is_active: bool = Field(default=True)

class Device(DeviceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    last_sync: Optional[datetime.datetime] = Field(
        default=None, description="Waktu terakhir sinkronisasi"
    )

class DeviceCreate(DeviceBase):
    """Schema input untuk menambah perangkat"""
    pass

class DeviceRead(DeviceBase):
    """Schema output untuk menampilkan perangkat"""
    id: int
    last_sync: Optional[datetime.datetime]
