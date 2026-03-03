# Cross-Review Round 2: Data Dana's Perspective (Ace Onboarding)

**Author:** Data Dana (`data-dana`)
**Date:** 2026-02-28
**Trigger:** New agent onboarding -- App Dev Ace (`appdev-ace`) joins the team
**Reviewed SOPs:** All five agent SOPs + team coordination protocol

---

## 1. What I Learned About Ace's Workflow and How It Connects to Mine

Ace is the **integration endpoint**. He consumes outputs from every agent on the team and assembles them into a Streamlit portal that tells a cohesive story to a layperson audience. His role is fundamentally different from everyone else on the team: while Ray, Evan, Vera, and I each produce intermediate analytical artifacts, Ace produces the final user-facing product.

**What Ace needs from me specifically (from his SOP, "Inputs I Need" section):**
- Data file locations and formats (parquet/CSV in `data/`)
- Data dictionary for any series displayed in the portal
- Data refresh specifications (which series update, how often, from which API)
- Known data quirks that affect display (base year changes, gaps)

**Key architectural details that affect my work:**
- Ace loads data via `pd.read_parquet()` from the `data/` directory with `@st.cache_data` caching
- He uses TTL-based cache expiry (e.g., `ttl=3600` for market data) -- so he needs to know which series are "live" vs. "static"
- His portal pages reference data files directly, so file paths and naming must be stable and predictable
- He inherits the team's colorblind-safe palette from Vera, so display-name metadata flows through to the portal

**Where Ace fits in the pipeline:**
Per team-coordination.md, Ace is step 6 -- after Vera (step 5), but with direct inputs from me (step 3) and Ray (step 2). He can begin scaffolding during steps 2-4, which means he may ask me about data structure and file locations before the analysis-ready dataset is finalized.

---

## 2. Where My Handoffs to Ace Might Cause Friction

### 2.1 Data Dictionary Completeness for Portal Display

My current data dictionary format includes: Column Name, Display Name, Description, Source, Series ID, Unit, Transformation, Seasonal Adj., Known Quirks. This was designed for Evan (econometric consumption) and Vera (chart labels). Ace needs additional fields:

- **Refresh frequency:** Is this series updated daily, monthly, quarterly, or is it a one-time pull? My dictionary does not currently capture this.
- **API source for refresh:** Which MCP server or API endpoint provides updates? Ace needs this for his `@st.cache_data(ttl=...)` logic.
- **Display format:** Does the portal show this as a percentage, an index level, or a dollar amount? My "Unit" field partly covers this, but Ace may need explicit formatting hints (e.g., "2 decimal places", "comma-separated thousands").

### 2.2 File Naming Stability

My naming convention is `{subject}_{frequency}_{start}_{end}.{ext}`. This embeds the date range in the filename. When I refresh data and the end date changes, the filename changes -- which breaks Ace's hardcoded `pd.read_parquet("data/macro_panel_monthly_200001_202312.parquet")` references. Ace will need either:
- A stable filename alias (e.g., `data/macro_panel_monthly_latest.parquet`) that I update on refresh, or
- A manifest file that maps logical dataset names to current physical filenames

### 2.3 Data Refresh Specifications

My SOP currently treats each data delivery as a one-time event. Ace's portal, however, implies an ongoing data pipeline: cached data with TTL expiry, live signals, and auto-refresh. I have no documented protocol for:
- How to specify which series need periodic refresh
- How to communicate refresh schedules
- How to handle versioning when data is updated in place vs. appended

### 2.4 Data Quirks for Layperson Display

My "Known Quirks" column is written for Evan (econometric implications) and Vera (chart interpretation). Ace needs a **layperson-facing version** -- e.g., instead of "Base year changed 1982-84; may induce level shift in index comparisons," he needs "Note: CPI measurement methodology was updated in the early 1980s, which can affect long-term comparisons."

---

## 3. Suggestions for Ace's SOP

1. **Add a Data Intake Specification.** Ace's "Inputs I Need" section from Dana is good but lightweight. He should add a structured intake template (similar to the Data Request Template Evan uses) so I know exactly what he needs per dataset:
   ```
   ## Data Intake — [Portal Page]
   From: App Dev Ace
   To: Data Dana
   Variables needed: [list]
   Refresh requirement: [one-time / daily / weekly / monthly]
   Display format: [percentage / index / currency / raw]
   Layperson quirk notes needed: [yes/no]
   ```

2. **Specify the stable filename contract.** Ace should document whether he expects stable filenames or a manifest file, so I can plan my delivery workflow accordingly. This should be in his SOP under "Implement Data Layer."

3. **Add a Data-to-AppDev handoff acknowledgment.** Ace's SOP has no acknowledgment step for data receipt. Given that the team uses structured acknowledgments (per team-coordination.md), Ace should confirm that data files are loadable, paths are correct, and the data dictionary covers the portal's display needs.

4. **Document the caching-to-refresh mapping.** Ace's SOP mentions `@st.cache_data(ttl=3600)` but does not specify how he determines TTL values. He should document: "TTL values are set based on the refresh frequency in Dana's data dictionary." This closes the loop between my refresh specs and his caching logic.

---

## 4. Suggestions for My Own SOP (Blind Spots Revealed by Ace's Needs)

1. **Add a Data-to-AppDev Handoff section.** I have Data-to-Econ and Data-to-Viz handoff templates but nothing for Ace. I need a dedicated section covering:
   - Dataset file paths (stable references)
   - Extended data dictionary with refresh frequency, API source, and display format hints
   - Layperson-friendly quirk descriptions
   - A handoff message template

2. **Add a "Refresh Specification" field to the data dictionary.** New columns needed: `Refresh Frequency` (one-time / daily / monthly / quarterly), `Refresh Source` (MCP server or API), `Last Updated` (timestamp). This directly feeds Ace's caching logic.

3. **Consider a stable-filename alias strategy.** When I deliver or refresh datasets, also create/update a symlink or "latest" copy at a stable path. Document this convention so Ace (and other consumers) can rely on predictable paths.

4. **Add layperson-friendly quirk descriptions.** Alongside the technical "Known Quirks" column (for Evan), add a "Display Note" column with plain-English descriptions suitable for portal display to non-specialist readers.

5. **Document the partial-delivery implications for Ace.** My SOP has a Partial Delivery Protocol, but Ace's portal may break if expected data files are missing. I should note: "When delivering partial data, notify Ace explicitly which files are affected so he can render placeholder content or skip affected pages."

---

## 5. Updates Needed to team-coordination.md

1. **The team structure diagram is already updated** to include Ace at the bottom of the pipeline. Good.

2. **The "Portal Assembly Handoffs" section covers Dana-to-AppDev** with: data refresh pipeline code/specs, cached dataset locations and update frequency, data dictionary for portal-displayed series. This is adequate for now but could be more specific about the stable-filename contract and refresh specification format.

3. **Suggestion: Add a "Data Refresh Protocol" subsection.** The current team-coordination.md treats the analysis as a one-shot pipeline (steps 1-7). With a live portal, there is an ongoing maintenance dimension. Add a subsection under Portal Assembly Handoffs documenting:
   - Who owns data refresh (Dana)
   - How refresh schedules are communicated (via data dictionary)
   - How Ace is notified when data is updated
   - How versioning works for refreshed datasets

4. **Suggestion: Add Ace to the Acknowledgment Protocol examples.** The protocol is generic but all concrete examples in the handoff sections reference Ray, Dana, Evan, Vera. Adding Ace-specific examples would help ground the protocol.

---

## Summary of Key Observations

- Ace's role as integration endpoint means he has the broadest dependency surface on the team. He needs inputs from all four of us, which makes handoff clarity especially important.
- My biggest gap is the **absence of a Data-to-AppDev handoff template** and the lack of **refresh/update metadata** in my data dictionary.
- The filename stability issue is a latent bug waiting to happen -- it will surface the first time I refresh a dataset and Ace's portal breaks.
- The cross-review onboarding exercise worked well in round 1 and continues to surface real friction points. This is now a formalized team norm per team-coordination.md's New Agent Onboarding Protocol section.

---

*Written in good faith as part of the New Agent Onboarding Protocol. Every suggestion comes from imagining the real integration friction that arises when an app developer tries to build a stable portal on top of a research-oriented data pipeline.*
