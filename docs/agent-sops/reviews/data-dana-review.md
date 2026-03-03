# Cross-Review: Data Dana's Perspective

**Author:** Data Dana (`data-dana`)
**Date:** 2026-02-28
**Reviewed SOPs:** Econometrics Agent, Visualization Agent, Research Agent, Team Coordination Protocol

---

## 1. What I Learned About My Teammates

### Econ Evan (Econometrics Agent)

Evan is the methodological backbone of the team. His workflow is deeply structured around hypothesis-driven analysis -- he will not touch a regression without a stated hypothesis, an identification strategy, and a plan for diagnostics. What matters most to him is rigor: robust standard errors by default, sensitivity analysis as a non-negotiable step, and economic interpretation over statistical output. His pressure points are clear: he depends on clean, well-documented data arriving on time, and he needs the research context to justify his model specification choices. If either input is late or ambiguous, his entire pipeline stalls. He also carries the heaviest diagnostic burden on the team -- the sheer number of tests he must run (residual normality, heteroskedasticity, serial correlation, instrument validity, panel diagnostics) means he cannot afford to spend time re-cleaning data or guessing what a variable means.

### Viz Vera (Visualization Agent)

Vera is a design-minded professional who follows Tufte's principles seriously. She cares about clarity, accessibility, and the story a chart tells. Her workflow depends on receiving well-structured model results (pickle files, coefficient CSVs, diagnostic tables) along with clear interpretation notes about what the chart should highlight. The pressure she faces is mostly downstream ambiguity: vague requests like "make a chart of X" without specifying the insight to convey. She also has a meticulous quality gate around colorblind safety, legibility, and anti-chartjunk principles. Her output is the team's public face -- the charts and tables that Alex and external audiences see -- so she carries reputational risk for the entire pipeline.

### Research Ray (Research Agent)

Ray provides the intellectual foundation. He sources academic papers, central bank publications, and policy documents, then synthesizes them into structured research briefs. What matters most to him is source credibility and balanced presentation -- he explicitly refuses to present a single study as consensus and insists on noting contradictory evidence. His pressure comes from scope management: open-ended research requests can spiral, and he rightly insists on scoping approval before deep-diving. He also carries a unique time pressure because his output (literature context, recommended model specs, identification strategies) feeds into both my data sourcing decisions and Evan's model specification, so delays from Ray cascade.

---

## 2. Where Our Work Connects

### What I Deliver and To Whom

| Recipient | Deliverable | Format | Risk Points |
|-----------|-------------|--------|-------------|
| Econ Evan | Analysis-ready dataset | `.parquet` or `.csv` | Variable naming mismatch, undocumented transformations, missing stationarity tests |
| Econ Evan | Data dictionary | Markdown table | Incomplete descriptions, ambiguous units |
| Econ Evan | Summary statistics | `df.describe()` output | Missing distributional context (skewness, outlier flags) |
| Econ Evan | Stationarity test results | Text/table | Test choice mismatch (ADF vs. KPSS vs. Phillips-Perron) |
| Viz Vera | (Indirect) Clean datasets if she needs raw data for exploratory charts | `.parquet` / `.csv` | She may not know my naming conventions |

### What I Receive and From Whom

| Source | Deliverable | What I Need From It | Risk Points |
|--------|-------------|---------------------|-------------|
| Alex | Data request | Variables, frequency, sample period, source preference | Ambiguous proxy variable requests |
| Research Ray | Research brief | Recommended data sources, specific series names, time periods used in literature | Vague data pointers ("use CPI" without specifying which CPI measure, SA vs. NSA, index vs. YoY) |
| Econ Evan | (Feedback loop) Requests for additional variables or transformations mid-analysis | Clear specification of what is needed | Ad-hoc requests that break the pipeline flow |

### Where Friction Could Arise

1. **Ray to Dana handoff (data source recommendations):** Ray's brief may recommend "the standard macro variables" without specifying exact FRED series IDs, frequency, or seasonal adjustment. I then have to guess or ask, which costs a round-trip.

2. **Dana to Evan handoff (stationarity testing):** My SOP says to deliver stationarity results, and Evan's SOP says he runs his own ADF/KPSS tests in exploratory analysis. This is duplicated work. We need to agree: do I deliver pre-tested results that Evan trusts, or does he always re-run? If both, we waste cycles. If only one, who owns it?

3. **Dana to Vera (indirect):** There is no formal handoff defined between me and Vera. But if she needs raw data for time-series plots or distribution charts, she currently has no documented way to request it from me. She would go through Evan or Alex, adding latency.

4. **Mid-analysis data requests:** Evan may discover during diagnostics that he needs an additional control variable or instrument. This triggers an unplanned data sourcing cycle. There is no expedited path for these requests in the current protocol.

---

## 3. Suggestions for SOP Improvements

### For Econ Evan's SOP

1. **Add a "Data Requirements Specification" step before estimation.** After the analysis brief and before exploratory analysis, Evan should produce a structured data request listing exact variables, acceptable proxies, and minimum sample requirements. This would eliminate ambiguity in what I source and reduce back-and-forth. A simple template:
   ```
   Required: [variable] | Proxy acceptable: [yes/no] | Frequency: [M/Q] | Min period: [YYYY-YYYY]
   ```

2. **Clarify stationarity test ownership.** Evan's SOP Section 2 (Exploratory Analysis) says he runs ADF/KPSS on each series. My SOP says I deliver stationarity results. Add a note: "If the data agent has already provided stationarity tests, review and confirm rather than re-running from scratch. Flag disagreements."

3. **Document the feedback loop for mid-analysis data needs.** Add a subsection: "If additional variables are needed during estimation or diagnostics, submit a structured request to the data agent specifying the variable, source preference, and urgency. Do not source data independently unless it is a trivial lookup."

4. **Empathy note -- what Data Dana needs from you:** Add a line: "When requesting data, be specific about units (index level vs. percent change vs. log), seasonal adjustment preference, and whether you need the raw or transformed series. Ambiguous requests cost the data pipeline a full cycle."

### For Viz Vera's SOP

1. **Add a direct data request channel.** Vera's SOP describes receiving inputs from the data agent and econometrics agent, but there is no protocol for Vera to request additional data directly from me (e.g., "I need the raw CPI series for a time-series overlay"). Add: "For raw data needs, submit a request to the data agent specifying the variable, date range, and intended chart type."

2. **Specify expected input formats more precisely.** The SOP says Vera receives "dataset (from data agent) and/or model results (from econometrics agent)" but does not specify what format she expects the dataset in. Add: "Datasets should arrive as `.parquet` or `.csv` with a `DatetimeIndex`, matching the data agent's output standards. If a specific subset or transformation is needed, specify in the request."

3. **Add a "data validation on intake" step.** Before charting, Vera should do a quick sanity check on the data she receives (date range matches expectations, no obvious gaps in time-series, values in plausible range). This catches handoff errors early rather than producing a misleading chart.

4. **Empathy note -- what Data Dana needs from you:** "If a chart reveals unexpected patterns (sudden spikes, gaps, level shifts), flag it back to the data agent before publishing. You may be the first person to visually inspect the data, and your eyes catch things that summary statistics miss."

### For Research Ray's SOP

1. **Make data source recommendations actionable and specific.** The current SOP says to provide "Recommended Data Sources" but does not require specificity. Change to: "Data source recommendations must include: exact series name or identifier (e.g., FRED series ID `CPIAUCSL`), frequency, seasonal adjustment status, and the sample period used in the cited study. Vague pointers like 'use CPI data' are insufficient."

2. **Add a "Data Availability Check" step.** Before finalizing a research brief, Ray should verify (using the `fred` or `yahoo-finance` MCP) that recommended data series actually exist and cover the needed time period. This prevents me from chasing phantom series.

3. **Include a "Variables Used in Key Studies" table.** In the research brief template, add a structured table:
   ```
   | Study | Dependent Variable | Key Regressors | Data Source | Period |
   ```
   This directly feeds both my sourcing work and Evan's specification.

4. **Empathy note -- what Data Dana needs from you:** "The data agent translates your conceptual variable recommendations into actual downloadable series. The more precise you are about what specific data the literature uses, the fewer assumptions the data pipeline has to make. A FRED series ID is worth a thousand words."

---

## 4. Suggestions for My Own SOP

After reading my teammates' SOPs, I see several gaps in my own:

1. **Add a "Data Request Intake" template.** Reading Evan's SOP, I realize I should standardize how I receive requests. My SOP describes what I deliver but not what I need in a request. Add a template:
   ```
   ## Data Request
   - Requester: [agent name]
   - Variables needed: [list with specifics]
   - Frequency: [daily/weekly/monthly/quarterly]
   - Sample period: [start - end]
   - Acceptable proxies: [yes/no, if yes which]
   - Priority: [standard / expedited]
   - Source preference: [any / specific]
   ```

2. **Add an expedited path for mid-analysis requests.** Evan's diagnostics step may reveal the need for an additional instrument or control variable. My SOP should have a lightweight "quick-pull" protocol for single-variable additions that skips the full quality gate where appropriate (e.g., for a quick feasibility check before full processing).

3. **Add a Viz Vera handoff section.** My SOP only documents delivery to the econometrics agent. I should add: "If the visualization agent requests raw or processed data directly, deliver with the same quality gates. Provide a note on any known data quirks that could affect chart interpretation (e.g., base year changes, definitional breaks)."

4. **Include a "Known Data Gotchas" reference.** Reading Ray's emphasis on verifying data citations, I should maintain a running list of series-specific issues (e.g., FRED series that were redefined, seasonal adjustment methodology changes, vintage data differences). This would help the whole team.

5. **Add a post-delivery feedback loop.** After Evan runs his exploratory analysis on my data, I should expect a brief confirmation or issue report. My SOP should say: "After delivery, confirm with the receiving agent that the dataset meets their needs within one task cycle. Resolve issues before they compound."

---

## 5. Suggestions for Team Coordination Protocol

1. **Add a formal mid-analysis data request pathway.** The current task flow shows a clean linear pipeline (Research + Data in parallel, then Econ, then Viz). In practice, Evan will need additional data during modeling. Add a documented "feedback loop" arrow from Econ back to Data with a lightweight request protocol, so these requests do not get treated as new full tasks.

2. **Define a direct Data-to-Viz handoff.** The protocol currently shows Viz receiving input only from Econ. Add an optional direct path from Data to Viz for exploratory visualizations or data quality charts that do not require a model. This is useful for early-stage data inspection and for Alex's review.

3. **Add a "handoff acknowledgment" step.** The protocol says "every handoff includes a brief message describing what's being delivered," but does not require the receiver to acknowledge receipt and confirm adequacy. Add: "The receiving agent must acknowledge the handoff within one task cycle and flag any issues. Silence is not acceptance."

4. **Clarify file versioning rules.** The protocol says "never overwrite another agent's output -- create versioned files if updating" but does not specify a versioning convention. Add: append `_v2`, `_v3` or use datetime stamps (e.g., `macro_panel_monthly_200001_202312_20260228.parquet`) to distinguish versions.

5. **Add a "Definition of Done" for each handoff.** Each handoff section lists deliverables but does not say what constitutes "done." For example, is the Data-to-Econ handoff done when the files are saved, when a message is sent, or when Evan confirms the data is adequate? Clarifying this prevents work from falling through the cracks.

6. **Include a team-wide "Data Quirks Log."** A shared markdown file (e.g., `docs/data_quirks_log.md`) where any agent can note data issues they discover. Ray might notice a paper uses a revised series, Vera might spot a visual anomaly, Evan might find a structural break. Centralizing this benefits everyone.

---

*This review is written in good faith with the goal of making our team work more smoothly. Every suggestion comes from imagining the real friction points that arise when four specialists try to produce rigorous economic analysis under time pressure. The SOPs are already strong -- these are refinements, not overhauls.*
