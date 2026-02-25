from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserTypeEnum(str, Enum):
    giver = "giver"
    receiver = "receiver"
    both = "both"


class DeliveryMethodEnum(str, Enum):
    doordash = "doordash"
    ubereats = "ubereats"
    instacart = "instacart"


# --- Auth ---

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str = Field(min_length=1, max_length=100)
    phone: Optional[str] = None
    user_type: UserTypeEnum = UserTypeEnum.giver


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    user_type: str
    display_name: str


class VerifyRequest(BaseModel):
    code: str


# --- Profiles ---

class ProfileCreate(BaseModel):
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=2)
    story: str = Field(min_length=10, max_length=500)
    street: str = Field(min_length=1, max_length=200)
    zip_code: str = Field(min_length=5, max_length=10)


class ProfileUpdate(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    story: Optional[str] = Field(None, max_length=500)


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    display_name: str
    city: str
    state: str
    story: str
    is_verified: bool
    meals_received: int = 0
    member_since: str

    class Config:
        from_attributes = True


class ProfileListResponse(BaseModel):
    profiles: list[ProfileResponse]
    total: int
    page: int
    per_page: int


# --- Transactions ---

class TransactionCreate(BaseModel):
    receiver_id: str
    amount: float = Field(gt=0)
    tip_amount: float = Field(ge=0, default=0)
    delivery_method: DeliveryMethodEnum
    message: Optional[str] = Field(None, max_length=500)


class TransactionResponse(BaseModel):
    id: str
    receiver_name: str
    receiver_city: str
    amount: float
    tip_amount: float
    delivery_method: str
    status: str
    message: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class CheckoutSessionResponse(BaseModel):
    session_url: str
    session_id: str


# --- Dashboard ---

class DashboardStats(BaseModel):
    total_meals: int
    total_given: float
    families_helped: int
    recent_transactions: list[TransactionResponse]


# --- Admin ---

class AdminProfileAction(BaseModel):
    reason: Optional[str] = None
