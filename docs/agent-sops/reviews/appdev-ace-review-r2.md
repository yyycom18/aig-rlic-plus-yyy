# Cross-Review: App Dev Ace (Round 2)

**Date:** 2026-02-28
**Agent:** appdev-ace
**Context:** New agent onboarding cross-review per team-coordination.md New Agent Onboarding Protocol

---

## 1. What I Learned About Each Teammate's Workflow and Pressures

### Dana (Data Agent)

Dana is the foundation layer. Every downstream agent depends on her output quality. Key observations:

- She operates under a strict quality-gate regime: monotonic date indices, no silent fills, documented missingness, stationarity tests, and a mandatory data dictionary with every delivery. This is good -- it means I can trust what arrives in `data/`.
- Her biggest pressure is **completeness vs. speed**. She has a Partial Delivery Protocol for when APIs are down or a series is hard to source, which tells me she regularly faces sourcing friction.
- She runs stationarity tests (ADF, KPSS, PP) and delivers structured results. This is an econometrics concern, but Dana owns the execution -- a smart division of labor that avoids duplicated work.
- She serves both Evan and Vera directly, each with different handoff templates. Data-to-Viz includes Display Names for chart labels; Data-to-Econ includes stationarity results.
- Her anti-patterns list is strict: no `inplace=True`, no silent drops, no positional merges. This signals past pain from sloppy data pipelines.

**Pressure point for my intake:** Dana's output reaches me indirectly (through Vera's charts and Evan's results) AND directly (data files for the portal's live data layer). I need to understand both pathways.

### Evan (Econometrics Agent)

Evan is the analytical engine. He consumes Dana's data and Ray's research brief, then produces the model results everyone downstream depends on. Key observations:

- He has a rigorous two-source intake: Ray's research brief for specification guidance, and Dana's dataset for the actual data. He explicitly documents which of Ray's recommendations he adopts vs. departs from.
- His output is heavily structured: coefficient tables use a standardized CSV schema (`variable`, `coef`, `se`, `t_stat`, `p_value`, `ci_lower`, `ci_upper`), diagnostics use a standardized table format, and sensitivity tables follow a multi-column comparison layout.
- He produces a **Chart Request Template** for Vera with a "Main insight" sentence per chart -- this is the title Vera uses. This is critical because it means chart titles carry Evan's economic interpretation, not just variable names.
- His mid-analysis data requests to Dana can trigger expedited sourcing. This means the data pipeline is not always sequential -- there are feedback loops.
- He saves model objects as `.pkl` for reuse, which is relevant for my portal if I need to run any computations dynamically.

**Pressure point for my intake:** Evan delivers model result summaries, backtest performance tables, and strategy rules in plain English. My SOP says I need these, but Evan's SOP does not explicitly define a handoff template TO me (Ace). His Chart Request Template goes to Vera, and his narrative goes to Alex. My intake from Evan is currently informal.

### Vera (Visualization Agent)

Vera is my most direct upstream dependency for chart assets. Key observations:

- She has detailed per-chart-type input checklists (coefficient plot, time-series, scatter, distribution, diagnostic panel, heatmap, bar, regression table, sensitivity table). These checklists are exhaustive and well-documented.
- She requires a "Key message / insight" for every chart -- without it, delivery is blocked. This is a hard gate, not a suggestion.
- She maintains an Acknowledgment Template that she sends back to every requester, confirming what she received and what is missing. This is excellent practice for closing feedback loops.
- She has an Input Quality Log (`docs/agent-sops/viz-input-quality-log.md`) that tracks handoff quality over time. This is a continuous improvement mechanism I should adopt.
- Her output formats are PNG + SVG for charts, MD + CSV for tables, HTML for interactive charts, with a versioning convention (`_v{N}`).
- She has three input pathways: Econ-to-Viz (primary), Data-to-Viz (direct for exploratory), Research-to-Viz (annotation layer from Ray).

**Pressure point for my intake:** Vera delivers static charts and Plotly figure objects. My SOP lists "Plotly figure objects or specifications" as the primary input, but Vera's SOP primarily uses matplotlib/seaborn for static charts and Plotly for interactive. I need to clarify when she delivers Plotly objects vs. static PNGs, because the portal strongly prefers Plotly for interactivity.

### Ray (Research Agent)

Ray provides the intellectual scaffolding that gives the analysis its narrative spine. Key observations:

- He uses a Two-Stage Delivery: a quick spec memo (5 bullets for Evan to start immediately) followed by a full research brief. This is a throughput optimization -- Evan does not have to wait for the full literature synthesis.
- His research brief template is the most comprehensive document on the team: executive summary, literature findings, consensus view, open questions, recommended specification details table, variables-used-in-key-studies table, recommended data sources with exact series IDs, event timeline for Vera, domain visualization conventions, and full references.
- He performs a Data Feasibility Check against the team's MCP stack before recommending sources. This prevents Dana from chasing unavailable series.
- He has a Data Source Feedback Loop: when Dana reports a recommended source is impractical, Ray finds alternatives and updates the brief.
- His event timeline is a standard attachment for Vera's chart annotations AND potentially for my portal (structural breaks, policy events, regime shifts).

**Pressure point for my intake:** Ray provides narrative text sections in markdown for each portal page, the storytelling arc, and plain-English definitions. But his SOP's primary delivery format is the research brief -- not portal-ready narrative. I need to clarify whether Ray delivers separate portal narrative or if I extract/adapt from the research brief.

---

## 2. Where Handoffs TO Me Might Cause Friction

### Vera -> Ace: Chart Format Ambiguity

**Issue:** My SOP asks for "Plotly figure objects or specifications" as primary input. Vera's SOP defaults to matplotlib/seaborn for static charts and uses Plotly selectively for interactive. The team-coordination.md says Vera delivers "Plotly figure objects (`.json` or Python code) for interactive charts" and "static chart files (`.png`, `.svg`) for fallback."

**Friction risk:** If Vera delivers mostly static PNGs (her natural default), I either display them as images (losing interactivity) or have to recreate them in Plotly (duplicating work and risking inconsistency with Vera's visual standards).

**Suggested resolution:** Agree upfront on which charts need Plotly interactivity (time-series with date sliders, regime selectors) vs. which are fine as static images (coefficient plots, diagnostic panels). This should be part of the portal brief, not discovered at assembly time.

### Ray -> Ace: Narrative Text Gap

**Issue:** Ray's SOP focuses on delivering research briefs and spec memos to Evan and Dana. His brief template includes an "Implications for Our Analysis" section and literature synthesis, but not portal-ready narrative text.

**Friction risk:** My SOP says "Ray provides the narrative text; Ace integrates it with Vera's charts." But Ray's deliverables are academic-style briefs, not layperson narrative. I may need to rewrite extensively, which risks losing Ray's domain expertise or introducing errors.

**Suggested resolution:** Ray should deliver a separate "Portal Narrative" document alongside the research brief, written for a layperson audience. Alternatively, my SOP should acknowledge that I will adapt Ray's brief into portal narrative and send it back to Ray for accuracy review.

### Evan -> Ace: No Formal Handoff Template

**Issue:** Evan has a Chart Request Template for Vera and structured handoff messages for Dana. But the team-coordination.md lists my inputs from Evan as "model result summaries, backtest results, regime/signal status" without a formal template.

**Friction risk:** I may receive model results in inconsistent formats, or miss key context that Evan communicated to Vera but not to me.

**Suggested resolution:** Define an Econ-to-AppDev handoff template, even if lightweight: file paths, key findings for KPI cards, strategy rules in plain English, any interactive analysis specs.

### Dana -> Ace: Refresh Pipeline Specification

**Issue:** My SOP lists "data refresh specifications" as a needed input from Dana. Dana's SOP does not mention any handoff to me or any refresh pipeline documentation.

**Friction risk:** If the portal needs live/refreshed data, I will not know which series update, how often, or from which API without going back to Dana.

**Suggested resolution:** Dana should include a "Refresh Metadata" section in her data dictionary when the data is portal-bound: update frequency, API source, any rate limits, expected staleness window.

---

## 3. Suggestions for Each Teammate's SOP

### Dana

1. **Add a Data-to-AppDev handoff section.** Currently Dana has Data-to-Econ and Data-to-Viz but not Data-to-AppDev. For portal-bound data, I need: file locations, refresh specs (which API, how often), and known display quirks.
2. **Include a "Refresh Metadata" field in the data dictionary.** When a series is used in a live portal (not just a one-time analysis), I need to know the update cadence and API source for caching decisions.

### Evan

1. **Add an Econ-to-AppDev handoff template.** Even a lightweight one: file paths to model results, 3-5 key findings for KPI cards, strategy rules in plain English, and any specs for interactive analysis (what should users toggle?).
2. **Clarify backtest output format.** My SOP mentions "backtest performance tables (metrics, equity curves, regime periods)" but Evan's SOP does not specify the format for backtest results. A standardized CSV schema would help.

### Vera

1. **Clarify Plotly vs. static output defaults.** Vera's SOP favors matplotlib for most chart types and Plotly for interactive. For portal-bound charts, I need Plotly objects. A "Portal Delivery" variant of her output standards (Plotly-first) would reduce rework.
2. **Deliver chart specs as code, not just images.** If Vera provides the Plotly figure-building code (or serialized `.json` figures), I can integrate them directly. Static PNGs are a last resort for the portal.

### Ray

1. **Add a portal narrative deliverable.** Ray's research brief is written for the team (academic tone). The portal needs layperson narrative. Either Ray writes a parallel "Portal Narrative" section, or we formalize that I adapt his brief and send it back for accuracy review.
2. **Deliver event timeline in machine-readable format.** Ray's event timeline is markdown in the research brief. A CSV version (`date, event, relevance, type`) would let me programmatically add annotations to Plotly charts without manual extraction.

---

## 4. Suggestions for My Own SOP (Blind Spots Revealed)

1. **Acknowledge the narrative adaptation step.** My SOP says "Ray provides the narrative text; Ace integrates it with Vera's charts." In reality, Ray provides research briefs, not portal copy. I should add an explicit step: "Adapt research brief into layperson narrative. Send adapted text back to Ray for accuracy review before publishing."

2. **Add an Input Acknowledgment Template.** Vera has one, and the team-coordination protocol requires acknowledgments. My SOP does not include a structured acknowledgment template for when I receive inputs from teammates. I should add one.

3. **Clarify Plotly vs. static expectations upfront.** My SOP should specify which portal pages need Plotly interactivity and which are fine with static images, so Vera knows what to deliver from the start.

4. **Add an Input Quality Log.** Vera maintains one (`viz-input-quality-log.md`). As the integration point consuming everyone's output, I should track input quality too. This would surface systemic handoff issues at retrospectives.

5. **Define the portal-bound data contract.** My "Inputs I Need" from Dana section should explicitly state: "For any data series displayed in the portal, provide: file path, update frequency, API source, cache TTL recommendation, and known display quirks."

6. **Add Evan's coefficient CSV schema to my SOP.** My SOP does not reference Evan's standardized column schema (`variable`, `coef`, `se`, `t_stat`, `p_value`, `ci_lower`, `ci_upper`). I should document this as the expected format for model results I display.

---

## 5. Suggestions for team-coordination.md

1. **Add an Econ-to-AppDev handoff template.** The Portal Assembly Handoffs section lists what Evan sends me, but there is no structured template. Adding one would formalize the handoff and prevent ad-hoc delivery.

2. **Clarify Plotly deliverable expectations for portal-bound charts.** The Viz-to-AppDev handoff mentions "Plotly figure objects (`.json` or Python code)" but this is not reconciled with Vera's SOP, which defaults to matplotlib. The coordination protocol should state: "For portal-bound charts, Vera delivers Plotly figure objects. For report-only charts, static PNG/SVG is acceptable."

3. **Add a "Portal Brief" task type.** The Standard Task Flow goes from analysis to portal assembly, but there is no defined "Portal Brief" artifact (analogous to the Research Brief or Chart Request). Alex should create one that specifies: storytelling arc, target audience, which findings to highlight, data freshness requirements.

4. **Formalize the narrative adaptation workflow.** Between Ray's research brief and the portal's layperson narrative, someone has to translate. The coordination protocol should specify who owns this: does Ray write portal copy, does Ace adapt it, or is it a joint effort with a review loop?

5. **Add Ace to the Standard Task Flow feedback loops.** The current flow shows Ace at the end (step 6), but in practice I should be scaffolding the portal during steps 2-4 (as noted in the protocol). Making this explicit -- with early portal architecture review by Alex -- would catch structural issues before content arrives.

---

## Summary

As the integration point, my biggest risks are: (a) format mismatches between what teammates deliver and what the portal needs, (b) the narrative gap between Ray's academic briefs and layperson portal text, and (c) the absence of formal handoff templates from Evan and Dana to me specifically. The team's SOPs are exceptionally well-structured for the core analytical pipeline (Ray -> Dana -> Evan -> Vera), but the portal assembly pathway needs more formalization.
