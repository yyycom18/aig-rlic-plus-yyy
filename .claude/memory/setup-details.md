# Setup Details

## MCP Servers (9 total, budget max 10)

| # | Server | Package / Endpoint | Transport | API Key? |
|---|--------|--------------------|-----------|----------|
| 1 | financial-datasets | mcp-remote → financialdatasets.ai/mcp | Remote | No (OAuth) |
| 2 | yahoo-finance | @modelcontextprotocol/server-yahoo-finance | npx | No |
| 3 | filesystem | @modelcontextprotocol/server-filesystem | npx | No |
| 4 | alpha-vantage | mcp.alphavantage.co/mcp?apikey=KEY | HTTP | ALPHAVANTAGE_API_KEY |
| 5 | fred | fred-mcp-server | npx | FRED_API_KEY |
| 6 | context7 | @upstash/context7-mcp@latest | npx | No |
| 7 | sequential-thinking | @modelcontextprotocol/server-sequential-thinking | npx | No |
| 8 | memory | @modelcontextprotocol/server-memory | npx | No |
| 9 | fetch | @modelcontextprotocol/server-fetch | npx | No |

### Lessons learned (2026-02-28 audit)
- `@financial-datasets/mcp-server` does NOT exist on npm — it's a remote endpoint
- `yahoo-finance-mcp` does NOT exist — use `@modelcontextprotocol/server-yahoo-finance`
- `@anthropic/mcp-filesystem` does NOT exist — correct is `@modelcontextprotocol/server-filesystem`
- `@anthropic/mcp-remote` does NOT exist — Alpha Vantage uses HTTP transport directly
- Always use `npx -y` (not bare `npx`) to avoid interactive prompts in CI

## API Keys
- ALPHAVANTAGE_API_KEY — set as Codespaces secret, passed in URL for HTTP transport
- FRED_API_KEY — set as Codespaces secret, passed as env var
- Both flow: Codespaces secret → remoteEnv in devcontainer.json → env var → setup.sh
- setup.sh prompts interactively if keys not found and terminal is interactive

## Python Stack
numpy, pandas, scipy, statsmodels, scikit-learn, arch, linearmodels,
matplotlib, seaborn, plotly, yfinance, fredapi, jupyterlab, ipykernel,
openpyxl, xlsxwriter, requests, beautifulsoup4, lxml, tabulate, rich

## Agent Teams
- Enabled via `~/.claude/settings.json` → `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"`
- Recommended team patterns:
  - Data agent — pulls, cleans, validates
  - Econometrics agent — specifies, estimates models
  - Visualization agent — charts and tables
  - Research agent — papers, reports, context

## Devcontainer
- Image: Python 3.14 + Debian Trixie
- Features: github-cli, node (lts), claude-code
- Bind mounts: ~/.claude/ and ~/.claude.json from host
- initializeCommand: Python-based (cross-platform) to ensure mount sources exist
- postCreateCommand: bash setup.sh

## setup.sh Design
- `set -uo pipefail` (not -e) — MCP failures isolated via add_mcp() wrapper
- add_mcp() removes then re-adds for idempotency
- Node.js fallback: check PATH → nvm → fresh nvm install
- MCP failure counter reported at end
- Verification checks: Node.js, Python packages, MCP server list, server count budget

## Session History
- 2026-02-28: Initial setup. Independent audit found 6 FAILs (wrong npm names, missing -y, Windows compat). All fixed.
