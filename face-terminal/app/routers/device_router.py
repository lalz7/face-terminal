from fastapi import APIRouter, HTTPException
from typing import List
from app.models.device_model import Device, DeviceCreate, DeviceRead
from app.services.device_service import (
    get_all_devices,
    create_device,
    delete_device,
    toggle_device_active,
    update_device_status,
)

router = APIRouter(prefix="/devices", tags=["Devices"])


# ======================================================
# 1️⃣ Ambil semua perangkat
# ======================================================
@router.get("/", response_model=List[DeviceRead])
async def list_devices():
    """
    Ambil semua perangkat dari database.
    """
    devices = await get_all_devices()
    if not devices:
        raise HTTPException(status_code=404, detail="Tidak ada perangkat ditemukan.")
    return devices


# ======================================================
# 2️⃣ Tambah perangkat baru
# ======================================================
@router.post("/", response_model=DeviceRead)
async def add_device(device_data: DeviceCreate):
    """
    Tambah perangkat baru.
    """
    device = await create_device(device_data)
    return device


# ======================================================
# 3️⃣ Hapus perangkat berdasarkan IP
# ======================================================
@router.delete("/{ip}")
async def remove_device(ip: str):
    """
    Hapus perangkat berdasarkan IP.
    """
    success = await delete_device(ip)
    if not success:
        raise HTTPException(status_code=404, detail=f"Perangkat {ip} tidak ditemukan.")
    return {"status": "success", "message": f"Perangkat {ip} telah dihapus."}


# ======================================================
# 4️⃣ Toggle aktif/nonaktif
# ======================================================
@router.put("/{ip}/toggle", response_model=DeviceRead)
async def toggle_active(ip: str):
    """
    Aktif/nonaktifkan perangkat (switch boolean is_active)
    """
    device = await toggle_device_active(ip)
    if not device:
        raise HTTPException(status_code=404, detail=f"Perangkat {ip} tidak ditemukan.")
    return device


# ======================================================
# 5️⃣ Update status manual (online/offline)
# ======================================================
@router.put("/{ip}/status/{status}", response_model=DeviceRead)
async def update_status(ip: str, status: str):
    """
    Update status perangkat manual.
    Status hanya bisa 'online' atau 'offline'.
    """
    if status not in ["online", "offline"]:
        raise HTTPException(status_code=400, detail="Status tidak valid.")
    device = await update_device_status(ip, status)
    if not device:
        raise HTTPException(status_code=404, detail=f"Perangkat {ip} tidak ditemukan.")
    return device
