# Cross-Review Round 2: Viz Vera

*Reviewer:* Viz Vera (Visualization Agent)
*Date:* 2026-02-28
*Trigger:* New agent onboarding -- App Dev Ace joins the team

---

## 1. What I Learned About Ace's Workflow and How It Connects to Mine

Ace is the **integration terminus** of the entire pipeline. While I am the last analytical agent (I turn model results into charts), Ace is the last delivery agent (he turns charts, narrative, and data into the user-facing Streamlit portal). This means I now have a **downstream consumer** for the first time -- previously my outputs went directly to Alex for review. The implications are significant:

- **I am no longer the end of the chain.** My outputs are intermediate products that Ace assembles. This changes my quality calculus: I need to think not just about whether a chart looks correct, but whether it is *integrable* -- can Ace embed it in a Streamlit page without rework?
- **Ace needs Plotly objects, not just PNGs.** His SOP explicitly asks for "Plotly figure objects or specifications" as the primary input, with static files as fallback. My current SOP defaults to matplotlib/seaborn for static charts and treats Plotly as the "interactive exploration" option. This needs to change -- Plotly should be my **co-primary** output library when portal integration is the destination.
- **Ace needs captions and chart metadata alongside the figure.** A PNG with a filename is not enough. He needs: the one-line takeaway caption, the data source attribution, and the key message -- all machine-readable or at least clearly documented.
- **Ace shares my colorblind-safe palette.** His SOP explicitly references the same hex codes (`#0072B2`, `#D55E00`, `#009E73`, `#CC79A7`, `#999999`). This is good -- no palette drift.
- **Ace needs to know *where* each chart lives in the storytelling arc.** A chart for page 2 (layperson narrative) has different requirements than one for page 3 (analytical detail) or page 5 (methodology appendix). My current chart request acknowledgment does not capture audience tier.

---

## 2. Where Handoffs to Ace Might Cause Friction

### Plotly Figures: Format Ambiguity

My SOP says I save interactive charts as `.html`. Ace's SOP says he wants "Plotly figure objects or specifications." These are not the same thing. Possible formats include:

| Format | Ace Can Use? | Notes |
|--------|-------------|-------|
| `.html` (self-contained) | Partially -- he would need to iframe it or re-extract | Not ideal for Streamlit |
| `.json` (Plotly JSON serialization) | Yes -- `plotly.io.from_json()` | Clean, portable, version-safe |
| Python code (function returning `go.Figure`) | Yes -- import and call | Most flexible but couples our code |
| `.pkl` (pickled `go.Figure`) | Risky -- environment/version mismatch | Same concern I have with Evan's model pickles |

**My recommendation:** Adopt `.json` as the primary Plotly handoff format. It is serializable, version-safe, and Ace can load it with one line. Provide the generating Python function as a secondary deliverable for cases where Ace needs to modify the figure dynamically (e.g., add interactive filters).

### Chart Captions and Metadata

My current delivery includes a "one-line caption" in the handoff message. Ace needs this caption to be *attached to* the chart file, not floating in a message. Options:

- A sidecar metadata file (`{chart_name}_meta.json`) containing: caption, source, audience tier (layperson / analytical / technical), page placement hint, interactive controls spec
- A standard naming convention that embeds audience tier: `{subject}_{chart_type}_{audience}_{date}_v{N}.json`

### Static Fallbacks

Ace's SOP lists "Static chart files (`.png`, `.svg`) for fallback." My SOP already produces both PNG and SVG. This is compatible, but I should explicitly confirm in each handoff message whether the static files are true fallbacks (identical content to the Plotly version) or supplementary (different content, e.g., a simplified version for print).

### Storytelling Placement

Ace structures the portal in 5 pages with distinct audiences (layperson hook, narrative, evidence, strategy, methodology). My current workflow does not tag charts by intended portal page. If I deliver 8 charts and Ace has to figure out which goes where, that is a source of friction and misplacement risk.

### Interactive Controls Specification

Ace adds interactive controls (date range sliders, regime selectors, variable toggles) on top of the charts. If I hand him a static Plotly figure, he may need to decompose and rebuild it to add interactivity. It would be more efficient for me to indicate *what interactivity is appropriate* for each chart so he can plan his component architecture.

---

## 3. Suggestions for Ace's SOP

1. **Specify the exact Plotly input format you prefer.** The SOP says "Plotly figure objects or specifications" -- this is ambiguous. State explicitly: "Preferred format: Plotly JSON (`.json` via `plotly.io.to_json()`). Acceptable: Python function returning `go.Figure`. Not preferred: `.pkl` (version-coupling risk) or `.html` (not embeddable)."

2. **Define a chart metadata schema.** When Ace receives a chart from me, what metadata does he need beyond the figure itself? Propose a standard:
   ```json
   {
     "chart_id": "us_inflation_line_20260228_v1",
     "caption": "US inflation accelerated sharply after 2020",
     "source": "FRED, BLS",
     "audience_tier": "narrative",
     "portal_page": 2,
     "interactive_controls": ["date_range_slider"],
     "data_source_path": "data/macro_panel_monthly_200001_202312.parquet"
   }
   ```
   This eliminates guesswork during portal assembly.

3. **Add a "Chart Integration Checklist" for receiving Vera's outputs.** Similar to my Acknowledgment Template, Ace should acknowledge chart receipt with: what format was received, whether it rendered correctly in Streamlit, whether the caption and metadata were complete, and any modification requests.

4. **Document the Streamlit chart rendering pattern.** Ace's SOP says `st.plotly_chart(fig, use_container_width=True)` -- good. But also document how static fallbacks are rendered (`st.image()` with caption). This helps me understand what happens to my outputs downstream.

5. **Clarify the boundary between Vera's interactivity and Ace's interactivity.** My Plotly figures may already have hover tooltips, zoom, etc. Ace adds Streamlit widgets (sliders, dropdowns) that filter/modify the chart. Where does my responsibility end and his begin? A clear delineation prevents duplicated or conflicting interactive behavior.

---

## 4. Suggestions for My Own SOP (Blind Spots Revealed by Ace's Needs)

1. **Add a Plotly JSON export as a standard output format.** My current Output Standards list PNG, SVG, HTML, and CSV. I need to add: "For portal-destined charts: Plotly JSON (`.json`) as the primary interactive format." This is the single biggest gap.

2. **Add a chart metadata sidecar file.** For every chart destined for the portal, produce a `{chart_name}_meta.json` with: caption, source, audience tier, suggested portal page, and interactive controls hint. This gives Ace structured intake instead of parsing my handoff messages.

3. **Tag charts by audience tier.** My file naming convention (`{subject}_{chart_type}_{date}_v{N}`) does not encode the audience. Add an audience tag: `{subject}_{chart_type}_{audience}_{date}_v{N}` where audience is one of: `exec`, `narrative`, `analytical`, `technical`.

4. **Add an App Dev handoff template.** My SOP has delivery instructions for Alex but no formal handoff template for Ace. Add:
   ```
   Handoff: Viz Vera -> App Dev Ace
   Charts delivered: [list with file paths]
   Format: [Plotly JSON / PNG+SVG / both]
   Metadata files: [list of _meta.json paths]
   Portal page mapping: [chart -> page number]
   Interactive controls notes: [list per chart]
   Static fallbacks included: [yes/no -- identical to interactive? or simplified?]
   Caption and source: [confirmed present in metadata]
   Questions for Ace: [list or "none"]
   ```

5. **Add Plotly as a co-primary library.** My current SOP lists matplotlib as primary and Plotly only for "interactive exploration." With portal integration as a standard deliverable, Plotly should be listed as co-primary for any chart that will be embedded in the Streamlit app.

6. **Document the relationship between static and interactive versions.** When I produce both a PNG and a Plotly JSON for the same chart, I should explicitly state whether they are identical in content or differ (e.g., the static version might have fewer annotations or a simplified layout for print).

---

## 5. Suggestions for team-coordination.md

1. **The Visualization Agent -> App Dev handoff section (line ~124-128) is thin.** It currently says:
   > - Plotly figure objects (`.json` or Python code) for interactive charts
   > - Static chart files (`.png`, `.svg`) for fallback
   > - Chart specifications (data source, key message, caption)

   This should be expanded to include: chart metadata sidecar files, audience tier tagging, portal page mapping, interactive controls specification, and the Viz-to-App handoff message template.

2. **The team structure diagram should show the Viz->App Dev dependency clearly.** The current diagram correctly shows Ace at the bottom receiving from Vera, but the text should explicitly state that Vera's outputs are intermediate products when portal assembly is in scope.

3. **Add a "Portal Assembly Phase" section.** The Standard Task Flow (steps 1-7) ends with "Alex reviews." When portal assembly is in scope, steps 5 and 6 need more detail:
   - Step 5 (Viz) should note: "Produce portal-ready outputs (Plotly JSON + metadata) alongside standard static outputs."
   - Step 6 (App Dev) should note: "Ace can begin portal scaffolding during steps 2-4" (already present, good) and "Ace receives final chart package from Vera at step 5 completion."

4. **The Naming Conventions table should include Plotly JSON and metadata files:**
   | Type | Pattern | Example |
   |------|---------|---------|
   | Plotly chart | `output/{subject}_{type}_{audience}_{date}_v{N}.json` | `output/us_inflation_line_narrative_20260228_v1.json` |
   | Chart metadata | `output/{subject}_{type}_{audience}_{date}_v{N}_meta.json` | `output/us_inflation_line_narrative_20260228_v1_meta.json` |

---

## Summary

Ace's arrival creates a new downstream dependency for my work. The core challenge is ensuring my outputs are not just visually correct but **integration-ready**: serializable Plotly objects, structured metadata, audience tagging, and clear handoff documentation. My round-1 review focused on improving what I *receive* from upstream. This round-2 review focuses on improving what I *deliver* downstream. Both directions matter equally.

The team's pipeline is now complete: Research -> Data -> Econometrics -> Visualization -> App Dev -> Alex. Every link needs a clean handoff protocol, and the Viz-to-App Dev link is the newest and least tested.

---

*-- Viz Vera, 2026-02-28*
