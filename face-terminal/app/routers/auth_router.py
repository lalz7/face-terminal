from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import select

from app.models.user_model import User, UserCreate
from app.core.db import AsyncSessionLocal
from app.core.config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])

# ======================================================
# 🔐 KONFIGURASI JWT
# ======================================================
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # token berlaku 1 jam

# ======================================================
# 🔑 ENKRIPSI PASSWORD
# ======================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ======================================================
# 🧩 UTIL: Hash dan verifikasi password
# ======================================================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


# ======================================================
# 🧩 UTIL: Buat token JWT
# ======================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ======================================================
# 🔹 REGISTER USER BARU
# ======================================================
@router.post("/register")
async def register_user(user_data: UserCreate):
    async with AsyncSessionLocal() as session:
        # Cek apakah username sudah ada
        result = await session.execute(select(User).where(User.username == user_data.username))
        existing_user = result.first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username sudah digunakan.")

        # Hash password sebelum disimpan
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            full_name=user_data.full_name,
            password_hash=hashed_password,
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return {"status": "success", "message": f"User '{new_user.username}' berhasil dibuat."}


# ======================================================
# 🔹 LOGIN (MENGHASILKAN TOKEN)
# ======================================================
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == form_data.username))
        user = result.first()

        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Username atau password salah.")

        # Buat JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }


# ======================================================
# 🔹 VALIDASI TOKEN
# ======================================================
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token tidak valid.")
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.username == username))
            user = result.first()
            if not user:
                raise HTTPException(status_code=401, detail="User tidak ditemukan.")
            return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token tidak valid.")


# ======================================================
# 🔹 ROUTE PROTEKSI (contoh)
# ======================================================
@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Lihat profil user yang sedang login"""
    return {
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "created_at": current_user.created_at
    }
