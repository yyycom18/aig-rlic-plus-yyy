# Lessons Learned & Repeatable SOPs

## Session: 2026-02-28 — Environment Bootstrap

---

## Lesson 1: Never trust LLM-generated npm package names

**What happened:** I confidently produced 4 MCP server install commands with wrong package names:
- `@financial-datasets/mcp-server` → doesn't exist (it's a remote endpoint)
- `yahoo-finance-mcp` → doesn't exist
- `@anthropic/mcp-filesystem` → doesn't exist (correct: `@modelcontextprotocol/server-filesystem`)
- `@anthropic/mcp-remote` → doesn't exist

**SOP:** Always verify npm package names against the actual registry or official docs before writing install commands. Use a subagent to cross-check if needed.

---

## Lesson 2: Independent review catches what the builder misses

**What happened:** I built the entire setup across 4 files, audited it myself, and found 6 issues. Then a fresh subagent found 6 FAILs and 11 WARNs — including the 4 wrong package names I never questioned.

**SOP:** Before shipping infrastructure code, spawn an independent review agent with explicit audit criteria. The builder is blind to their own assumptions. This is non-negotiable for setup scripts, CI/CD, and anything that runs unattended.

---

## Lesson 3: `set -e` is dangerous with external service calls

**What happened:** `set -euo pipefail` combined with 9 `claude mcp add` commands meant the first failure would abort the entire script. No MCP servers after the failure point would be configured.

**SOP:** Use `set -uo pipefail` (without `-e`) and wrap external calls in error-isolating helper functions:
```bash
add_mcp() {
  local name="$1"; shift
  claude mcp remove "$name" 2>/dev/null || true
  if claude mcp add "$name" "$@" 2>&1; then
    echo "  OK  $name"
  else
    echo "  FAIL $name"
    FAILURES=$((FAILURES + 1))
  fi
}
```

---

## Lesson 4: Always use `npx -y` in non-interactive contexts

**What happened:** Tier 1 MCP commands used bare `npx` without `-y`. In `postCreateCommand` (non-interactive), npx prompts for install confirmation and hangs.

**SOP:** Every `npx` in a setup script must use `-y` to auto-confirm package installation.

---

## Lesson 5: Devcontainer `initializeCommand` runs on the HOST

**What happened:** Used `mkdir -p` and `touch` — bash commands that fail on native Windows. The `initializeCommand` runs on the host OS, not in the container.

**SOP:** Use cross-platform tools in `initializeCommand`. Python's `pathlib` works everywhere:
```json
"initializeCommand": "python3 -c \"import pathlib; h=pathlib.Path.home(); (h/'.claude').mkdir(exist_ok=True); (h/'.claude.json').touch(exist_ok=True)\""
```

---

## Lesson 6: nvm installed ≠ Node.js installed

**What happened:** The devcontainer had nvm but no Node.js version. `npx` wasn't on PATH. All MCP servers failed silently.

**SOP:** Always check `command -v node` before assuming Node.js is available. The setup.sh fallback chain should be: check PATH → source nvm and install LTS → install nvm from scratch.

---

## Lesson 7: Setup scripts must be idempotent

**What happened:** Running `setup.sh` twice would duplicate MCP server entries because `claude mcp add` doesn't check for existing entries.

**SOP:** Remove before adding: `claude mcp remove "$name" 2>/dev/null || true` before every `claude mcp add`.

---

## Lesson 8: Three-layer Claude config inheritance

**Architecture:**
| Layer | Location | Persistence | Scope |
|-------|----------|-------------|-------|
| User | `~/.claude/`, `~/.claude.json` | Bind mount from host | All projects |
| Project (shared) | `<repo>/.claude/settings.json`, `CLAUDE.md` | Git (committed) | All collaborators |
| Project (local) | `<repo>/.claude/settings.local.json` | Workspace (gitignored) | This machine only |

**SOP:** Shared permissions go in `.claude/settings.json` (committed). Personal overrides in `.claude/settings.local.json` (gitignored). User-level config persists via host bind mount.

---

## Lesson 9: MCP server transports vary — not everything is npx

**Types encountered:**
| Transport | Example | When to use |
|-----------|---------|-------------|
| npx (stdio) | `npx -y @modelcontextprotocol/server-filesystem` | npm packages with CLI entry |
| Remote (mcp-remote) | `npx -y mcp-remote https://endpoint/mcp` | Hosted services without npm package |
| HTTP | `claude mcp add -t http name URL` | Services with native HTTP MCP support |

**SOP:** Check how the service is hosted before writing the install command. Not every MCP server is an npm package.

---

## Lesson 10: Devcontainer rebuild vs restart

- **Restart** (`Ctrl+Shift+P → Reopen in Container`): keeps installed packages, just restarts the container process
- **Rebuild** (`Ctrl+Shift+P → Rebuild Container`): destroys and recreates the container. Only git-tracked files and host bind mounts survive.

**SOP:** Everything that must survive a rebuild should be either:
1. Committed to the repo (setup.sh, requirements.txt, CLAUDE.md)
2. Bind-mounted from the host (~/.claude/, ~/.claude.json)
3. Recreated by postCreateCommand (pip packages, MCP configs)

---

## Lesson 11: Context budget for MCP servers

More MCP servers = more tools = more context consumed per request. Past ~80 tools, effective context window shrinks from 200K toward 70K.

**SOP:** Keep MCP server count ≤ 10. Document the budget in CLAUDE.md. Add a count check to setup.sh verification step.

---

## Lesson 12: Avoid `postCreateCommand` duplication

**What happened:** `postCreateCommand` ran `pip install -r requirements.txt && bash setup.sh`, but setup.sh already runs `pip install -r requirements.txt`. Double work on every container build.

**SOP:** `postCreateCommand` should be a single entry point (`bash setup.sh`). Let the setup script handle everything internally.

---

## Repeatable SOP: Setting Up a New Quant Workstation

1. Clone repo (CLAUDE.md, setup.sh, requirements.txt, devcontainer.json already there)
2. Set Codespaces secrets: ALPHAVANTAGE_API_KEY, FRED_API_KEY
3. Open in VS Code → "Reopen in Container"
4. postCreateCommand runs setup.sh automatically
5. Restart Claude Code session to activate MCP servers
6. Verify: `claude mcp list` shows 9 servers, Python imports all pass
7. Start working — Alex persona loads from CLAUDE.md
