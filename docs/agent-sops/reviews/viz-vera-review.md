# Cross-Review: Viz Vera

*Reviewer:* Viz Vera (Visualization Agent)
*Date:* 2026-02-28

---

## 1. What I Learned About My Teammates

### Data Dana (Data Agent)

Dana is the foundation of the pipeline. Her work is all about precision and trust: if the data is wrong, everything downstream is wrong. She operates under heavy quality-gate pressure — stationarity checks, missing-value documentation, merge integrity, duplicate detection — and she has to deliver not just data but a full data dictionary alongside it. The pressure she faces is invisible to most of the team: when things go right, nobody notices; when a single date misalignment slips through, it can silently corrupt a model and a chart. She is methodical by necessity, and she values explicitness above all (descriptive column names, documented transformations, no silent operations). Her anti-pattern list tells me she has been burned by subtle errors before.

### Econ Evan (Econometrics Agent)

Evan is the analytical core of the team. He carries the heaviest methodological burden: choosing the right model class, justifying identification strategies, running extensive diagnostics, and then interpreting results with economic substance rather than just statistical significance. What struck me is how much judgment his work requires — it is not just running regressions, it is deciding which regression to run and defending that choice. He faces pressure from two directions: rigor (diagnostics, sensitivity analysis, robust standard errors) and communication (he has to translate technical results into narratives that Alex and I can act on). His SOP is the longest and most detailed, which reflects the complexity of what he does. He also has the most direct handoff to me, and the quality of what I produce depends almost entirely on what he delivers.

### Research Ray (Research Agent)

Ray provides the intellectual scaffolding. Without his briefs, Evan would be specifying models in a vacuum, and I would not know what story the charts should tell. Ray's challenge is different from the others: he deals in ambiguity and judgment. Academic papers contradict each other, methodologies vary, and findings can be regime-dependent. He has to synthesize all of that into actionable guidance without oversimplifying. His SOP reveals a strong emphasis on source credibility hierarchies and fact-checking, which tells me he takes the "garbage in, garbage out" principle seriously at the intellectual level, not just the data level. He also faces time pressure — the team cannot wait for a perfect literature review, so he has to deliver incrementally and flag gaps honestly.

---

## 2. Where Our Work Connects

### What I Receive and From Whom

| Source | What I Receive | Format | Quality Concerns |
|--------|---------------|--------|-----------------|
| Econ Evan | Fitted model results | `.pkl` | Can I always unpickle these reliably? Version/env mismatch risk |
| Econ Evan | Coefficient tables | `.csv` | Are column names standardized across model types? |
| Econ Evan | Diagnostic test results | `.md` or `.csv` | Format varies — sometimes markdown, sometimes CSV |
| Econ Evan | Chart specifications | Informal message | Often underspecified — "make a coefficient plot" without stating which coefficients to highlight |
| Econ Evan | Interpretation notes | Informal message | Quality varies — sometimes rich, sometimes absent |
| Data Dana | Raw or cleaned datasets | `.parquet` / `.csv` | Needed when I build exploratory charts directly from data (bypassing Evan) |
| Research Ray | Context for annotations | Research briefs | Useful for adding event markers, regime shading, contextual annotations |

### What I Deliver and To Whom

| Recipient | What I Deliver | Format |
|-----------|---------------|--------|
| Alex | Charts | `.png` + `.svg` |
| Alex | Formatted tables | `.md` + `.csv` |
| Alex | One-line captions | Inline with delivery message |

### Potential Friction Points

1. **Evan's chart specifications are informal.** There is no template or structured format for visualization requests. This leads to back-and-forth that slows delivery.
2. **Diagnostic format inconsistency.** Evan sometimes sends diagnostics as markdown, sometimes as CSV. I need a consistent format to automate diagnostic visualization.
3. **No direct channel from Ray to me.** Research briefs go to Evan, but I often need context too (e.g., event dates for overlays, regime boundaries, key threshold values). I have to either ask Evan to relay this or go read the briefs myself.
4. **Dana's data sometimes needed directly.** For exploratory visualization or data quality charts, I need Dana's output directly, but the formal flow routes everything through Evan. This creates unnecessary delays for simple data plots.

---

## 3. Suggestions for SOP Improvements

### For Data Dana's SOP

1. **Add a "Visualization-Ready" output option.** When Dana delivers datasets, she could optionally include a note about which variables are suitable for direct plotting (e.g., already in human-readable units, with clean labels). This would save me from having to reverse-engineer transformations. A simple line in the data dictionary — "Plot-ready: Yes/No" — would suffice.

2. **Standardize column naming for visual labels.** Dana's column names like `us_cpi_yoy` are great for code but poor for chart labels. Consider adding a metadata field for display names (e.g., `us_cpi_yoy` -> "US CPI (% YoY)"). This is a small addition that would eliminate a recurring manual step for me.

3. **Include sample period and frequency in the filename or metadata.** Dana already does this in filenames, which is excellent. But the data dictionary should also include a "recommended chart type" note for time-series vs. cross-section data — this helps me pick the right visualization immediately.

4. **Know this about my constraints:** I cannot produce a good chart from data I do not understand. If the data dictionary is missing or incomplete, I will have to ask questions that delay the whole pipeline. The data dictionary is not bureaucracy — it is my primary input document.

### For Econ Evan's SOP

1. **Create a structured visualization request template.** This is my top suggestion. Evan's SOP says he should deliver "specification of what charts/tables are needed" but provides no structure. I propose a simple template:

   ```
   ## Viz Request
   - Chart type: [coefficient plot / time-series / scatter / diagnostic panel / table]
   - Data source: [file path to results or data]
   - Key message: [what should the reader conclude?]
   - Variables to highlight: [list]
   - Comparison: [e.g., "Model 1 vs. Model 2" or "Pre/post break"]
   - Special annotations: [events, thresholds, confidence bands]
   ```

   This would cut my clarification requests by 80%.

2. **Standardize coefficient table column names.** Different model types in `statsmodels` vs. `linearmodels` produce different column names for the same concepts (e.g., "coef" vs. "Coef." vs. "parameter"). Evan should normalize these before handoff. A consistent schema: `variable`, `coef`, `se`, `t_stat`, `p_value`, `ci_lower`, `ci_upper`.

3. **Always include interpretation notes.** Evan's SOP lists this as a deliverable but does not make it mandatory. From my perspective, interpretation notes are not optional — they tell me what the chart's title should say. "US Inflation Accelerated After 2020" is a title I can write only if Evan tells me that is the finding.

4. **Save diagnostic results in a consistent format.** Pick one: CSV with standardized columns (`test_name`, `statistic`, `p_value`, `interpretation`). This lets me automate diagnostic summary tables and panels.

5. **Know this about my constraints:** I cannot invent the narrative. A chart title should state the finding, not just name the variables. If Evan does not tell me the finding, I either have to interpret the results myself (which is not my job and risks misrepresentation) or deliver a generic title that does not serve the reader. My quality gate literally requires "title states the insight" — so please give me the insight.

### For Research Ray's SOP

1. **Add a "Key Dates and Thresholds" section to research briefs.** When Ray identifies structural breaks, policy changes, or regime shifts in the literature, he should call these out in a dedicated section with specific dates and values. These are gold for my annotations — event lines, regime shading, threshold markers. Currently I have to mine this information from prose paragraphs.

2. **Include visual references when available.** If a paper Ray reviews contains a particularly effective chart or visualization approach, a note about it would help me. Something like: "Taylor (2019) uses a dual-panel chart with inflation expectations on top and realized inflation below — effective for showing expectation anchoring." This helps me choose chart designs grounded in domain conventions.

3. **Flag data visualization conventions in the literature.** Different fields have charting conventions (e.g., yield curves are always plotted with maturity on x-axis; Phillips curves traditionally show unemployment on x and inflation on y). If Ray notices conventions relevant to our analysis, a brief note saves me from committing domain faux pas.

4. **Know this about my constraints:** I am the last agent in the chain, which means delays upstream compress my time most. If Ray's brief arrives late, Evan is delayed, and I get squeezed. Incremental delivery (which Ray's SOP already encourages) is not just nice — it is essential for my ability to do quality work.

---

## 4. Suggestions for My Own SOP

After reading my teammates' SOPs, I see several things my own SOP should add or change:

1. **Add an "Inputs I Need" section.** My SOP describes what I produce but is vague about what I require. I should explicitly list the minimum viable input for each chart type (e.g., coefficient plot needs: variable names, point estimates, standard errors, confidence level, and the key finding for the title). This would help Evan and Dana know exactly what to deliver.

2. **Add a direct data visualization pathway.** My SOP assumes all inputs flow through Evan, but Dana sometimes needs charts directly (data quality visualizations, exploratory plots, distribution checks). I should formalize a "Data -> Viz" pathway with its own input specification, separate from the "Econ -> Viz" pathway.

3. **Add an "Annotation Source" checklist.** For every chart, I should document where annotations came from (Ray's brief, Evan's interpretation, Alex's instruction). This creates an audit trail and ensures I am not inventing context.

4. **Include a feedback loop section.** My SOP has no mechanism for me to give feedback to upstream agents about input quality. I should add a standard "Input Quality Note" that I send back with every delivery, noting what was clear, what required clarification, and what was missing. This builds a continuous improvement loop.

5. **Add table formatting standards for different model types.** Evan's SOP lists various model classes (OLS, IV, panel, GARCH). My SOP should have a corresponding section showing the standard table layout for each, so Evan knows what I will produce and can flag if it does not match his expectations.

6. **Mention the filesystem MCP server for loading inputs.** My SOP lists `filesystem` for saving outputs but should also explicitly mention using it to load `.pkl`, `.csv`, and `.parquet` files from the `results/` and `data/` directories.

---

## 5. Suggestions for Team Coordination Protocol

1. **Add a "Viz Request" handoff template in the Econometrics -> Visualization section.** The current protocol says Evan delivers "Specification of what charts/tables are needed" but provides no structure. Adding the template I proposed in Section 3 would standardize this handoff and reduce friction.

2. **Add a Data -> Visualization direct pathway.** The current flow diagram shows visualization only receiving from econometrics. In practice, Dana and I interact directly for data exploration charts, quality checks, and descriptive visualizations that do not require model estimation. The protocol should acknowledge and formalize this.

3. **Add a Research -> Visualization pathway.** Similarly, Ray's briefs sometimes contain information I need directly (event dates, regime definitions, domain chart conventions). The protocol should allow me to receive research briefs directly, not only through Evan.

4. **Expand the "Communication Rules" section with a feedback mechanism.** The current rules are about forward-flow (deliver, flag, escalate). There is no formal mechanism for downstream agents to give structured feedback to upstream agents. I suggest adding: "After receiving a handoff, the receiving agent sends a brief acknowledgment noting: (a) what was received, (b) any missing items, (c) estimated delivery time for their own output."

5. **Add a versioning protocol for iterative outputs.** The protocol says "never overwrite another agent's output" and suggests versioned files, but does not specify how. I suggest: `{original_name}_v{N}.{ext}` where N increments. This matters most for me because Alex often requests chart revisions, and I need a clear naming scheme for iterations.

6. **Include estimated turnaround times for each handoff type.** This would help the team understand pipeline dynamics. As the last agent in the chain, I am most affected by upstream delays, and having visibility into expected handoff durations would let me plan my work better.

7. **Add a "Working Agreements" section.** Small things that reduce friction: preferred message format for handoffs, how to request urgent turnaround, when to use TaskUpdate vs. direct messages. These soft protocols matter as much as the formal ones.

---

*This review reflects my honest assessment after reading all four SOPs and the coordination protocol. The team has strong foundations — clear roles, well-defined quality gates, and a sensible pipeline structure. The gaps I have identified are mostly about handoff specificity and bidirectional communication. Fixing these would reduce back-and-forth, prevent rework, and let each of us do our best work.*

— Viz Vera
