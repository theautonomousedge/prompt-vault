# Architecture Decisions Log — Prompt Vault

> Every non-trivial decision gets logged here with rationale and date.
> Agents MUST append here when making architectural choices. Never delete entries.

---

## Decision Format
```
### D-[number]: [Short title]
- **Date**: YYYY-MM-DD | **Session**: N
- **Decision**: What was decided
- **Rationale**: Why
- **Impact**: What it affects
- **Alternatives considered**: What was rejected and why
```

---

## Decisions

### D-001: Monolith backend (all routes in main.py)
- **Date**: 2026-02-25 | **Session**: 1
- **Decision**: Keep all 22 API routes in `backend/main.py` as a single file
- **Rationale**: MVP simplicity. 510 lines is manageable. Splitting into routers adds complexity without value at this scale
- **Impact**: All API changes happen in one file. Easy to find things, easy to break things
- **Alternatives considered**: FastAPI routers in separate files — rejected for MVP, revisit at Phase 5

### D-002: Vanilla HTML/CSS/JS frontend (no frameworks)
- **Date**: 2026-02-25 | **Session**: 1
- **Decision**: No React, no Vue, no build tools, no npm. Plain HTML pages with shared JS files
- **Rationale**: Fastest path to working UI. No build step = no build failures. Each page is self-contained
- **Impact**: No component reuse, some HTML duplication across pages. Acceptable for 9 pages
- **Alternatives considered**: React/Vue — rejected. HTMX — considered but adds dependency

### D-003: Frontend served from FastAPI (static mount)
- **Date**: 2026-02-25 | **Session**: 1
- **Decision**: Mount `frontend/` directory as static files in FastAPI at root `/`
- **Rationale**: Single server on port 8000. No CORS issues in dev. Stripe redirect URLs work naturally
- **Impact**: API routes MUST be defined before the static mount (catch-all). Frontend is at same origin as API
- **Alternatives considered**: Separate static server on port 3000 — rejected, creates CORS issues

### D-004: API_BASE same-origin aware
- **Date**: 2026-02-25 | **Session**: 1
- **Decision**: `api.js` uses `window.API_BASE || ''` instead of hardcoded `http://localhost:8000`
- **Rationale**: When frontend is served from FastAPI, same-origin requests don't need a base URL
- **Impact**: Works in both dev (same origin) and could be overridden for separate hosting
- **Alternatives considered**: Keep hardcoded — rejected, breaks when deployed

### D-005: FRONTEND_URL config for Stripe redirects
- **Date**: 2026-02-25 | **Session**: 1
- **Decision**: Stripe success/cancel URLs use `FRONTEND_URL` env var (default: `http://localhost:8000`)
- **Rationale**: Stripe needs absolute URLs for redirects. Must be configurable for deployment
- **Impact**: `.env.example` now has 8 vars. `payments.py` reads from config
- **Alternatives considered**: Hardcode localhost — rejected, breaks in production

### D-006: Demo mode auto-completes transactions
- **Date**: 2026-02-25 | **Session**: 1
- **Decision**: When Stripe keys aren't configured, transactions auto-mark as `completed` and return empty `session_url`
- **Rationale**: Lets the full flow work without Stripe keys during development
- **Impact**: Frontend checks `if (result.session_url)` — empty string = demo mode, shows inline confirmation
- **Alternatives considered**: Error out without Stripe — rejected, blocks all development

### D-007: Comprehensive CLAUDE.md + handoff system
- **Date**: 2026-02-25 | **Session**: 1-2
- **Decision**: CLAUDE.md is the single source of truth. Handoff.md is append-only. Both updated every session end
- **Rationale**: User loses massive time when agents don't communicate between sessions
- **Impact**: 10 failsafe rules protect these files. End-of-session protocol is mandatory
- **Alternatives considered**: Just README — rejected, agents don't read READMEs consistently
