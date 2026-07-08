"""Authentication endpoint for admin and citizen login/signup."""

from datetime import datetime, timedelta, timezone
import hashlib
import uuid
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud import firestore
from pydantic import BaseModel, EmailStr

from app.api.deps import SettingsDep, FirestoreDep
from app.db.collections import CollectionNames, get_collection_ref

router = APIRouter(tags=["auth"])


def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    token_type: str = "bearer"


class SignUpRequest(BaseModel):
    """Schema for citizen signup request."""
    email: EmailStr
    password: str
    full_name: str
    mobile_number: str


@router.post(
    "/signup",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Citizen Sign Up",
    description="Registers a new citizen user in the database and returns a session token.",
)
async def signup(
    payload: SignUpRequest,
    settings: SettingsDep,
    db: FirestoreDep,
) -> LoginResponse:
    """Sign up a new citizen user and issue a JWT token."""
    users_ref = get_collection_ref(db, CollectionNames.USERS)
    
    # Check if user already exists
    existing_query = (
        users_ref.where(filter=firestore.FieldFilter("email", "==", payload.email))
        .limit(1)
        .get()
    )
    if len(existing_query) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists",
        )

    # Save citizen user in USERS collection
    user_id = uuid.uuid4().hex
    user_data = {
        "id": user_id,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "full_name": payload.full_name,
        "mobile_number": payload.mobile_number,
        "created_at": datetime.now(timezone.utc),
    }
    
    try:
        users_ref.document(user_id).set(user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save account details",
        ) from e

    # Generate JWT token
    expiration = datetime.now(timezone.utc) + timedelta(hours=24)
    token_data = {
        "sub": payload.email,
        "exp": expiration,
    }
    
    try:
        token = jwt.encode(token_data, settings.jwt_secret, algorithm="HS256")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate session token",
        ) from e

    return LoginResponse(access_token=token)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign In",
    description="Authenticates admin or citizen users and returns a JSON Web Token (JWT).",
)
async def login(
    payload: LoginRequest,
    settings: SettingsDep,
    db: FirestoreDep,
) -> LoginResponse:
    """Validate credentials and return JWT token."""
    # 1. Check if admin credentials match
    if (
        payload.email == settings.admin_email
        and payload.password == settings.admin_password
    ):
        expiration = datetime.now(timezone.utc) + timedelta(hours=24)
        token_data = {
            "sub": payload.email,
            "exp": expiration,
        }
        token = jwt.encode(token_data, settings.jwt_secret, algorithm="HS256")
        return LoginResponse(access_token=token)

    # 2. Check if a registered user in Firestore matches
    users_ref = get_collection_ref(db, CollectionNames.USERS)
    user_query = (
        users_ref.where(filter=firestore.FieldFilter("email", "==", payload.email))
        .limit(1)
        .get()
    )
    
    if len(user_query) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user_doc = user_query[0].to_dict()
    if user_doc.get("password_hash") != hash_password(payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate JWT token expiring in 24 hours
    expiration = datetime.now(timezone.utc) + timedelta(hours=24)
    token_data = {
        "sub": payload.email,
        "exp": expiration,
    }

    try:
        token = jwt.encode(token_data, settings.jwt_secret, algorithm="HS256")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate session token",
        ) from e

    return LoginResponse(access_token=token)
