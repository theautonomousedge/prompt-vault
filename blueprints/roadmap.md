# Phase Roadmap — Prompt Vault

> The step-by-step plan. Agents follow this, they don't rewrite it.
> Mark tasks done as you complete them. Add tasks only if explicitly approved.

---

## Phase 1: Make It Run End-to-End — COMPLETED (Session 1)

- [x] Stripe success/cancel page handlers (success.html, cancel.html)
- [x] Demo mode transaction completion (auto-complete without Stripe)
- [x] Frontend served from FastAPI static mount
- [x] API base URL made same-origin aware (api.js)
- [x] FRONTEND_URL config for Stripe redirects (payments.py)
- [x] Test donor journey: register → browse → donate → dashboard
- [x] Test recipient journey: register → create profile → appears in browse
- [x] Test admin journey: login → pending profiles → approve/flag → transactions

## Phase 2: Harden Auth & Security — NEXT UP

- [ ] Lock CORS to specific origins (replace `*` wildcard)
- [ ] Add rate limiting on auth routes (registration, login)
- [ ] Add rate limiting on transaction creation
- [ ] Server-side HTML sanitization on story and message fields
- [ ] Input length validation enforcement (backend already has schema limits)
- [ ] Review and test error handling (fix silent swallowing in admin)
- [ ] Add request logging for debugging

## Phase 3: Real Verification & Notifications

- [ ] Choose email service (SendGrid, SES, or Resend)
- [ ] Real 6-digit verification code generation
- [ ] Send verification email on registration
- [ ] Validate code against stored code (not "any 6 digits")
- [ ] "Someone sent you a meal!" notification email to recipient
- [ ] Donation receipt email to donor
- [ ] Optional: SMS via Twilio

## Phase 4: Gift Card Fulfillment

- [ ] Research DoorDash/Uber Eats/Instacart gift card APIs
- [ ] Build fulfillment service (purchase gift card post-payment)
- [ ] Store encrypted gift card codes in Transaction.gift_card_code
- [ ] Delivery tracking status updates
- [ ] Fallback handling (service unavailable → queue for retry)

## Phase 5: Polish & Scale

- [ ] Activate Connection model (private gifting between linked users)
- [ ] Recurring donation plans (weekly/monthly auto-send)
- [ ] Social sharing (share-your-impact cards)
- [ ] Profile image uploads
- [ ] PostgreSQL migration
- [ ] Deploy: backend on Railway/Fly.io, frontend stays served from FastAPI
- [ ] Accessibility audit (ARIA, keyboard nav, screen readers)
- [ ] Consider splitting main.py into routers (if >800 lines)
