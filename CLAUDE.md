# CLAUDE.md — Prompt Vault (Food Gifting MVP)

> **MANDATORY**: Every agent MUST read this file at session start. No exceptions.

---

## FAILSAFE RULES — DO NOT VIOLATE UNDER ANY CIRCUMSTANCES

1. **NEVER overwrite, truncate, or delete this file.** Only APPEND or UPDATE specific sections.
2. **NEVER remove sections from this file.** You may update content within sections but the section headers and structure must remain intact.
3. **NEVER overwrite `scripts/handoff.md`.** Only APPEND new session entries. Previous sessions' handoffs must be preserved as a running log.
4. **Before writing to CLAUDE.md or handoff.md**, READ the current contents first. Use the Edit tool to modify specific sections — do NOT use the Write tool to overwrite the entire file.
5. **If you are unsure whether an edit will destroy content**, ask the user before proceeding.
6. **The file structure section, known gaps table, and phase roadmap are living documents** — update them, don't replace them. Add new entries, mark completed items, update line counts.
7. **NEVER use Write tool on CLAUDE.md** — always use Edit tool to change specific sections. This prevents accidental overwrites.
8. **At session end, if CLAUDE.md or handoff.md appear empty or corrupted**, reconstruct from git history: `git show HEAD:CLAUDE.md`
9. **NEVER skip the end-of-session protocol.** Even if the user says "just push it" — update CLAUDE.md and handoff.md FIRST.
10. **Backup check**: Before pushing, run `wc -l CLAUDE.md scripts/handoff.md` and verify both files have substantial content. If either is under 20 lines, something went wrong — investigate before pushing.

---

## PROJECT IDENTITY

- **Name**: Prompt Vault — Food Gifting Platform
- **Stack**: Python (FastAPI) backend + Vanilla HTML/CSS/JS frontend
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **Auth**: JWT + bcrypt
- **Payments**: Stripe Checkout
- **Encryption**: Fernet AES-256 for addresses
- **Branch**: `claude/food-gifting-mvp-FFgJW`

---

## FILE STRUCTURE (Last Updated: 2026-02-25, Session 1 End)

```
prompt-vault/
├── CLAUDE.md                    # THIS FILE — project rules & state (READ FIRST)
├── .env.example                 # Environment variable template (8 vars)
├── .gitignore                   # Git ignore rules
├── README.md                    # Project overview & setup instructions
├── requirements.txt             # Python dependencies (10 packages, pinned)
│
├── backend/                     # FastAPI Python backend
│   ├── main.py          (510L)  # App entry + 22 API routes + static file serving
│   ├── models.py        (130L)  # SQLAlchemy: User, Profile, Address, Transaction, Connection
│   ├── schemas.py       (125L)  # Pydantic request/response validation
│   ├── auth.py           (56L)  # JWT + bcrypt + role guards
│   ├── encryption.py     (29L)  # Fernet AES-256 for addresses
│   ├── config.py         (14L)  # Env var loader + FRONTEND_URL
│   ├── payments.py       (53L)  # Stripe checkout + configurable success/cancel URLs
│   └── seed.py          (162L)  # Dev seeder (5 recipients, 1 admin, 1 donor, 3 txns)
│
├── frontend/                    # Static frontend (no build tools, no framework)
│   ├── index.html       (161L)  # Landing — hero, stats, featured profiles, CTAs
│   ├── signup.html      (170L)  # Register + login + receiver profile setup
│   ├── browse.html       (73L)  # Profile grid — filters, search, pagination
│   ├── profile.html      (68L)  # Single profile — story, badge, donate CTA
│   ├── donate.html      (136L)  # Meal gifting — amount, delivery, tip, summary
│   ├── success.html      (52L)  # Payment success page (Stripe redirect target)
│   ├── cancel.html       (52L)  # Payment cancelled page (Stripe redirect target)
│   ├── dashboard.html    (72L)  # Donor impact stats + activity feed
│   ├── admin.html       (122L)  # Admin panel — pending, transactions, analytics
│   ├── css/
│   │   └── style.css  (1096L)  # Design system — dark earth theme, 2 breakpoints
│   └── js/
│       ├── app.js       (529L)  # All 7 page handlers + utilities
│       ├── api.js        (65L)  # 14 API methods, same-origin aware
│       └── auth.js       (87L)  # Token management, nav state, route guards
│
└── scripts/                     # Session management & ops
    └── handoff.md               # Agent-to-agent handoff log (append-only)
```

**Total: ~4,037 lines across 21 source files**

---

## SESSION PROTOCOL — MANDATORY FOR EVERY AGENT

### At Session START:
1. Read this CLAUDE.md completely
2. Read `scripts/handoff.md` for previous session context
3. Check `git log --oneline -10` to see recent work
4. Confirm you're on branch `claude/food-gifting-mvp-FFgJW`

### During Session:
1. Use TodoWrite to track all tasks
2. Make small, atomic commits with clear messages
3. Do NOT restructure the file layout without explicit approval
4. Do NOT add new frameworks or build tools
5. Do NOT create files unless absolutely necessary
6. Keep backend in `backend/`, frontend in `frontend/`, scripts in `scripts/`

### At Session END (BEFORE final push — DO NOT SKIP):
1. **Update this CLAUDE.md** — refresh the file structure section with current line counts
2. **Update `scripts/handoff.md`** — full handoff report (see template below)
3. **Commit both files** with message: `chore: end-of-session update — CLAUDE.md + handoff`
4. **Push** to `claude/food-gifting-mvp-FFgJW`

---

## CODING RULES

### Python Backend:
- FastAPI with SQLAlchemy ORM (sync, not async)
- All routes live in `main.py` (monolith for MVP — do NOT split into routers yet)
- All models in `models.py`, all schemas in `schemas.py`
- Use dependency injection for auth (`get_current_user`, `require_admin`)
- SQLite database file is `food_gifting.db` in project root (gitignored)
- Run with: `cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000`

### Frontend:
- Vanilla HTML/CSS/JS — NO frameworks, NO build tools, NO npm
- Each HTML page includes `css/style.css`, `js/api.js`, `js/auth.js`, `js/app.js`
- Page detection via `document.body.dataset.page` attribute
- API base URL is `http://localhost:8000` in `api.js`
- Serve with any static server or just open files directly

### Git:
- Branch: `claude/food-gifting-mvp-FFgJW` — NEVER push to main
- Small, atomic commits
- Push with: `git push -u origin claude/food-gifting-mvp-FFgJW`

---

## API ROUTES REFERENCE (22 total)

### Auth (3):
- `POST /auth/register` — Register with email, password, display_name, user_type
- `POST /auth/login` — Login, returns JWT
- `POST /auth/verify` — Verify account (MVP: any 6-digit code)

### Profiles (4):
- `GET /profiles` — List public profiles (filters: city, state, search, sort, pagination)
- `GET /profiles/{id}` — Single profile with meal count
- `POST /profiles` — Create receiver profile (encrypted address)
- `PUT /profiles/{id}` — Update profile

### Transactions (2):
- `POST /transactions` — Create donation + Stripe checkout (or demo mode)
- `GET /transactions/my` — Donor's history (last 50)

### Dashboard (1):
- `GET /dashboard/stats` — Donor impact stats

### Admin (5):
- `GET /admin/profiles/pending` — Unverified profiles
- `POST /admin/profiles/{id}/approve` — Approve profile
- `POST /admin/profiles/{id}/flag` — Flag/hide profile
- `GET /admin/transactions` — Transaction log
- `GET /admin/stats` — Platform analytics

### Stripe (1):
- `POST /webhook/stripe` — Payment completion webhook

### Config (1):
- `GET /config/stripe` — Public Stripe key for frontend

---

## DATABASE MODELS (5)

1. **User** — id, email, phone, display_name, user_type (giver/receiver/both/admin), password_hash, is_verified, created_at
2. **Profile** — id, user_id (FK), city, state, story, is_public, is_verified, is_flagged, created_at
3. **Address** — id, user_id (FK), encrypted_street, encrypted_zip, city, state (sensitive fields AES encrypted)
4. **Transaction** — id, giver_id, receiver_id, amount, tip_amount, delivery_method, gift_card_code, status, stripe_payment_intent_id, message, created_at
5. **Connection** — id, giver_id, receiver_id, relationship_type, is_confirmed (DEFINED BUT UNUSED)

---

## KNOWN GAPS & STATUS

| # | Issue | Status | Priority |
|---|-------|--------|----------|
| 1 | Stripe success/cancel pages missing | **FIXED S1** | ~~HIGH~~ |
| 2 | Demo flow doesn't complete without Stripe | **FIXED S1** | ~~HIGH~~ |
| 3 | Email/SMS verification is fake (any 6 digits) | DEFERRED | Medium |
| 4 | Gift card code fulfillment not implemented | DEFERRED | Medium |
| 5 | Connection model unused | DEFERRED | Low |
| 6 | API base URL hardcoded to localhost | **FIXED S1** | ~~Medium~~ |
| 7 | CORS wildcard (*) too permissive | DEFERRED | Medium |
| 8 | No rate limiting | DEFERRED | Medium |
| 9 | No server-side HTML sanitization | DEFERRED | Low |
| 10 | Silent error swallowing in admin | **TODO** | Low |
| 11 | Frontend served from FastAPI (static mount) | **DONE S1** | — |

---

## PHASE ROADMAP

### Phase 1: Make It Run End-to-End ← COMPLETED (Session 1)
- ~~Stripe success/cancel handlers~~ DONE
- ~~Demo mode transaction completion~~ DONE
- ~~Test all 3 user journeys (donor, recipient, admin)~~ DONE
- ~~Frontend served from FastAPI static mount~~ DONE
- ~~API base URL made same-origin aware~~ DONE

### Phase 2: Harden Auth & Security
- Lock CORS, add rate limiting, sanitize inputs, configure API URL

### Phase 3: Real Verification & Notifications
- Email service integration, real verification codes, notification emails

### Phase 4: Gift Card Fulfillment
- DoorDash/Uber Eats/Instacart API integration, delivery tracking

### Phase 5: Polish & Scale
- Connections, recurring donations, social sharing, image uploads, PostgreSQL, deploy

---

## HANDOFF TEMPLATE (for scripts/handoff.md)

```markdown
# Session Handoff — [DATE]

## What Was Done
- [bullet points of completed work]

## What Was NOT Finished
- [bullet points of incomplete work with context]

## What We Discussed / Decided
- [any decisions, architecture choices, or user preferences noted]

## Known Bugs Found
- [any bugs discovered during this session]

## Next Session Should Start With
- [specific first steps for the next agent]

## Files Changed This Session
- [list of files modified/created with brief description]
```
