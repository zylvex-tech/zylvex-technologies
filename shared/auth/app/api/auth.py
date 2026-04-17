import os
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    Token,
    LoginRequest,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.crud.user import create_user, authenticate_user, get_user_by_email
from app.core.security import (
    create_access_token,
    create_refresh_token_db,
    verify_refresh_token,
    revoke_refresh_token,
    hash_refresh_token,
    get_password_hash,
)
from app.core.config import settings
from app.middleware.auth import get_current_user
from app.models.user import User, EmailVerification, PasswordReset, RefreshToken
from app.utils.email import send_verification_email, send_password_reset_email

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        db_user = create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Generate email verification token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    email_verification = EmailVerification(
        user_id=db_user.id,
        token=token,
        expires_at=expires_at,
        used=False,
    )
    db.add(email_verification)
    db.commit()

    # Send verification email (falls back to console logging if SendGrid not set)
    frontend_url = settings.FRONTEND_URL
    send_verification_email(db_user.email, token, frontend_url)

    return db_user


@router.get("/verify-email")
def verify_email(
    token: str = Query(..., description="Email verification token"),
    db: Session = Depends(get_db),
):
    """Verify user's email address using the token from the verification email."""
    verification = (
        db.query(EmailVerification)
        .filter(EmailVerification.token == token)
        .first()
    )

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    if verification.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has already been used",
        )

    if verification.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired",
        )

    # Mark user as verified
    user = db.query(User).filter(User.id == verification.user_id).first()
    if user:
        user.is_verified = True

    # Mark token as used
    verification.used = True
    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return access + refresh tokens"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is deactivated"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in.",
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token, _ = create_refresh_token_db(db, user.id)

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
def refresh(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token and rotate refresh token"""
    db_token = verify_refresh_token(db, token_data.refresh_token)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = db_token.user_id

    # Revoke the old refresh token (rotation)
    old_token_hash = hash_refresh_token(token_data.refresh_token)
    revoke_refresh_token(db, old_token_hash)

    # Issue new tokens
    access_token = create_access_token(data={"sub": str(user_id)})
    new_refresh_token, _ = create_refresh_token_db(db, user_id)

    return Token(
        access_token=access_token, refresh_token=new_refresh_token, token_type="bearer"
    )


@router.post("/logout")
def logout(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Revoke a refresh token"""
    token_hash = hash_refresh_token(token_data.refresh_token)
    success = revoke_refresh_token(db, token_hash)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found"
        )

    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Request a password reset email.

    Always returns 200 regardless of whether the email exists
    (prevents user enumeration).
    """
    user = get_user_by_email(db, body.email)

    if user:
        # Generate reset token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        password_reset = PasswordReset(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
            used=False,
        )
        db.add(password_reset)
        db.commit()

        # Send reset email
        frontend_url = settings.FRONTEND_URL
        send_password_reset_email(user.email, token, frontend_url)

    return {
        "message": (
            "If an account with that email exists,"
            " a password reset link has been sent."
        )
    }


@router.post("/reset-password")
def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """Reset password using a valid reset token."""
    reset_record = (
        db.query(PasswordReset)
        .filter(PasswordReset.token == body.token)
        .first()
    )

    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    if reset_record.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has already been used",
        )

    if reset_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired",
        )

    # Update user password
    user = db.query(User).filter(User.id == reset_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    user.hashed_password = get_password_hash(body.new_password)

    # Mark token as used
    reset_record.used = True

    # Invalidate all existing refresh tokens (security: log out all sessions)
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked.is_(False),
    ).update({"revoked": True})

    db.commit()

    return {"message": "Password reset successfully"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.get("/verify")
def verify_token(current_user: User = Depends(get_current_user)):
    """Verify token and return user identity data (used by other services)"""
    return {
        "id": str(current_user.id),
        "sub": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
    }
