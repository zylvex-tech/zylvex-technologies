from datetime import datetime, timedelta
from typing import Optional
import uuid
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import secrets
import hashlib

from app.core.config import settings
from app.models.user import RefreshToken


pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token() -> str:
    """Create a cryptographically secure refresh token"""
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """Hash refresh token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token_db(
    db: Session, user_id: uuid.UUID
) -> tuple[str, RefreshToken]:
    """Create and store refresh token in database"""
    raw_token = create_refresh_token()
    token_hash = hash_refresh_token(raw_token)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    db_refresh_token = RefreshToken(
        user_id=user_id, token_hash=token_hash, expires_at=expires_at, revoked=False
    )
    db.add(db_refresh_token)
    db.commit()
    db.refresh(db_refresh_token)

    return raw_token, db_refresh_token


def verify_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    """Verify refresh token and return the token record if valid"""
    token_hash = hash_refresh_token(token)
    db_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked.is_(False),
            RefreshToken.expires_at > datetime.utcnow(),
        )
        .first()
    )

    return db_token


def revoke_refresh_token(db: Session, token_hash: str) -> bool:
    """Revoke a refresh token"""
    db_token = (
        db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    )
    if db_token:
        db_token.revoked = True
        db.commit()
        return True
    return False


def decode_token(token: str) -> Optional[dict]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        return None
