# Architecture Blueprint — Prompt Vault

> SINGLE SOURCE OF TRUTH for system design. Read before making structural changes.
> If you want to change anything here, propose it first — don't just do it.

---

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (port 8000)                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  API Routes   │  │  Static Files │  │ Stripe Webhook│  │
│  │  (main.py)    │  │  (frontend/) │  │  (main.py)    │  │
│  └──────┬───────┘  └──────────────┘  └───────┬───────┘  │
│         │                                      │          │
│  ┌──────┴───────┐                    ┌────────┴────────┐ │
│  │  SQLAlchemy   │                    │  Stripe API     │ │
│  │  ORM Layer    │                    │  (payments.py)  │ │
│  │  (models.py)  │                    └─────────────────┘ │
│  └──────┬───────┘                                        │
│         │                                                 │
│  ┌──────┴───────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  SQLite DB    │  │  Fernet AES  │  │  JWT + bcrypt │  │
│  │  (dev.db)     │  │  (addresses) │  │  (auth.py)    │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Request Flow

```
Browser → FastAPI (port 8000)
  ├── /api routes → auth check → SQLAlchemy → SQLite → JSON response
  ├── /webhook/stripe → signature verify → update transaction
  └── /* static → serve frontend HTML/CSS/JS files
```

## Key Architecture Rules

1. **Everything runs on one server** — FastAPI serves both API and frontend on port 8000
2. **Backend is a monolith** — All 22 routes live in `main.py`. Do NOT split into routers until Phase 5
3. **Frontend is frameworkless** — Vanilla HTML/CSS/JS. Each page loads 3 shared JS files (api, auth, app)
4. **Page routing is file-based** — `browse.html`, `donate.html`, etc. No SPA router
5. **Auth is stateless JWT** — 24-hour tokens, no server-side sessions. Bearer header on protected routes
6. **Addresses are encrypted at rest** — Fernet AES-256. Never exposed to donors, even in API responses
7. **Stripe is optional** — Demo mode auto-completes transactions when keys aren't configured
8. **Database is SQLite for dev** — PostgreSQL for production (same SQLAlchemy models work for both)

## File Ownership

| Area | Files | Rule |
|------|-------|------|
| All API routes | `main.py` | Single file, do not split |
| All models | `models.py` | Single file, 5 models |
| All schemas | `schemas.py` | Pydantic validation |
| All frontend logic | `app.js` | Page handlers keyed by `data-page` |
| All API calls | `api.js` | Thin wrapper with auth injection |
| Auth state | `auth.js` | Token storage, nav updates, guards |
| Styles | `style.css` | Single file, CSS custom properties |

## Data Flow: Donation

```
1. Donor clicks "Send a Meal" on profile.html
2. → donate.html loads with receiver_id, name, city from URL params
3. Donor picks amount, delivery method, tip, writes message
4. Frontend POSTs to /transactions with Bearer token
5. Backend creates Transaction (status: pending)
6. Backend calls Stripe → returns checkout URL (or demo mode)
7. If Stripe: redirect to Stripe → success.html on completion
8. If demo: auto-complete transaction → show inline confirmation
9. Webhook updates transaction status to completed
10. Dashboard stats reflect new donation
```
