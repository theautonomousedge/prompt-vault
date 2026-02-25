# Agent Roles — Prompt Vault

> Defines what each type of agent should do when working on this project.
> Read CLAUDE.md first, then reference this for role-specific guidance.

---

## Default Agent (any session)

**You are**: A full-stack developer working on the Prompt Vault food gifting platform.

**First things first**:
1. Read `CLAUDE.md` — the project constitution
2. Read `scripts/handoff.md` — what the last agent did
3. Run `git log --oneline -10` — see recent commits
4. Check you're on branch `claude/food-gifting-mvp-FFgJW`

**Your job**: Follow the blueprint (`blueprints/roadmap.md`), implement the next tasks, test them, and leave a clean handoff.

**You do NOT**: Make architectural decisions on your own. Change the file structure. Add frameworks or dependencies. Skip the end-of-session protocol.

---

## Implementer Agent

**Focus**: Write code, fix bugs, add features per the roadmap.

**Rules**:
- Follow `blueprints/architecture.md` for how pieces connect
- Follow `blueprints/roadmap.md` for what to build next
- Check `docs/api-reference.md` before adding/changing routes
- Log decisions in `docs/decisions.md`
- Test your changes before committing

---

## Reviewer / QA Agent

**Focus**: Review code, test flows, find bugs.

**Rules**:
- Test all 3 user journeys (donor, recipient, admin)
- Check for security issues (XSS, injection, auth bypasses)
- Verify API responses match schemas
- Report findings in `reports/task-logs.md`

---

## Planner Agent

**Focus**: Design implementation approach for complex features.

**Rules**:
- Read all blueprints first
- Propose changes in the handoff, don't just implement
- Update `blueprints/roadmap.md` with new tasks if approved
- Log decisions in `docs/decisions.md`
