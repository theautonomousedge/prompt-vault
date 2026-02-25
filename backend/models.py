import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, ForeignKey, Numeric, Enum, LargeBinary, create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from config import DATABASE_URL

Base = declarative_base()


def gen_uuid():
    return str(uuid.uuid4())


class UserType(str, enum.Enum):
    giver = "giver"
    receiver = "receiver"
    both = "both"
    admin = "admin"


class DeliveryMethod(str, enum.Enum):
    doordash = "doordash"
    ubereats = "ubereats"
    instacart = "instacart"


class TransactionStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    display_name = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False, default=UserType.giver)
    password_hash = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="user", uselist=False)
    address = relationship("Address", back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    story = Column(Text, nullable=False)
    is_public = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    encrypted_street = Column(LargeBinary, nullable=False)
    encrypted_zip = Column(LargeBinary, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)

    user = relationship("User", back_populates="address")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=gen_uuid)
    giver_id = Column(String, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    tip_amount = Column(Numeric(10, 2), default=0)
    delivery_method = Column(Enum(DeliveryMethod), nullable=False)
    gift_card_code = Column(LargeBinary, nullable=True)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.pending)
    stripe_payment_intent_id = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    giver = relationship("User", foreign_keys=[giver_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


class Connection(Base):
    __tablename__ = "connections"

    id = Column(String, primary_key=True, default=gen_uuid)
    giver_id = Column(String, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(String, ForeignKey("users.id"), nullable=False)
    relationship_type = Column(String, nullable=True)
    is_confirmed = Column(Boolean, default=False)

    giver = relationship("User", foreign_keys=[giver_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
