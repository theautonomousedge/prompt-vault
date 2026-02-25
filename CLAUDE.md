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

## AGENT BEHAVIORAL RULES

### You CAN do autonomously:
- Read any file, search codebase, run `git log`/`git status`
- Edit code in `backend/` and `frontend/` to implement roadmap tasks
- Run the server, run tests, seed the database
- Make small atomic commits during your session
- Fix bugs you discover while working

### You MUST ask the user before:
- Adding new dependencies to `requirements.txt`
- Creating new files outside the existing structure
- Changing the file/folder layout
- Making architectural decisions not in the blueprints
- Pushing to remote (do it at end-of-session per protocol, but confirm if unsure)
- Deleting any file

### Deviation Protocol:
If you want to change something architectural that contradicts `blueprints/architecture.md`:
1. **STOP** — do not implement it
2. Describe what you want to change and why
3. Wait for explicit approval
4. If approved: update the blueprint FIRST, then implement

### When in doubt, ask. Don't guess.

### NEXT 3 STEPS (from `blueprints/roadmap.md`):
> Agents: Update this section when you complete steps. Always show the next 3.

1. **Lock CORS** — Replace `allow_origins=["*"]` with specific origins in `main.py`
2. **Add rate limiting** — Install `slowapi`, add limits to auth and transaction routes
3. **Server-side sanitization** — Sanitize story/message fields before storing

*(These are from Phase 2: Harden Auth & Security. See `blueprints/roadmap.md` for full list.)*

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

## QUICK START

```bash
pip install -r requirements.txt          # Install deps
cd backend && python seed.py             # Seed test data
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000  # Run server
```

**Test accounts** (from seed): Admin: `admin@promptvault.org` / `admin1234` | Donor: `donor@test.com` / `donor1234` | Recipients: `maria@test.com` etc. / `password123`

**Verify it works**: `curl http://localhost:8000/health` → `{"status":"ok"}`

---

## FILE STRUCTURE (Last Updated: 2026-02-25, Session 2 End)

```
prompt-vault/
├── CLAUDE.md                    # THIS FILE — project rules & state (READ FIRST)
├── brainstorm.md                # User ideas & musings (append-only)
├── .env.example                 # Environment variable template (8 vars)
├── .gitignore                   # Git ignore rules
├── README.md                    # Project overview & setup instructions
├── requirements.txt             # Python dependencies (10 packages, pinned)
│
├── blueprints/                  # Architecture & planning (SINGLE SOURCE OF TRUTH)
│   ├── architecture.md          # System design, how pieces connect, data flows
│   ├── roadmap.md               # Phase-by-phase task list (agents follow this)
│   └── data-model.md            # DB schema, relationships, enums, encryption
│
├── docs/                        # Reference material (read on demand)
│   ├── api-reference.md         # All 22 API routes + DB models + Pydantic schemas
│   └── decisions.md             # Architecture decisions log (append-only)
│
├── reports/                     # For the USER (progress tracking)
│   └── task-logs.md             # Chronological task history across sessions
│
├── agents/                      # Agent role definitions
│   └── README.md                # What each agent type should do
│
├── skills/                      # Available tools & patterns reference
│   └── README.md                # Commands, test creds, codebase patterns
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

**Total: ~4,037 lines across 21 source files + ~1,200 lines in docs/blueprints/reports**

---

## SESSION PROTOCOL — MANDATORY FOR EVERY AGENT

### At Session START:
1. Read this CLAUDE.md completely (especially FAILSAFE RULES and NEXT 3 STEPS)
2. Read `scripts/handoff.md` for previous session context
3. Read `brainstorm.md` for any user ideas to be aware of
4. Check `git log --oneline -10` to see recent work
5. Confirm you're on branch `claude/food-gifting-mvp-FFgJW`
6. Tell the user: "Here's where we are and the next 3 steps: [list them]"

### During Session:
1. Use TodoWrite to track all tasks
2. Make small, atomic commits with clear messages
3. Log any non-trivial decisions in `docs/decisions.md`
4. If user says "brainstorm [idea]" → append to `brainstorm.md`
5. Follow `blueprints/roadmap.md` — don't freelance
6. Reference `docs/api-reference.md` when touching routes/models
7. Reference `skills/README.md` for commands and patterns

### At Session END (BEFORE final push — DO NOT SKIP):
1. **Update CLAUDE.md** — refresh file structure line counts, update NEXT 3 STEPS
2. **Update `scripts/handoff.md`** — append full handoff report (see template)
3. **Update `reports/task-logs.md`** — append session's completed tasks
4. **Update `brainstorm.md`** — if any new ideas were discussed
5. **Update `blueprints/roadmap.md`** — mark completed tasks, add new ones if approved
6. **Commit all docs** with message: `chore: end-of-session update — CLAUDE.md + handoff`
7. **Verify**: `wc -l CLAUDE.md scripts/handoff.md` (both must be >20 lines)
8. **Push** to `claude/food-gifting-mvp-FFgJW`

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

## API & DATA REFERENCE

> Full details moved to external files to keep this file scannable.

- **22 API routes** (Auth 3, Profiles 4, Transactions 2, Dashboard 1, Admin 5, Stripe 1, Config 1) → See `docs/api-reference.md`
- **5 database models** (User, Profile, Address, Transaction, Connection) → See `docs/api-reference.md`
- **Pydantic schemas** (7 request + 6 response) → See `docs/api-reference.md`
- **Architecture & data flows** → See `blueprints/architecture.md`
- **DB relationships & enums** → See `blueprints/data-model.md`
- **All decisions with rationale** → See `docs/decisions.md`

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
# Session [N] — [DATE]

## What Was Done
- [bullet points of completed work]

## What Was NOT Finished
- [bullet points of incomplete work with context]

## What We Discussed / Decided
- [any decisions, architecture choices, or user preferences noted]
- [log these in docs/decisions.md too]

## Known Bugs Found
- [any bugs discovered during this session]

## Brainstorm Items Captured
- [any ideas the user mentioned — also in brainstorm.md]

## Test Credentials
- Admin: admin@promptvault.org / admin1234
- Donor: donor@test.com / donor1234
- Recipients: maria@test.com, etc. / password123

## Next Session Should Start With
- [specific first steps for the next agent]

## Files Changed This Session
- [list of files modified/created with brief description]
```

---

## KEY REFERENCES (quick links for agents)

| What | Where |
|------|-------|
| System architecture | `blueprints/architecture.md` |
| Phase roadmap | `blueprints/roadmap.md` |
| Data model & enums | `blueprints/data-model.md` |
| API routes (all 22) | `docs/api-reference.md` |
| Architecture decisions | `docs/decisions.md` |
| Agent role guide | `agents/README.md` |
| Commands & patterns | `skills/README.md` |
| User ideas | `brainstorm.md` |
| Task history (for user) | `reports/task-logs.md` |
| Agent handoff log | `scripts/handoff.md` |
