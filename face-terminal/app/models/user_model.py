from sqlmodel import SQLModel, Field
from typing import Optional
import datetime

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, description="Nama pengguna admin")
    full_name: Optional[str] = Field(default=None, description="Nama lengkap pengguna")
    role: str = Field(default="admin", description="Peran pengguna (admin / viewer)")

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(description="Password yang sudah di-hash")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        description="Tanggal pembuatan akun"
    )

class UserCreate(SQLModel):
    """Schema input untuk membuat user baru"""
    username: str
    password: str
    full_name: Optional[str] = None

class UserRead(UserBase):
    """Schema output untuk menampilkan data user"""
    id: int
    created_at: datetime.datetime
