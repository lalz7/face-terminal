from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio


from app.core.db import init_db
from app.services.hikvision_service import sync_all_devices
from app.services.event_service import cleanup_old_events
from app.routers import device_router, event_router, auth_router, page_router


app = FastAPI(title="Face Terminal API")

# Folder frontend
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ======================================================
# 🔹 APSCHEDULER SETUP
# ======================================================

scheduler = AsyncIOScheduler()
job_running = False  # Mencegah overlap sync


# ======================================================
# 🔁 JOB: Sinkronisasi perangkat setiap 1 detik
# ======================================================
async def scheduled_sync_job():
    global job_running
    if job_running:
        # Lewati jika sinkronisasi masih berjalan
        return

    job_running = True
    try:
        await sync_all_devices(verbose=False)
    except Exception as e:
        print(f"❌ {datetime.now()} — Error sinkronisasi: {e}")
    finally:
        job_running = False


# ======================================================
# 🧹 JOB: Cleanup event lama setiap hari jam 00:00
# ======================================================
async def scheduled_cleanup_job():
    try:
        deleted = await cleanup_old_events(days=60)
        print(f"🧹 {datetime.now()} — Cleanup event sukses, {deleted} event dihapus (>60 hari).")
    except Exception as e:
        print(f"⚠️ {datetime.now()} — Gagal cleanup event: {e}")


@app.on_event("startup")
async def startup_event():
    print("🔧 Inisialisasi database...")
    await init_db()

    print("🕒 Menjalankan scheduler background...")

    # Job 1: Sinkronisasi perangkat setiap 1 detik
    scheduler.add_job(scheduled_sync_job, "interval", seconds=1, id="sync_devices")

    # Job 2: Cleanup event lama setiap hari jam 00:00
    scheduler.add_job(
        scheduled_cleanup_job,
        "cron",
        hour=0,
        minute=0,
        id="cleanup_events",
    )

    scheduler.start()
    print("🚀 Scheduler aktif — sinkronisasi tiap 1 detik, cleanup tiap 00:00\n")

    # Jalankan satu kali sinkronisasi langsung saat startup
    await scheduled_sync_job()


# ======================================================
# 🔹 ROUTERS
# ======================================================
app.include_router(device_router.router)
app.include_router(event_router.router)
app.include_router(auth_router.router)
app.include_router(page_router.router)


# ======================================================
# 🔹 ROOT
# ======================================================
@app.get("/")
async def home():
    return {"status": "running", "message": "Face Terminal API aktif"}
