#!/usr/bin/env bash
# ============================================================================
# AIG-RLIC+ Environment Setup
# Quantitative & Qualitative Economic/Financial Analysis Toolkit
#
# Expected MCP server count: 8 (budget max: 10)
# ============================================================================
set -uo pipefail

WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_FAILURES=0

echo "=========================================="
echo " AIG-RLIC+ Environment Setup"
echo "=========================================="

# --------------------------------------------------------------------------
# Helper: add MCP server with error isolation & idempotency
# --------------------------------------------------------------------------
add_mcp() {
  local name="$1"; shift
  # Remove existing entry to ensure idempotency
  claude mcp remove "$name" 2>/dev/null || true
  if claude mcp add "$name" "$@" 2>&1; then
    echo "  OK  $name"
  else
    echo "  FAIL $name — see error above"
    MCP_FAILURES=$((MCP_FAILURES + 1))
  fi
}

# --------------------------------------------------------------------------
# 1. Prerequisites — ensure Node.js is available for MCP servers
# --------------------------------------------------------------------------
echo ""
echo "[1/5] Checking Node.js..."

if command -v node &>/dev/null; then
  echo "  -> Node.js $(node --version) found."
else
  echo "  -> Node.js not found. Installing via nvm..."
  export NVM_DIR="${NVM_DIR:-/usr/local/share/nvm}"
  if [ -s "$NVM_DIR/nvm.sh" ]; then
    . "$NVM_DIR/nvm.sh"
    nvm install --lts
    echo "  -> Node.js $(node --version) installed via nvm."
  else
    echo "  -> nvm not found. Installing nvm + Node.js LTS..."
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    . "$NVM_DIR/nvm.sh"
    nvm install --lts
    echo "  -> Node.js $(node --version) installed via fresh nvm."
  fi
fi

# --------------------------------------------------------------------------
# 2. Python packages
# --------------------------------------------------------------------------
echo ""
echo "[2/5] Installing Python packages..."

if [ -f "$WORKSPACE_DIR/requirements.txt" ]; then
  pip install --quiet -r "$WORKSPACE_DIR/requirements.txt"
else
  pip install --quiet \
    numpy pandas scipy statsmodels scikit-learn \
    matplotlib seaborn plotly \
    yfinance fredapi \
    arch linearmodels \
    jupyterlab ipykernel \
    openpyxl xlsxwriter \
    requests beautifulsoup4 lxml \
    tabulate rich
fi

echo "  -> Python packages installed."

# --------------------------------------------------------------------------
# 3. MCP Servers (8 total — budget max 10)
# --------------------------------------------------------------------------
echo ""
echo "[3/5] Configuring MCP servers..."

# Tier 1 — No API keys required
add_mcp financial-datasets -- npx -y mcp-remote https://mcp.financialdatasets.ai/mcp
add_mcp yahoo-finance -- npx -y yahoo-finance-mcp-server
add_mcp filesystem -- npx -y @modelcontextprotocol/server-filesystem "$WORKSPACE_DIR"

# Tier 2 — Require API keys (env → interactive prompt → skip)
ALPHAVANTAGE_API_KEY="${ALPHAVANTAGE_API_KEY:-}"
FRED_API_KEY="${FRED_API_KEY:-}"

# Prompt for missing keys if running interactively
if [ -t 0 ]; then
  if [ -z "$ALPHAVANTAGE_API_KEY" ]; then
    echo ""
    echo "  Alpha Vantage API key not found in environment."
    echo "  Get a free key at: https://www.alphavantage.co/support/#api-key"
    read -rp "  Enter Alpha Vantage API key (or press Enter to skip): " ALPHAVANTAGE_API_KEY
  fi
  if [ -z "$FRED_API_KEY" ]; then
    echo ""
    echo "  FRED API key not found in environment."
    echo "  Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html"
    read -rp "  Enter FRED API key (or press Enter to skip): " FRED_API_KEY
  fi
fi

if [ -n "$ALPHAVANTAGE_API_KEY" ]; then
  claude mcp remove alpha-vantage 2>/dev/null || true
  if claude mcp add -t http alpha-vantage "https://mcp.alphavantage.co/mcp?apikey=${ALPHAVANTAGE_API_KEY}" 2>&1; then
    echo "  OK  alpha-vantage"
  else
    echo "  FAIL alpha-vantage"
    MCP_FAILURES=$((MCP_FAILURES + 1))
  fi
else
  echo "  SKIP alpha-vantage (no API key)"
fi

if [ -n "$FRED_API_KEY" ]; then
  add_mcp fred -e FRED_API_KEY="$FRED_API_KEY" -- npx -y @iflow-mcp/fred-mcp-server
else
  echo "  SKIP fred (no API key)"
fi

# Persist API keys to ~/.bashrc so Python scripts (fredapi, etc.) can access them
# via os.environ, not just MCP server processes.
BASHRC="$HOME/.bashrc"
for KEY_NAME in FRED_API_KEY ALPHAVANTAGE_API_KEY; do
  KEY_VAL="${!KEY_NAME:-}"
  if [ -n "$KEY_VAL" ]; then
    # Remove any existing entry, then append
    sed -i "/^export ${KEY_NAME}=/d" "$BASHRC" 2>/dev/null || true
    echo "export ${KEY_NAME}=\"${KEY_VAL}\"" >> "$BASHRC"
  fi
done

# Tier 3 — Reasoning, docs, persistence
# Note: fetch MCP server removed — Claude Code's built-in WebFetch covers the same
# functionality without consuming an MCP slot.
add_mcp context7 -- npx -y @upstash/context7-mcp@latest
add_mcp sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
add_mcp memory -- npx -y @modelcontextprotocol/server-memory

echo ""
if [ "$MCP_FAILURES" -gt 0 ]; then
  echo "  -> MCP servers configured with $MCP_FAILURES failure(s)."
else
  echo "  -> All MCP servers configured."
fi

# --------------------------------------------------------------------------
# 4. Agent Teams
# --------------------------------------------------------------------------
echo ""
echo "[4/5] Enabling agent teams..."

SETTINGS_FILE="$HOME/.claude/settings.json"
mkdir -p "$(dirname "$SETTINGS_FILE")"

if [ -f "$SETTINGS_FILE" ]; then
  # Merge the env key into existing settings using Python
  python3 -c "
import json
with open('$SETTINGS_FILE') as f:
    data = json.load(f)
data.setdefault('env', {})['CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS'] = '1'
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
else
  echo '{"env":{"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS":"1"}}' | python3 -m json.tool > "$SETTINGS_FILE"
fi

echo "  -> Agent teams enabled."

# --------------------------------------------------------------------------
# 5. Verification
# --------------------------------------------------------------------------
echo ""
echo "[5/5] Verifying installation..."

echo ""
echo "  Node.js:"
if command -v node &>/dev/null; then
  echo "  OK  node $(node --version)"
  echo "  OK  npx  $(npx --version)"
else
  echo "  FAIL node not found"
fi

echo ""
echo "  Python packages:"
python3 -c "
packages = [
    ('numpy',        'numpy'),
    ('pandas',       'pandas'),
    ('scipy',        'scipy'),
    ('statsmodels',  'statsmodels'),
    ('scikit-learn', 'sklearn'),
    ('arch',         'arch'),
    ('linearmodels', 'linearmodels'),
    ('matplotlib',   'matplotlib'),
    ('seaborn',      'seaborn'),
    ('plotly',       'plotly'),
    ('yfinance',     'yfinance'),
    ('fredapi',      'fredapi'),
]
ok, fail = 0, 0
for name, mod in packages:
    try:
        m = __import__(mod)
        ver = getattr(m, '__version__', '?')
        print(f'  OK  {name:20s} {ver}')
        ok += 1
    except ImportError as e:
        print(f'  FAIL {name:20s} {e}')
        fail += 1
print(f'\n  {ok} passed, {fail} failed')
"

echo ""
echo "  MCP servers:"
claude mcp list 2>&1 || echo "  (could not list — see error above)"

# Check server count against budget
SERVER_COUNT=$(claude mcp list 2>/dev/null | grep -c "^" || echo "0")
if [ "$SERVER_COUNT" -gt 10 ]; then
  echo "  WARN: $SERVER_COUNT MCP servers exceeds budget of 10"
fi

# --------------------------------------------------------------------------
# Done
# --------------------------------------------------------------------------
echo ""
echo "=========================================="
echo " Setup complete."
echo " Restart Claude Code to activate MCP servers."
echo "=========================================="
