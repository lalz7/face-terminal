from sqlmodel import select
from app.models.device_model import Device, DeviceCreate
from app.core.db import AsyncSessionLocal
from datetime import datetime

# 🔹 Ambil semua perangkat
async def get_all_devices():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Device))
        return result.all()

# 🔹 Tambah perangkat baru
async def create_device(data: DeviceCreate):
    async with AsyncSessionLocal() as session:
        device = Device.from_orm(data)
        session.add(device)
        await session.commit()
        await session.refresh(device)
        return device

# 🔹 Toggle (aktif/nonaktif) perangkat berdasarkan IP
async def toggle_device_active(ip: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Device).where(Device.ip == ip))
        device = result.first()
        if not device:
            return None
        device.is_active = not device.is_active
        await session.commit()
        await session.refresh(device)
        return device

# 🔹 Update status perangkat
async def update_device_status(ip: str, status: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Device).where(Device.ip == ip))
        device = result.first()
        if device:
            device.status = status
            device.last_sync = datetime.utcnow()
            await session.commit()
            await session.refresh(device)
            return device
        return None

# 🔹 Hapus perangkat berdasarkan IP
async def delete_device(ip: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Device).where(Device.ip == ip))
        device = result.first()
        if device:
            await session.delete(device)
            await session.commit()
            return True
        return False
