from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import (
    User, Profile, Address, Transaction, Connection,
    UserType, DeliveryMethod, TransactionStatus,
    init_db, get_db,
)
from schemas import (
    RegisterRequest, LoginRequest, TokenResponse, VerifyRequest,
    ProfileCreate, ProfileUpdate, ProfileResponse, ProfileListResponse,
    TransactionCreate, TransactionResponse, CheckoutSessionResponse,
    DashboardStats, AdminProfileAction,
)
from auth import (
    hash_password, verify_password, create_token,
    get_current_user, require_admin,
)
from encryption import encrypt_value
from payments import create_checkout_session, construct_webhook_event
from config import STRIPE_PUBLISHABLE_KEY

app = FastAPI(title="Prompt Vault — Crowdsourced Food Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.post("/auth/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=req.email,
        phone=req.phone,
        display_name=req.display_name,
        user_type=UserType(req.user_type.value),
        password_hash=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id, user.user_type.value)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        user_type=user.user_type.value,
        display_name=user.display_name,
    )


@app.post("/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user.id, user.user_type.value)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        user_type=user.user_type.value,
        display_name=user.display_name,
    )


@app.post("/auth/verify")
def verify_account(req: VerifyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # In production, validate code against sent verification code
    # For MVP, any 6-digit code works
    if len(req.code) == 6 and req.code.isdigit():
        current_user.is_verified = True
        db.commit()
        return {"message": "Account verified"}
    raise HTTPException(status_code=400, detail="Invalid verification code")


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

def build_profile_response(profile: Profile, db: Session) -> ProfileResponse:
    meals = db.query(func.count(Transaction.id)).filter(
        Transaction.receiver_id == profile.user_id,
        Transaction.status == TransactionStatus.completed,
    ).scalar() or 0

    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        display_name=profile.user.display_name,
        city=profile.city,
        state=profile.state,
        story=profile.story,
        is_verified=profile.is_verified,
        meals_received=meals,
        member_since=profile.created_at.strftime("%B %Y") if profile.created_at else "",
    )


@app.get("/profiles", response_model=ProfileListResponse)
def list_profiles(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    city: str | None = None,
    state: str | None = None,
    sort: str = "newest",
    search: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Profile).filter(Profile.is_public == True, Profile.is_flagged == False)  # noqa: E712

    if city:
        q = q.filter(func.lower(Profile.city) == city.lower())
    if state:
        q = q.filter(func.upper(Profile.state) == state.upper())
    if search:
        q = q.join(User).filter(
            (func.lower(Profile.city).contains(search.lower()))
            | (func.lower(Profile.story).contains(search.lower()))
            | (func.lower(User.display_name).contains(search.lower()))
        )

    if sort == "newest":
        q = q.order_by(Profile.created_at.desc())
    else:
        q = q.order_by(Profile.created_at.desc())

    total = q.count()
    profiles = q.offset((page - 1) * per_page).limit(per_page).all()

    return ProfileListResponse(
        profiles=[build_profile_response(p, db) for p in profiles],
        total=total,
        page=page,
        per_page=per_page,
    )


@app.get("/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return build_profile_response(profile, db)


@app.post("/profiles", response_model=ProfileResponse)
def create_profile(
    req: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.user_type not in (UserType.receiver, UserType.both):
        raise HTTPException(status_code=403, detail="Only receivers can create profiles")

    existing = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile = Profile(
        user_id=current_user.id,
        city=req.city,
        state=req.state.upper(),
        story=req.story,
    )
    db.add(profile)

    address = Address(
        user_id=current_user.id,
        encrypted_street=encrypt_value(req.street),
        encrypted_zip=encrypt_value(req.zip_code),
        city=req.city,
        state=req.state.upper(),
    )
    db.add(address)
    db.commit()
    db.refresh(profile)

    return build_profile_response(profile, db)


@app.put("/profiles/{profile_id}", response_model=ProfileResponse)
def update_profile(
    profile_id: str,
    req: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.id == profile_id, Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if req.city is not None:
        profile.city = req.city
    if req.state is not None:
        profile.state = req.state.upper()
    if req.story is not None:
        profile.story = req.story

    db.commit()
    db.refresh(profile)
    return build_profile_response(profile, db)


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

@app.post("/transactions", response_model=CheckoutSessionResponse)
def create_transaction(
    req: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    receiver = db.query(User).filter(User.id == req.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Recipient not found")

    txn = Transaction(
        giver_id=current_user.id,
        receiver_id=req.receiver_id,
        amount=req.amount,
        tip_amount=req.tip_amount,
        delivery_method=DeliveryMethod(req.delivery_method.value),
        message=req.message,
        status=TransactionStatus.pending,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    try:
        session = create_checkout_session(
            amount_cents=int(req.amount * 100),
            tip_cents=int(req.tip_amount * 100),
            receiver_name=receiver.display_name,
            transaction_id=txn.id,
        )
        txn.stripe_payment_intent_id = session.id
        db.commit()
        return CheckoutSessionResponse(session_url=session.url, session_id=session.id)
    except Exception as e:
        # If Stripe isn't configured, mark as completed for demo purposes
        txn.status = TransactionStatus.completed
        db.commit()
        return CheckoutSessionResponse(
            session_url="",
            session_id=f"demo_{txn.id}",
        )


@app.get("/transactions/my", response_model=list[TransactionResponse])
def my_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    txns = (
        db.query(Transaction)
        .filter(Transaction.giver_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .limit(50)
        .all()
    )

    results = []
    for t in txns:
        receiver = db.query(User).filter(User.id == t.receiver_id).first()
        profile = db.query(Profile).filter(Profile.user_id == t.receiver_id).first()
        results.append(TransactionResponse(
            id=t.id,
            receiver_name=receiver.display_name if receiver else "Unknown",
            receiver_city=profile.city if profile else "",
            amount=float(t.amount),
            tip_amount=float(t.tip_amount),
            delivery_method=t.delivery_method.value,
            status=t.status.value,
            message=t.message,
            created_at=t.created_at.isoformat() if t.created_at else "",
        ))
    return results


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    completed = db.query(Transaction).filter(
        Transaction.giver_id == current_user.id,
        Transaction.status == TransactionStatus.completed,
    )

    total_meals = completed.count()
    total_given = float(
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.giver_id == current_user.id,
            Transaction.status == TransactionStatus.completed,
        )
        .scalar() or 0
    )
    families = (
        db.query(func.count(func.distinct(Transaction.receiver_id)))
        .filter(
            Transaction.giver_id == current_user.id,
            Transaction.status == TransactionStatus.completed,
        )
        .scalar() or 0
    )

    recent_txns = (
        db.query(Transaction)
        .filter(Transaction.giver_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .limit(10)
        .all()
    )

    recent = []
    for t in recent_txns:
        receiver = db.query(User).filter(User.id == t.receiver_id).first()
        profile = db.query(Profile).filter(Profile.user_id == t.receiver_id).first()
        recent.append(TransactionResponse(
            id=t.id,
            receiver_name=receiver.display_name if receiver else "Unknown",
            receiver_city=profile.city if profile else "",
            amount=float(t.amount),
            tip_amount=float(t.tip_amount),
            delivery_method=t.delivery_method.value,
            status=t.status.value,
            message=t.message,
            created_at=t.created_at.isoformat() if t.created_at else "",
        ))

    return DashboardStats(
        total_meals=total_meals,
        total_given=total_given,
        families_helped=families,
        recent_transactions=recent,
    )


# ---------------------------------------------------------------------------
# Stripe Webhook
# ---------------------------------------------------------------------------

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = construct_webhook_event(payload, sig)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        txn_id = session.get("metadata", {}).get("transaction_id")
        if txn_id:
            txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
            if txn:
                txn.status = TransactionStatus.completed
                txn.stripe_payment_intent_id = session.get("payment_intent")
                db.commit()

    return {"received": True}


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

@app.get("/admin/profiles/pending")
def admin_pending_profiles(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    profiles = db.query(Profile).filter(Profile.is_verified == False).all()  # noqa: E712
    return [build_profile_response(p, db) for p in profiles]


@app.post("/admin/profiles/{profile_id}/approve")
def admin_approve_profile(
    profile_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile.is_verified = True
    profile.is_flagged = False
    db.commit()
    return {"message": "Profile approved"}


@app.post("/admin/profiles/{profile_id}/flag")
def admin_flag_profile(
    profile_id: str,
    body: AdminProfileAction,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile.is_flagged = True
    profile.is_public = False
    db.commit()
    return {"message": "Profile flagged"}


@app.get("/admin/transactions")
def admin_transactions(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    txns = db.query(Transaction).order_by(Transaction.created_at.desc()).limit(100).all()
    results = []
    for t in txns:
        giver = db.query(User).filter(User.id == t.giver_id).first()
        receiver = db.query(User).filter(User.id == t.receiver_id).first()
        results.append({
            "id": t.id,
            "giver_name": giver.display_name if giver else "Unknown",
            "receiver_name": receiver.display_name if receiver else "Unknown",
            "amount": float(t.amount),
            "tip_amount": float(t.tip_amount),
            "delivery_method": t.delivery_method.value,
            "status": t.status.value,
            "created_at": t.created_at.isoformat() if t.created_at else "",
        })
    return results


@app.get("/admin/stats")
def admin_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return {
        "total_users": db.query(func.count(User.id)).scalar(),
        "total_profiles": db.query(func.count(Profile.id)).scalar(),
        "total_transactions": db.query(func.count(Transaction.id)).scalar(),
        "total_amount": float(
            db.query(func.sum(Transaction.amount))
            .filter(Transaction.status == TransactionStatus.completed)
            .scalar() or 0
        ),
        "pending_profiles": db.query(func.count(Profile.id)).filter(Profile.is_verified == False).scalar(),  # noqa: E712
        "flagged_profiles": db.query(func.count(Profile.id)).filter(Profile.is_flagged == True).scalar(),  # noqa: E712
    }


# ---------------------------------------------------------------------------
# Config endpoint (public Stripe key for frontend)
# ---------------------------------------------------------------------------

@app.get("/config/stripe")
def stripe_config():
    return {"publishable_key": STRIPE_PUBLISHABLE_KEY}
