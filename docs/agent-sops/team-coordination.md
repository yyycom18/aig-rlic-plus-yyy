# Team Coordination Protocol

## Overview

This document defines how agents on the AIG-RLIC+ team coordinate work, hand off outputs, and resolve issues. All agents should read this document at session start alongside their individual SOP.

## Team Structure

```
                       Alex (Lead Analyst)
                    ┌────────┼────────┐
                    │        │        │
              ┌─────┴──┐  ┌─┴───┐  ┌─┴──────────┐
              │Research │  │Data │  │Econometrics │
              │  Ray    │  │Dana │  │   Evan      │
              └────┬────┘  └──┬──┘  └──────┬──────┘
                   │          │            │
                   │          └─────┬──────┘
                   │          ┌─────┴──────┐
                   │          │Visualization│
                   │          │    Vera     │
                   │          └──────┬──────┘
                   │                 │
                   └────────┬────────┘
                       ┌────┴─────┐
                       │ App Dev  │
                       │   Ace    │
                       └──────────┘
```

**Alex** (lead) assigns tasks, reviews outputs, and makes final decisions on methodology and interpretation.
**Ace** (app dev) is the integration point — assembles all outputs into the Streamlit portal.

## Standard Task Flow

A typical analysis follows this sequence:

```
1. Alex frames the question and creates tasks
2. Research agent gathers literature and context    ──┐
3. Data agent sources and cleans datasets            ──┤ (parallel)
4. Econometrics agent specifies and estimates models  ←┘ (after 2 & 3)
5. Visualization agent produces charts and tables     ← (after 4)
6. App dev assembles portal with narrative + visuals  ← (after 5, with input from 2 & 3)
7. Alex reviews, interprets, and delivers final output
```

Steps 2 and 3 run in parallel. Steps 4, 5, and 6 are sequential dependencies.
Ace can begin scaffolding the portal structure during steps 2-4 while waiting for final outputs.

## Handoff Protocol

Every handoff follows three rules:
1. **Use the structured template** defined in the sender's SOP
2. **Receiver must acknowledge** within one task cycle (silence ≠ acceptance)
3. **Partial delivery is OK** — mark it clearly and include a manifest of what's missing

### Primary Pipeline Handoffs

#### Research Agent → Econometrics Agent (Two-Stage)

**Stage 1 — Quick Spec Memo (deliver ASAP):**
- 5-bullet specification memo: DV, regressors, instruments, pitfalls, sample conventions
- Naming: `docs/spec_memo_{topic}_{date}.md`

**Stage 2 — Full Research Brief:**
- Complete brief with literature synthesis, specification details table, data sources with series IDs, event timeline, references
- Naming: `docs/research_brief_{topic}_{date}.md`

#### Research Agent → Data Agent

- Data source recommendations table (variable, series ID, MCP server, frequency, availability status)
- Included in the research brief; Dana extracts on receipt

#### Data Agent → Econometrics Agent

- Analysis-ready dataset (`.parquet` or `.csv`)
- Data dictionary with Display Name column (variable name, display name, description, source, series ID, unit, transformation, SA status, known quirks)
- Summary statistics
- Stationarity test results (structured table: variable, test, statistic, p-value, lags, conclusion)
- Handoff message using Data-to-Econ template (see Dana's SOP)
- Naming: `data/{subject}_{frequency}_{start}_{end}.parquet`

#### Econometrics Agent → Visualization Agent

- Fitted model results (`.pkl`)
- Coefficient tables (`.csv`) using standardized schema: `variable`, `coef`, `se`, `t_stat`, `p_value`, `ci_lower`, `ci_upper`
- Diagnostic test results (standardized table: test, statistic, p-value, interpretation)
- **Chart Request Template** (chart type, data source path, key variables, main insight sentence, audience, comparison notes, special annotations)
- Naming: `results/{model_name}_{date}.pkl`, `results/{model_name}_coefficients_{date}.csv`

#### Visualization Agent → Alex

- Charts (`.png` and `.svg`) with versioning: `_v{N}`
- Formatted tables (`.md` and `.csv`)
- One-line captions for each chart
- Annotation source tracking table
- Naming: `output/{subject}_{chart_type}_{date}_v{N}.{ext}`

### Direct (Non-Pipeline) Handoffs

#### Data Agent → Visualization Agent

- For exploratory charts, data quality plots, descriptive visualizations
- Dataset with Display Name metadata in data dictionary
- Data quirks relevant to visual interpretation
- See Dana's SOP: Data-to-Viz Handoff section

#### Research Agent → Visualization Agent

- Event timeline (date, event, relevance, type) for chart annotations
- Domain visualization conventions from literature
- See Ray's SOP: Event Timeline section

#### Econometrics Agent → Data Agent (Mid-Analysis)

- Expedited single-variable requests during diagnostics
- Must include: variable name, source preference, urgency flag, econometric rationale
- See Evan's SOP: Mid-Analysis Data Requests section

### Portal Assembly Handoffs

#### Visualization Agent → App Dev

- Plotly figure objects (`.json` or Python code) for interactive charts
- Static chart files (`.png`, `.svg`) for fallback
- Chart specifications (data source, key message, caption)
- See Vera's SOP: Output Standards

#### Research Agent → App Dev

- Narrative text sections (markdown) for each portal page
- Section ordering and storytelling arc
- Plain-English interpretation of findings for layperson audience

#### Data Agent → App Dev

- Data refresh pipeline code or specifications
- Cached dataset locations and update frequency
- Data dictionary for any series displayed in the portal

#### Econometrics Agent → App Dev

- Model result summaries for display (key coefficients, diagnostics, strategy performance)
- Backtest results in tabular format
- Regime/signal status for any live indicators

#### App Dev → Alex

- Running portal URL (Streamlit Community Cloud)
- Portal architecture documentation
- User guide for content updates

## Shared Workspace Structure

```
/workspaces/aig-rlic-plus/
├── app/               # Streamlit portal source code (Ace owns)
│   ├── app.py         # Main Streamlit entry point
│   ├── pages/         # Multi-page app sections
│   ├── components/    # Reusable UI components
│   └── assets/        # Static assets (images, CSS)
├── data/              # Cleaned, analysis-ready datasets
├── results/           # Model outputs, coefficient tables, diagnostics
├── output/            # Final charts, tables, reports
├── docs/              # Research briefs, documentation
│   └── agent-sops/    # This folder — agent SOPs
├── cache/             # Temporary cached data (auto-cleaned)
├── temp/              # Scratch space (auto-archived)
└── scripts/           # Reusable analysis scripts
```

## Acknowledgment Protocol

Every handoff requires a structured acknowledgment from the receiver:

1. **Sender** delivers output using the handoff template from their SOP
2. **Receiver** acknowledges within one task cycle with:
   - What was received (file list)
   - Whether it meets their needs (accepted / accepted with caveats / blocked — specify what's missing)
   - Any questions or follow-ups
3. **If no acknowledgment** within one task cycle, sender follows up explicitly
4. **Silence is never acceptance** — an unacknowledged handoff is an open loop

## Communication Rules

1. **Use TaskList / TaskUpdate** for tracking — do not rely on messages alone
2. **Be explicit about blockers** — if you need input from another agent, say exactly what you need
3. **Deliver incrementally** — a partial dataset now is better than a perfect one late
4. **Flag surprises immediately** — unexpected data patterns, missing series, test failures
5. **Never overwrite another agent's output** — create versioned files with `_v{N}` suffix
6. **Acknowledge every handoff** — confirm receipt and adequacy (see Acknowledgment Protocol above)
7. **Cite upstream contributions** — reference teammates' deliverables by file path in your output

## Naming Conventions

### Files

| Type | Pattern | Example |
|------|---------|---------|
| Dataset | `data/{subject}_{freq}_{start}_{end}.parquet` | `data/macro_panel_monthly_200001_202312.parquet` |
| Research brief | `docs/research_brief_{topic}_{date}.md` | `docs/research_brief_phillips_curve_20260228.md` |
| Model results | `results/{model}_{date}.pkl` | `results/phillips_ols_20260228.pkl` |
| Coefficients | `results/{model}_coefficients_{date}.csv` | `results/phillips_ols_coefficients_20260228.csv` |
| Chart | `output/{subject}_{type}_{date}.png` | `output/us_inflation_line_20260228.png` |
| Table | `output/{subject}_table_{date}.md` | `output/regression_results_table_20260228.md` |

### Branches (if applicable)

- `analysis/{topic}` for analysis work
- `data/{source}` for data pipeline changes
- `docs/{topic}` for documentation updates

## Escalation Rules

| Situation | Action |
|-----------|--------|
| Missing data for a required variable | Data agent flags to Alex; suggests alternatives |
| Model diagnostics fail | Econometrics agent reports to Alex with proposed fix |
| Conflicting literature findings | Research agent presents both sides; Alex decides |
| Chart request is ambiguous | Visualization agent asks econometrics agent for clarification |
| Any agent is blocked for > 1 task cycle | Escalate to Alex immediately |

## Quality Standards (Team-Wide)

- Every output file has a descriptive name following the naming convention
- Every handoff includes a structured message using the sender's SOP template
- Every handoff is acknowledged by the receiver within one task cycle
- No agent delivers output without running their quality gate checklist
- All code is reproducible — another agent should be able to re-run it
- Assumptions are documented, not implicit
- Upstream contributions are cited by file path

### Defense 1: Self-Describing Artifacts (Producer Rule)

**Any artifact that crosses an agent boundary must carry enough context that the consumer cannot misinterpret it.** Implicit assumptions — state labels, sign conventions, units, date ranges, return types, merge keys — are the #1 source of silent errors in multi-agent pipelines.

**Concrete requirements for producers:**

1. **Column names encode meaning, not indices.** Never deliver columns named `state_0`, `regime_1`, `cluster_2`. Use `stress_prob`, `calm_prob`, `high_vol_regime`. If a model assigns numeric labels, rename them before saving the output file.

2. **Units are explicit.** Include units in column names (`spread_bps`, `return_pct`, `vol_annualized`) or in a sidecar metadata file. Never assume the consumer knows your unit convention.

3. **Sign conventions are stated.** Document whether positive means "widening" or "tightening", whether a higher value means "more stressed" or "less stressed". If the convention is non-obvious, add a comment in the data dictionary row.

4. **Date/sample boundaries are in the file.** If an artifact is OOS-only, the filename or metadata must say so. Never rely on the consumer knowing your train/test split.

5. **Sidecar manifest for model artifacts.** Every `.pkl` or `.parquet` model output must be accompanied by a `_manifest.json` that documents: what each column/variable means, what higher/lower values signify, and at least one sanity-check assertion (see Defense 2).

**Why this matters:** When Vera receives `prob_state_0` and `prob_state_1`, she must guess which is stress. If Evan delivers `prob_stress` and `prob_calm`, guessing is impossible. This principle applies to every handoff, not just HMM states — it covers sign conventions, return types (arithmetic vs geometric), threshold directions, and any other implicit assumption.

### Defense 2: Reconciliation at Every Boundary (Consumer + Reviewer Rule)

**Every agent that consumes an upstream artifact must verify that their interpretation produces results consistent with the upstream agent's reported numbers.** Gate reviewers must run automated numerical reconciliation, not just structural checks.

**Concrete requirements:**

**For consumers (Vera, Ace, or any downstream agent):**

1. **Sanity-check on ingestion.** Before using any upstream data, verify at least one known fact. Examples:
   - "During GFC (2008-09), stress probability should be > 0.8"
   - "Tournament winner Sharpe should be ~1.17"
   - "B&H max drawdown should be ~-34%"
   These checks are derived from the upstream agent's summary or handoff message. If the check fails, STOP and ask — do not proceed with a guess.

2. **Cross-check derived outputs against source.** If you compute a drawdown curve from raw data, the max drawdown of that curve must match the number reported in the upstream results CSV (within rounding). If it doesn't, your interpretation of the data is wrong.

3. **When in doubt, verify with a known period.** Pick a well-understood historical episode (GFC, COVID) and confirm your derived series behaves as expected during that period. This catches sign inversions, unit errors, and state label swaps generically.

**For gate reviewers (Alex):**

4. **Automated reconciliation script.** Before signing off on any gate, run a script that compares every number displayed in the portal/charts against the source CSV/parquet. This is not optional spot-checking — it is a systematic check that every displayed number traces back to the ground truth.

5. **Reconciliation covers derived quantities.** Don't just check that "Sharpe = 1.17" appears correctly. Recompute the Sharpe from the equity curve data in the chart and verify it matches. This catches errors in the derivation, not just the label.

**Template for a reconciliation script:**

```python
# gate_reconciliation.py — mandatory before Gate 3/4 sign-off
import json, pandas as pd

def reconcile_chart(chart_name, check_fn, tolerance=0.02):
    """Load a chart JSON and run a numerical check against ground truth."""
    with open(f'output/charts/plotly/{chart_name}.json') as f:
        fig = json.load(f)
    result = check_fn(fig)
    assert result, f"RECONCILIATION FAILED: {chart_name}"
    print(f"  OK  {chart_name}")

# Example checks:
# 1. Drawdown chart W1 MDD must match tournament CSV
# 2. Equity curve final value must be consistent with reported annualized return
# 3. HMM stress probability must be high during GFC, low during 2013-2014
# 4. KPI card numbers must match tournament CSV
# ... add one check per chart
```

**Why this matters:** Structural reviews (files exist, parse OK, titles are good) catch ~20% of errors. Numerical reconciliation catches the remaining ~80% — the silent errors where the chart looks plausible but shows the wrong data. The cost of writing these checks is low; the cost of shipping wrong charts is high.

## Task Completion Hooks (Team-Wide Standard)

Every agent must run these two hooks when completing any task. Individual SOPs contain role-specific details; these are the universal minimums.

### Hook 1: Validation & Verification (before marking task done)

1. **Re-read the original request** — does the deliverable actually answer what was asked?
2. **Run your Quality Gates checklist** — every box must be checked
3. **Self-review** — read your output as if you were the receiving agent. Would you accept this?
4. **Verify file naming and location** — follows conventions, saved to correct workspace directory
5. **Send structured handoff message** — use the template from your SOP
6. **Request acknowledgment** — explicitly ask the receiver to confirm

### Hook 2: Reflection & Memory (after every completed task)

1. **What went well? What was harder than expected?**
2. **Did any handoff friction occur?** Note it for SOP improvement
3. **Did you learn something reusable?** (data gotcha, method insight, tool trick, collaboration pattern)
4. **Distill 1-2 key lessons** and update your memories file at `~/.claude/agents/{your-id}/memories.md`
5. **Cross-project lessons** go to `~/.claude/agents/{your-id}/experience.md`
6. **If a lesson affects another agent's workflow**, message them directly — don't assume they'll discover it

These hooks are not optional. They are the mechanism by which the team improves over time. Skipping them to save time is a false economy — the cost shows up as repeated mistakes and handoff friction in future tasks.

## New Agent Onboarding Protocol

When a new agent joins the team (or when the team is first formed), run this cross-review exercise before starting real work:

### Step 1: Cross-Review SOPs
Every agent reads ALL teammates' SOPs plus the team coordination protocol. Each writes a structured review covering:
1. What I learned about each teammate's workflow and pressures
2. Where our handoffs connect and where friction could arise
3. Suggestions for each teammate's SOP (empathy, rapport, handoff clarity)
4. Suggestions for my own SOP (blind spots revealed by reading others')
5. Suggestions for the team coordination protocol

Reviews are saved to `docs/agent-sops/reviews/{agent-id}-review.md`.

### Step 2: Self-Update SOPs
Each agent incorporates the best feedback into their own SOP. Ownership matters — you update your own SOP, not someone else's.

### Step 3: Distill and Remember
Each agent distills key lessons into:
- `~/.claude/agents/{agent-id}/memories.md` (gotchas, insights, commitments)
- `~/.claude/agents/{agent-id}/experience.md` (cross-project patterns)

### Why This Matters
Reading teammates' SOPs reveals handoff gaps, duplicated work, and blind spots that no amount of solo work surfaces. This is not optional — it is the single highest-leverage activity for team cohesion. Do it for every new team or whenever the team composition changes.

---

## Retrospective

After completing a major analysis (not after every task), the team lead (Alex) convenes a brief retrospective:

1. Each agent reviews their Input Quality Log / memories for recurring friction
2. Top 3 improvement suggestions are collected
3. SOPs are updated by their respective owners
4. Team coordination protocol is updated if cross-cutting changes are needed
5. Learnings are promoted to global experience files if cross-project applicable
