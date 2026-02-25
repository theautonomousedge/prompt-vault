# Prompt Vault — Crowdsourced Food Platform

A peer-to-peer food gifting marketplace. Donors browse profiles of people who need meals and send them food via digital gift cards. No cash, no addresses exposed — just food to mouths.

## Architecture

```
frontend/          Vanilla HTML/CSS/JS — no frameworks
backend/           Python FastAPI + SQLAlchemy + SQLite (PostgreSQL-ready)
```

**Key features:**
- AES-256 encrypted addresses — never exposed to donors
- Stripe Checkout for payments with platform tip support
- JWT auth with role-based access (donor, receiver, admin)
- Mobile-responsive dark theme with warm earth tones

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values. To generate a Fernet encryption key:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

For Stripe test keys, visit [dashboard.stripe.com](https://dashboard.stripe.com).

### 3. Seed the database

```bash
cd backend
python seed.py
```

This creates sample users:
- **Admin:** admin@promptvault.org / admin1234
- **Donor:** donor@test.com / donor1234
- **Recipients:** maria@test.com, james@test.com, aisha@test.com, carlos@test.com, sarah@test.com / password123

### 4. Start the backend

```bash
cd backend
uvicorn main:app --reload
```

API runs at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### 5. Open the frontend

Open `frontend/index.html` in your browser. For best results, serve via a local server:

```bash
cd frontend
python -m http.server 3000
```

Then visit `http://localhost:3000`.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/register | Register a new user |
| POST | /auth/login | Log in, receive JWT |
| POST | /auth/verify | Verify email/phone |
| GET | /profiles | List public recipient profiles |
| GET | /profiles/{id} | Get single profile |
| POST | /profiles | Create recipient profile |
| PUT | /profiles/{id} | Update profile |
| POST | /transactions | Create donation (Stripe checkout) |
| GET | /transactions/my | Donor's transaction history |
| GET | /dashboard/stats | Donor impact stats |
| GET | /admin/profiles/pending | Pending profiles (admin) |
| POST | /admin/profiles/{id}/approve | Approve profile (admin) |
| POST | /admin/profiles/{id}/flag | Flag profile (admin) |
| GET | /admin/transactions | Transaction log (admin) |
| GET | /admin/stats | Platform analytics (admin) |
| POST | /webhook/stripe | Stripe payment webhook |

## Test Flow

1. Register as a donor at `/signup.html`
2. Browse recipient profiles at `/browse.html`
3. Click "Send a Meal" on a profile
4. Complete the checkout flow at `/donate.html`
5. Check your impact at `/dashboard.html`
6. Log in as admin to moderate at `/admin.html`
