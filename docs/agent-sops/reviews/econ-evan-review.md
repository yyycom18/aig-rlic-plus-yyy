# Cross-Review: Econ Evan

**Author:** Evan (Econometrics Agent, `econ-evan`)
**Date:** 2026-02-28
**Scope:** Review of all teammate SOPs and team coordination protocol

---

## 1. What I Learned About My Teammates

### Data Dana (Data Agent)

Dana is the foundation builder. Her entire workflow is oriented around one principle: **data quality is non-negotiable**. She operates under constant pressure from two directions — upstream data sources that are unreliable or incomplete, and downstream consumers (me, primarily) who need analysis-ready datasets on a schedule.

What matters most to her:
- Completeness and correctness of every delivered dataset
- Documentation (data dictionaries, summary stats, transformation logs)
- Reproducibility of the data pipeline — no ad-hoc steps that can't be retraced

Pressures she faces:
- API rate limits, outages, and data availability gaps across MCP servers
- Balancing speed of delivery against thoroughness of validation
- Handling ambiguous requests where the "right" frequency or transformation isn't obvious
- Being the first link in the chain means her delays cascade to everyone

I respect that her SOP explicitly forbids silent operations — no silent drops, no silent fills, no `inplace=True`. That discipline protects the whole team.

### Viz Vera (Visualization Agent)

Vera is the translator. She turns our quantitative outputs into visual narratives that Alex (and ultimately stakeholders) can act on. Her guiding philosophy is Tufte — maximize data-ink ratio, no chartjunk, let the data speak.

What matters most to her:
- Clarity of the story a chart tells — titles should state the insight, not just the variable
- Accessibility (colorblind-safe palettes, legible text at output size)
- Consistency of style across all project outputs

Pressures she faces:
- She is at the end of the pipeline, so she inherits every upstream delay
- She often needs interpretation guidance that goes beyond raw numbers — "what should this chart emphasize?"
- Balancing publication quality with speed when the team is iterating

I notice that Vera's SOP has the most detailed style specifications of any agent. That consistency is valuable for the project's credibility.

### Research Ray (Research Agent)

Ray is the intellectual scaffolding. His job is to ensure our models are grounded in established theory and current institutional reality, not just data-mining exercises. He operates in the most unstructured space on the team — literature searches don't have clean APIs with guaranteed output formats.

What matters most to him:
- Source credibility and proper attribution
- Presenting both sides of debates, not just the convenient narrative
- Making findings actionable — "Implications for Our Analysis" is a required section, not an afterthought

Pressures he faces:
- Open-ended scope — "survey the literature on X" can consume unlimited time
- Verifying claims in papers he can only access partially (paywalls, incomplete fetches)
- Delivering context fast enough to inform model specification without holding up the pipeline
- The temptation to over-deliver (comprehensive survey) vs. what the team actually needs (focused brief)

I appreciate that Ray's SOP explicitly warns against delaying delivery for perfection. That's a mature stance that shows awareness of team dynamics.

---

## 2. Where Our Work Connects

### What I Receive

| From | What | When | Risk Points |
|------|------|------|-------------|
| **Data Dana** | Analysis-ready dataset + data dictionary + summary stats + stationarity tests | Before I can specify or estimate anything | If the dataset has undocumented transformations, I may misspecify the model. If stationarity results are missing, I have to redo work. |
| **Research Ray** | Research brief + recommended specifications + identification strategies | Ideally before model specification, but can arrive in parallel | If the brief arrives after I've already specified the model, it may require re-work. If specification recommendations are too vague, they're not actionable. |
| **Alex** | Analysis brief with question, dependent variable, candidate regressors, identification strategy | At task creation | If the identification strategy is unclear, I need to propose alternatives — this can block progress. |

### What I Deliver

| To | What | When | Risk Points |
|----|------|------|-------------|
| **Viz Vera** | Fitted model `.pkl`, coefficient tables `.csv`, diagnostics, chart specs with interpretation notes | After estimation and diagnostics pass quality gates | If I deliver raw model objects without interpretation notes, Vera has to guess what the chart should emphasize. If coefficient tables lack clear variable names, she produces mislabeled charts. |
| **Alex** | Narrative interpretation (2-3 paragraphs), sensitivity analysis, full diagnostics | With the model results | If I bury the economic interpretation in technical jargon, Alex has to translate again. |

### Key Friction Points

1. **Dana-to-Evan timing.** I cannot start estimation until I have the dataset. If Dana encounters data sourcing issues, I'm blocked. The coordination protocol acknowledges this but doesn't specify what partial delivery looks like for data.

2. **Ray-to-Evan timing.** Research and data sourcing run in parallel (steps 2-3 in the task flow), but ideally I'd have Ray's specification recommendations before I start modeling. In practice, I may need to start with a baseline specification and refine after the brief arrives.

3. **Evan-to-Vera handoff quality.** My SOP says I deliver "chart specification with interpretation notes" but doesn't formalize what that specification looks like. Vera's SOP says she needs to know "what story the chart should tell." These need to meet in a concrete format.

4. **Variable naming across the pipeline.** Dana names columns descriptively (`us_cpi_yoy`). I use them in formulas (`smf.ols('y ~ us_cpi_yoy + ...')`). Vera labels axes from these names. If naming is inconsistent at any stage, it creates confusion.

---

## 3. Suggestions for SOP Improvements

### For Data Dana's SOP

1. **Add a "partial delivery" protocol.** When a dataset is 80% ready but one series is delayed (e.g., API outage for a single variable), deliver what you have with a clear manifest of what's missing and an ETA. This lets me start exploratory analysis and stationarity checks on the available variables rather than waiting for the complete package. Currently, the SOP implies all-or-nothing delivery.

2. **Include a variable naming contract.** The SOP says "name columns descriptively" but doesn't specify the exact convention. Propose a formal pattern like `{country}_{concept}_{transform}_{freq}` (e.g., `us_cpi_yoy_m`). This prevents me from receiving `cpi_change` one time and `us_cpi_yoy` the next.

3. **Flag econometric implications of data decisions.** When you forward-fill, interpolate, or change frequency, note the econometric implications. For example: "Forward-filled 3 observations for GDP; this may induce serial correlation in monthly regressions." I would rather receive a warning than discover it during diagnostics.

4. **Add a section: "What the econometrics agent needs to know about your constraints."** Data sourcing is not instant. API rate limits, missing series, and frequency mismatches are real. If I understood these constraints better, I'd write more realistic data requests and fewer "can you also add..." follow-ups.

### For Viz Vera's SOP

1. **Add an intake checklist for econometrics handoffs.** When you receive model results from me, you should have: (a) coefficient table with clear variable names, (b) interpretation notes stating the key insight, (c) specification of chart type, (d) sample period, (e) whether the chart is for exploration or final report. Formalizing this prevents back-and-forth.

2. **Include a "question-back" protocol.** If interpretation notes are unclear or missing, the SOP should specify: ask the econometrics agent one structured question (e.g., "What is the main takeaway for the coefficient plot?") rather than guessing. Currently the SOP says "ask what comparison or insight should be highlighted" but doesn't specify who to ask or the format.

3. **Add diagnostic chart templates.** I frequently need residual plots, QQ plots, CUSUM charts, and actual-vs-fitted plots. If Vera has pre-built templates for these standard econometric diagnostics, turnaround would be much faster. The SOP lists "Residual plots (4-panel)" under chart types but doesn't standardize the layout.

4. **Acknowledge iteration.** First-pass charts often need refinement after Alex reviews them. The SOP reads as a single-pass workflow. Add a section on revision cycles: what to expect, how to version chart files, and how to handle conflicting feedback.

### For Research Ray's SOP

1. **Separate "specification guidance" from "literature review."** I need two different things from Ray: (a) actionable model specification recommendations (functional form, instruments, controls) and (b) broader context for interpretation. These have different urgency levels — I need (a) before estimation and (b) can arrive later. The current template lumps them together.

2. **Add a "quick specification memo" format.** For time-sensitive requests, a 5-bullet memo is more useful than a full research brief: (1) recommended dependent variable, (2) key regressors from the literature, (3) common instruments, (4) known identification pitfalls, (5) sample period conventions. The full brief can follow.

3. **Include data availability notes in recommendations.** When Ray recommends a variable or instrument from the literature, note whether it's available through our MCP servers. Recommending "use the Romer & Romer monetary policy shocks series" is less useful if that series requires manual construction. A quick check with Dana's sourcing priority list would close this gap.

4. **Flag when literature findings depend on specific econometric methods.** If a paper's result holds under IV but not OLS, that matters for my specification. The "Methodology" extraction field exists but the SOP doesn't emphasize flagging method-sensitivity.

---

## 4. Suggestions for My Own SOP

After reading my teammates' SOPs, I see several gaps in my own:

1. **Formalize the chart specification handoff to Vera.** My SOP says I deliver "specification of what charts/tables are needed" and "interpretation notes" but doesn't define the format. I should add a template:
   ```
   Chart Request:
   - Type: [coefficient plot / time-series / scatter / diagnostic]
   - Data source: [file path to .csv or .pkl]
   - Key variables: [list]
   - Main insight: [one sentence the title should convey]
   - Audience: [exploration / final report]
   - Special notes: [highlight specific coefficients, add confidence bands, etc.]
   ```

2. **Add a "data request specification" template for Dana.** Rather than ad-hoc requests, I should standardize what I ask for:
   ```
   Data Request:
   - Variables: [list with preferred names]
   - Frequency: [daily / monthly / quarterly]
   - Sample period: [start-end]
   - Transformations needed: [log, difference, YoY, none]
   - Stationarity tests: [yes/no, which tests]
   - Priority: [core variables vs. nice-to-have]
   ```

3. **Add an "iterate with Ray" step.** After receiving the research brief, I should explicitly confirm which specification recommendations I'm adopting and which I'm departing from, with reasons. This closes the feedback loop and builds institutional knowledge.

4. **Document my diagnostic output format.** Vera and Alex both consume my diagnostics. I should standardize the format: a markdown table with test name, test statistic, p-value, and one-line interpretation. Currently my SOP lists what tests to run but not the output format.

5. **Add a sensitivity analysis reporting standard.** My SOP says "report a sensitivity table" but doesn't specify the format. I should adopt a standard layout: main specification in column 1, alternatives in subsequent columns, with rows for each coefficient and bottom rows for diagnostics.

6. **Be more explicit about acknowledging teammates' contributions.** Dana's data quality work and Ray's literature search are invisible in my final output. I should add a practice of noting in my narrative: "Using the dataset prepared by Dana (see data dictionary at ...)" and "Following the specification recommended by Ray's brief (see ...)."

---

## 5. Suggestions for Team Coordination Protocol

1. **Define a "partial handoff" mechanism.** The protocol describes clean, sequential handoffs but real work is messier. Add guidance for: (a) delivering 80% of a dataset with a missing-variable manifest, (b) delivering a preliminary specification that will be refined after the research brief arrives, (c) delivering a draft chart that may change after Alex's review. This would reduce blocking.

2. **Add a handoff message template.** The protocol says "every handoff includes a brief message" but doesn't specify the format. Propose:
   ```
   Handoff: [Agent] -> [Agent]
   Files: [list of file paths]
   Summary: [one paragraph]
   Known issues: [list or "none"]
   Questions for recipient: [list or "none"]
   ```

3. **Clarify the parallel execution model.** Steps 2 (Research) and 3 (Data) run in parallel, but step 4 (Econometrics) waits for both. In practice, I can start exploratory analysis as soon as the data arrives, even without the research brief. The protocol should acknowledge this overlap and define what "start early" looks like vs. "wait for all inputs."

4. **Add a version control convention for iterative outputs.** The protocol says "never overwrite another agent's output — create versioned files if updating" but doesn't specify the versioning scheme. Propose appending `_v1`, `_v2` or using datetime stamps. Without a convention, we'll end up with `_final`, `_final2`, `_FINAL_REAL`.

5. **Add a retrospective step.** After each completed analysis cycle, the team should briefly document: what worked, what caused friction, what to change. This is how SOPs improve over time. Currently there's no feedback loop built into the protocol.

6. **Include estimated turnaround times.** Not exact predictions, but rough guidance: "Data sourcing for a standard macro panel: expect 1 task cycle. Research brief for a well-studied topic: expect 1 task cycle. Novel topic with sparse literature: expect 2 cycles." This helps agents plan dependencies.

7. **Add a "blocked" signaling protocol.** The escalation rules say to escalate to Alex if blocked for more than 1 task cycle, but there's no mechanism for agents to signal "I can start partial work" vs. "I'm completely blocked." A simple status vocabulary would help: `ready`, `partial` (can start with what I have), `blocked` (need input before any progress).

---

## Final Thought

Reading my teammates' SOPs gave me a much clearer picture of the pressures each person operates under. Dana deals with the messiness of raw data that no one else sees. Ray works in the most ambiguous space with the least structured outputs. Vera inherits everyone's time pressure at the end of the pipeline. And I sit in the middle, dependent on both upstream inputs and responsible for the quality of what flows downstream.

The biggest single improvement we could make is formalizing handoff formats. Right now, every SOP describes what to deliver but not the exact shape of the package. A shared "handoff contract" template — even a simple one — would eliminate most of the back-and-forth that slows the team down.

---

*Review completed: 2026-02-28*
*Agent: Econ Evan (`econ-evan`)*
