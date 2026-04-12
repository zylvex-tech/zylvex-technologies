from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import (
    UserCreate, UserResponse, Token, LoginRequest,
    RefreshTokenRequest
)
from app.crud.user import create_user, authenticate_user
from app.core.security import (
    create_access_token, create_refresh_token_db, verify_refresh_token,
    revoke_refresh_token, hash_refresh_token
)
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        db_user = create_user(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return db_user


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token, _ = create_refresh_token_db(db, user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
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
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout")
def logout(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Revoke a refresh token"""
    token_hash = hash_refresh_token(token_data.refresh_token)
    success = revoke_refresh_token(db, token_hash)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found"
        )

    return {"message": "Successfully logged out"}


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
