import httpx
import asyncio
from datetime import datetime
from sqlmodel import select
from app.core.db import AsyncSessionLocal
from app.models.device_model import Device
from app.models.event_model import EventCreate
from app.services.event_service import create_event
from app.services.device_service import update_device_status

# ======================================================
#  CLIENT GLOBAL
# ======================================================
client = httpx.AsyncClient(timeout=10.0)

# ======================================================
# 1️⃣ Cek status perangkat
# ======================================================
async def get_device_status(ip: str, username: str, password: str) -> str:
    url = f"http://{ip}/ISAPI/System/status"
    try:
        response = await client.get(url, auth=httpx.DigestAuth(username, password))
        if response.status_code == 200:
            return "online"
        return "offline"
    except Exception:
        return "offline"


# ======================================================
# 2️⃣ Ambil event dari perangkat
# ======================================================
async def fetch_device_events(ip: str, username: str, password: str, device_id: int) -> int:
    url = f"http://{ip}/ISAPI/Event/notification"
    try:
        response = await client.get(url, auth=httpx.DigestAuth(username, password))
        if response.status_code != 200:
            return 0

        data = response.json()
        events = data.get("EventList", [])
        saved_count = 0

        for e in events:
            event_data = EventCreate(
                device_id=device_id,
                event_type=e.get("Type", "Unknown"),
                event_time=datetime.utcnow(),
                picture_url=e.get("ImageURL"),
                synced=False,
            )
            await create_event(event_data)
            saved_count += 1

        return saved_count
    except Exception:
        return 0


# ======================================================
# 3️⃣ Update status perangkat
# ======================================================
async def sync_device_status(ip: str, username: str, password: str):
    status = await get_device_status(ip, username, password)
    await update_device_status(ip, status)
    return status


# ======================================================
# 4️⃣ Sinkronisasi semua perangkat aktif
# ======================================================
async def sync_all_devices(verbose: bool = True) -> dict:
    """
    Sinkronisasi semua perangkat aktif:
      - Cek status
      - Ambil event (jika online)
      - Update DB
    Return: summary dict
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Device).where(Device.is_active == True))
        devices = result.all()

    if not devices:
        if verbose:
            print(f"⚠️ {datetime.now()} — Tidak ada perangkat aktif di database.")
        return {"total": 0, "online": 0, "offline": 0}

    online_count = 0
    offline_count = 0
    tasks = []

    if verbose:
        print(f"\n🔁 {datetime.now()} — Mulai sinkronisasi {len(devices)} perangkat...")

    for device in devices:
        tasks.append(sync_single_device(device, verbose))

    results = await asyncio.gather(*tasks)

    for r in results:
        if r["status"] == "online":
            online_count += 1
        else:
            offline_count += 1

    summary = {
        "total": len(devices),
        "online": online_count,
        "offline": offline_count,
    }

    if verbose:
        print(f"✅ {datetime.now()} — Sinkronisasi selesai: {summary}\n")

    return summary


# ======================================================
# 5️⃣ Sinkronisasi satu perangkat
# ======================================================
async def sync_single_device(device: Device, verbose: bool = True) -> dict:
    try:
        status = await get_device_status(device.ip, device.username, device.password)
        await update_device_status(device.ip, status)

        if status == "online":
            event_count = await fetch_device_events(
                device.ip, device.username, device.password, device.id
            )
            if verbose:
                print(f"🟢 {device.ip} [{device.name}] ONLINE - {event_count} event tersimpan")
        else:
            if verbose:
                print(f"🔴 {device.ip} [{device.name}] OFFLINE")

        return {"ip": device.ip, "status": status}

    except Exception as e:
        if verbose:
            print(f"❌ Error {device.ip}: {e}")
        return {"ip": device.ip, "status": "error"}
