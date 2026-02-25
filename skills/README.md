# Available Skills & Tools — Prompt Vault

> Reference this file to know what tools and capabilities are available.
> Don't reinvent the wheel — use what's here.

---

## Built-in Tools (Always Available)

| Tool | Use For | Notes |
|------|---------|-------|
| **Read** | Read any file | Use instead of `cat`, `head`, `tail` |
| **Edit** | Modify files | Use instead of `sed`, `awk`. Requires reading file first |
| **Write** | Create new files | Only for NEW files. Use Edit for existing |
| **Glob** | Find files by pattern | Use instead of `find` or `ls` |
| **Grep** | Search file contents | Use instead of `grep` or `rg` |
| **Bash** | Run commands | For git, pip, uvicorn, tests only |
| **TodoWrite** | Track tasks | Use for multi-step work |
| **Task** | Launch sub-agents | For parallel research or complex tasks |
| **WebSearch** | Search the web | For docs, APIs, error solutions |
| **WebFetch** | Fetch URL content | For reading web pages |

## Project-Specific Commands

| Command | What It Does | When To Use |
|---------|-------------|-------------|
| `cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000` | Start server | Testing changes |
| `cd backend && python seed.py` | Seed test data | Fresh database setup |
| `cd backend && python -c "from main import app; print('OK')"` | Verify imports | After changing backend code |
| `wc -l CLAUDE.md scripts/handoff.md` | Check file integrity | Before pushing (failsafe rule 10) |
| `git push -u origin claude/food-gifting-mvp-FFgJW` | Push changes | End of session only |

## Test Credentials (from seed.py)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@promptvault.org | admin1234 |
| Donor | donor@test.com | donor1234 |
| Recipient | maria@test.com | password123 |
| Recipient | james@test.com | password123 |
| Recipient | aisha@test.com | password123 |
| Recipient | carlos@test.com | password123 |
| Recipient | sarah@test.com | password123 |

## Key Patterns in This Codebase

### Adding a new API route
1. Add Pydantic schema to `schemas.py`
2. Add route to `main.py` (BEFORE the static mount at the bottom)
3. Update `docs/api-reference.md`
4. Add frontend API method to `api.js`
5. Update CLAUDE.md file structure if line counts changed significantly

### Adding a new frontend page
1. Create `frontend/newpage.html` with `data-page="newpage"` on body
2. Add page handler in `app.js`: `pages.newpage = async () => { ... }`
3. Include all 3 script tags (api.js, auth.js, app.js)
4. Add nav link if needed
5. Update CLAUDE.md file structure
