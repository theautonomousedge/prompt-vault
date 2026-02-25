# API Reference — Prompt Vault

> Detailed reference for all API routes, database models, and schemas.
> Referenced from CLAUDE.md. Update this file when routes/models change.

---

## API ROUTES (22 total)

### Health (1)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | Service health check → `{"status": "ok"}` |

### Auth (3)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | None | Register with email, password, display_name, user_type. Returns JWT + user info |
| POST | `/auth/login` | None | Login with email + password. Returns JWT + user info |
| POST | `/auth/verify` | Bearer | Verify account. MVP: any 6-digit code works |

### Profiles (4)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/profiles` | None | List public profiles. Query params: `city`, `state`, `search`, `sort`, `page`, `per_page` |
| GET | `/profiles/{id}` | None | Single profile with meal count and member_since |
| POST | `/profiles` | Bearer | Create receiver profile (city, state, story, street, zip_code). Address is AES encrypted |
| PUT | `/profiles/{id}` | Bearer | Update own profile (city, state, story) |

### Transactions (2)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/transactions` | Bearer | Create donation. With Stripe: returns checkout URL. Without: demo mode (auto-completes) |
| GET | `/transactions/my` | Bearer | Donor's last 50 transactions with receiver names |

### Dashboard (1)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/dashboard/stats` | Bearer | Donor stats: total_meals, total_given, families_helped, recent_transactions |

### Admin (5)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/admin/profiles/pending` | Admin | List unverified profiles |
| POST | `/admin/profiles/{id}/approve` | Admin | Approve profile (sets is_verified=True, is_flagged=False) |
| POST | `/admin/profiles/{id}/flag` | Admin | Flag profile (sets is_flagged=True, is_public=False). Body: `{reason}` |
| GET | `/admin/transactions` | Admin | Last 100 transactions with giver/receiver names |
| GET | `/admin/stats` | Admin | Platform totals: users, profiles, transactions, amount, pending, flagged |

### Stripe (1)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/webhook/stripe` | Stripe sig | Handles `checkout.session.completed` → marks transaction completed |

### Config (1)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/config/stripe` | None | Returns `{publishable_key}` for frontend Stripe init |

---

## DATABASE MODELS (5)

### User
| Field | Type | Notes |
|-------|------|-------|
| id | str (UUID) | Primary key, auto-generated |
| email | str | Unique, required |
| phone | str | Optional |
| display_name | str | Required |
| user_type | Enum | `giver`, `receiver`, `both`, `admin` |
| password_hash | str | bcrypt hashed |
| is_verified | bool | Default False |
| created_at | datetime | Auto UTC |

### Profile
| Field | Type | Notes |
|-------|------|-------|
| id | str (UUID) | Primary key |
| user_id | str (FK → User) | One-to-one |
| city | str | Required |
| state | str | 2-letter uppercase |
| story | str | Max 500 chars |
| is_public | bool | Default True |
| is_verified | bool | Default False (admin approves) |
| is_flagged | bool | Default False |
| created_at | datetime | Auto UTC |

### Address (Encrypted)
| Field | Type | Notes |
|-------|------|-------|
| id | str (UUID) | Primary key |
| user_id | str (FK → User) | One-to-one |
| encrypted_street | str | Fernet AES-256 encrypted |
| encrypted_zip | str | Fernet AES-256 encrypted |
| city | str | Plaintext (for filtering) |
| state | str | Plaintext (for filtering) |

### Transaction
| Field | Type | Notes |
|-------|------|-------|
| id | str (UUID) | Primary key |
| giver_id | str (FK → User) | Donor |
| receiver_id | str (FK → User) | Recipient |
| amount | float | Meal gift card amount |
| tip_amount | float | Platform tip |
| delivery_method | Enum | `doordash`, `ubereats`, `instacart` |
| gift_card_code | str | **UNUSED** — placeholder for Phase 4 |
| status | Enum | `pending`, `completed`, `failed`, `refunded` |
| stripe_payment_intent_id | str | Stripe session/payment ID |
| message | str | Optional donor message (max 500) |
| created_at | datetime | Auto UTC |

### Connection (UNUSED)
| Field | Type | Notes |
|-------|------|-------|
| id | str (UUID) | Primary key |
| giver_id | str (FK → User) | — |
| receiver_id | str (FK → User) | — |
| relationship_type | str | — |
| is_confirmed | bool | — |

> **Note**: Connection model is defined but has no routes or UI. Deferred to Phase 5.

---

## PYDANTIC SCHEMAS (in `backend/schemas.py`)

### Request Schemas
- **RegisterRequest**: email (EmailStr), password (min 8), display_name, phone?, user_type
- **LoginRequest**: email, password
- **VerifyRequest**: code (6-digit string)
- **ProfileCreate**: city, state (2 chars), story (10-500 chars), street, zip_code
- **ProfileUpdate**: city?, state?, story?
- **TransactionCreate**: receiver_id, amount (>0), tip_amount (>=0), delivery_method, message?
- **AdminProfileAction**: reason?

### Response Schemas
- **TokenResponse**: access_token, token_type, user_id, user_type, display_name
- **ProfileResponse**: id, user_id, display_name, city, state, story, is_verified, meals_received, member_since
- **ProfileListResponse**: profiles[], total, page, per_page
- **TransactionResponse**: id, receiver_name, receiver_city, amount, tip_amount, delivery_method, status, message, created_at
- **CheckoutSessionResponse**: session_url, session_id
- **DashboardStats**: total_meals, total_given, families_helped, recent_transactions[]
