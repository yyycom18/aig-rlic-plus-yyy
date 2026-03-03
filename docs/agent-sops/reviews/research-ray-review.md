# Cross-Review: Research Ray's Perspective

**Author:** Research Ray (research-ray)
**Date:** 2026-02-28

---

## 1. What I Learned About My Teammates

### Data Dana (data-dana) — Data Engineer / Data Wrangler

Dana is the custodian of data quality. Her workflow is heavily procedural and defensive: inspect raw data before touching it, document every transformation, validate with automated checks, and deliver with a data dictionary. What matters most to her is **completeness and traceability** — she never silently drops observations, never forward-fills across large gaps without flagging, and never delivers without a completeness check. She faces pressure from two directions: upstream data sources that are unreliable or inconsistently formatted, and downstream consumers (mainly Evan) who need clean, correctly aligned datasets on a timeline. Her quality gate checklist is thorough — seven items that must all pass before handoff. The anti-pattern about never using `inplace=True` tells me she has been burned by debugging opaque data pipelines before.

### Econ Evan (econ-evan) — Econometrician / Quantitative Analyst

Evan is the methodological backbone of the team. His SOP is the most intellectually demanding — he must choose the right model class from a wide menu (OLS, IV, panel, time-series, GARCH, cointegration), justify every specification choice, run exhaustive diagnostics, and then interpret results economically, not just statistically. What matters most to him is **rigor and identification** — he never runs a regression without a hypothesis, never claims causality without an identification argument, and never cherry-picks specifications. His biggest pressure is the sheer number of diagnostics required: for a panel IV model, he might need to run 10+ diagnostic tests before he can report a result. He also depends heavily on both Dana and me delivering quality inputs — if my research brief suggests the wrong identification strategy or Dana's data has undocumented gaps, his entire estimation could be compromised.

### Viz Vera (viz-vera) — Data Visualization Specialist / Report Producer

Vera turns numbers into stories. Her SOP reveals someone who cares deeply about **clarity and honesty in visual communication** — she follows Tufte's principles, uses colorblind-safe palettes, and insists that titles state the insight rather than just the variable name. What matters most to her is that a chart tells its story without requiring the reader to consult the text. Her pressure comes from being last in the pipeline: she receives model results and must produce publication-quality output, often with tight deadlines and sometimes with vague requests ("make a chart of X"). She depends entirely on Evan for well-structured model outputs and interpretation notes. The anti-patterns about pie charts, rainbow colormaps, and 3D charts tell me she has strong opinions about visualization integrity — and rightfully so.

---

## 2. Where Our Work Connects

### What I Deliver and To Whom

| Recipient | Deliverable | Format | Purpose |
|-----------|------------|--------|---------|
| Evan | Research brief | Markdown (standard template) | Grounds model specification in literature; provides identification strategies, suggested functional forms, control variable rationale |
| Evan | Recommended model specifications | Within research brief | Gives him a literature-backed starting point rather than guessing |
| Evan | Suggested instruments / identification strategies | Within research brief | Critical for IV estimation — instruments must be argued from theory |
| Dana | Recommended data sources | Within research brief or direct message | Points her to specific series/databases the literature has used |
| Dana | Variable definitions from papers | Within research brief | Ensures she sources the right proxy variables |

### What I Receive and From Whom

| Source | Input | Purpose |
|--------|-------|---------|
| Alex | Research question and scope | Defines what literature to search |
| Dana | (Indirect) Data availability feedback | Sometimes a paper's recommended data does not exist for our sample; Dana flags this, and I need to find alternatives |
| Evan | (Indirect) Follow-up questions on methodology | After reading my brief, Evan may need clarification on a paper's method or deeper detail on an identification argument |

### Where Friction Could Arise

1. **My brief arrives late, Evan is blocked.** Research and data sourcing run in parallel (steps 2-3 in the task flow), but Evan cannot start model specification until both are done. If I get caught in a deep literature rabbit hole, Evan waits.

2. **My data source recommendations are impractical.** I might recommend a dataset from a paper (e.g., "use the Jordà-Schularick-Taylor Macrohistory Database") without checking whether Dana can actually access it through our MCP servers. This creates back-and-forth.

3. **My model recommendations are too vague for Evan.** Saying "the literature uses panel methods" is not helpful. Evan needs specifics: FE vs. RE, which instruments, what lag structure, which controls.

4. **Version drift.** If I update a research brief after Evan has already started working from an earlier version, we risk misalignment. Currently there is no versioning protocol for research briefs.

5. **No direct channel to Vera.** My work rarely flows directly to Vera, but sometimes she needs context for chart annotations (e.g., "what event caused the structural break in Q3 2008?"). There is no formal mechanism for this.

---

## 3. Suggestions for SOP Improvements

### For Data Dana's SOP

1. **Add a "Data Availability Pre-Check" step.** Before deep-diving into sourcing, Dana should cross-reference the research brief's recommended data sources against available MCP servers. This would catch impractical recommendations early and reduce round-trips with me. A simple checklist: "For each variable in the research brief, confirm: (a) MCP server can provide it, (b) frequency matches, (c) sample period is covered."

2. **Include a feedback loop to Research Agent.** Dana's SOP has no step for communicating back to me when a recommended data source is unavailable or problematic. Adding a line like "If a recommended variable or source from the research brief is not accessible, notify the research agent with the specific gap so alternatives can be identified" would save time.

3. **Document data limitations for downstream agents.** Dana's data dictionary is excellent, but it could include a "Known Limitations" field for each variable — e.g., "CPI series revised quarterly; current values are preliminary" or "This series has a structural break in 2010 due to methodology change." This would help both Evan (for model specification) and me (for interpreting results against the literature).

4. **Add a section on understanding the research context.** Dana's SOP is purely technical. A brief note encouraging her to read (or at least skim) the research brief before sourcing would help her understand why certain variables matter and make better judgment calls when she encounters sourcing trade-offs.

### For Econ Evan's SOP

1. **Add a "Research Brief Intake" step.** Evan's workflow starts with "Receive Analysis Brief" but does not explicitly mention reading and acknowledging the research brief. Adding a step like "Read the research brief; confirm that the recommended specifications are feasible given available data; flag any disagreements with the literature's approach" would formalize the handoff.

2. **Include a mechanism for requesting deeper research.** Sometimes Evan will read my brief and realize he needs more detail on a specific identification strategy or a comparison of two methodological approaches. His SOP should include a step: "If the research brief does not cover a needed methodological question, request a targeted follow-up from the research agent with specific questions."

3. **Add interpretation notes for Vera.** Evan's "Deliver Results" section mentions saving model objects and tables, but it could be more explicit about what Vera needs. For instance: "Include a 2-3 sentence 'chart brief' for each requested visualization: what variable(s) to plot, what the chart should highlight, and any annotations (e.g., recession shading, structural break dates)." This would reduce Vera's need to guess.

4. **Cross-reference diagnostics with research brief assumptions.** If the research brief flags potential issues (e.g., "the literature warns about structural breaks post-2008"), Evan's diagnostic step should explicitly check those flagged risks. Adding "Review research brief for flagged risks; ensure diagnostics address each one" would tighten the loop.

### For Viz Vera's SOP

1. **Add a "Context Gathering" step.** Vera's workflow starts with receiving a visualization request but does not mention consulting the research brief for context. Charts are more effective when the designer understands the economic story. A step like "Review the research brief (if available) for economic context, key events, and narrative framing" would improve her chart titles, annotations, and storytelling.

2. **Include a channel for requesting context from Research Agent.** Vera might need to know: "What happened in Q3 2008 that explains this structural break?" or "What is the policy-relevant threshold for this coefficient?" Currently, her escalation path goes to Evan for clarification, but some questions are better directed to me. Adding "For economic context or event identification, consult the research agent" would be efficient.

3. **Add annotation guidelines tied to research findings.** Vera's SOP covers chart mechanics thoroughly but could include guidance on economic annotations: recession shading (NBER dates), policy event markers (rate changes, QE announcements), regime indicators. These are things I can provide if asked. A note like "Request event timeline from research agent for time-series charts spanning significant economic episodes" would produce better charts.

4. **Table formatting should account for sensitivity analysis.** Evan produces sensitivity tables alongside main results, but Vera's table formatting section focuses on single regression tables. Adding guidance for multi-specification comparison tables (e.g., "present as side-by-side panels with shared variable rows") would be practical.

---

## 4. Suggestions for My Own SOP

After reading my teammates' SOPs, I see several improvements I should make to my own:

1. **Add a "Data Feasibility Check" to my deliverables.** Before recommending data sources, I should verify — even briefly — whether they are accessible through our MCP stack. This means checking FRED, Yahoo Finance, Alpha Vantage, and Financial Datasets coverage before writing "use series X." My SOP should include: "For each recommended data source, note the likely MCP server and confirm basic availability. If uncertain, flag as 'availability unconfirmed — Dana to verify.'"

2. **Make model specification recommendations more concrete.** Evan needs specifics, not generalities. My SOP's synthesis template should include a sub-section: "Recommended Specification Details" with fields for: dependent variable, key regressors, control variables, instruments (if IV), lag structure (if time-series), fixed effects dimension (if panel), and functional form. Even if I cannot fill all fields, the template forces me to be specific about what I can.

3. **Add an "Event Timeline" deliverable for Vera.** I should proactively produce a timeline of key economic events relevant to the analysis period (recessions, policy changes, structural breaks) that Vera can use for chart annotations. This should be a standard attachment to the research brief, not something she has to request ad hoc.

4. **Include a "Follow-Up Availability" section.** My SOP should explicitly state that I am available for targeted follow-up requests from both Evan and Vera after the initial brief delivery. I should include turnaround expectations: "Quick-turn clarifications (1-2 specific questions): immediate. Deep-dive follow-ups (new sub-topic): treated as a new research request."

5. **Add incremental delivery guidance.** My SOP says "deliver incrementally rather than waiting for perfection" (in the anti-patterns), but my workflow does not operationalize this. I should add: "For complex topics, deliver a preliminary brief (key findings only) within the first pass, then a full brief with synthesis and recommendations. Notify Evan and Dana when the preliminary version is available so they can begin parallel work."

6. **Add a quality gate for actionability.** My current quality gates focus on sourcing and citation quality. I should add: "Implications section includes at least one specific, testable model specification recommendation" and "Data source recommendations include specific series identifiers (e.g., FRED series code), not just database names."

---

## 5. Suggestions for Team Coordination Protocol

1. **Add a formal research brief acknowledgment step.** The task flow shows Research and Data running in parallel (steps 2-3), then Econometrics starting after both finish. But there is no explicit step where Evan acknowledges receiving and reviewing the research brief. Adding "Econometrics agent confirms receipt of research brief and flags any gaps or disagreements before beginning specification" would catch issues early.

2. **Define a lightweight versioning protocol for handoff documents.** The protocol says "Never overwrite another agent's output — create versioned files if updating" but does not specify how. For research briefs that may evolve, a simple convention like `research_brief_{topic}_{date}_v{n}.md` with a changelog section at the top would prevent version confusion.

3. **Add a Research-to-Visualization handoff.** The current handoff matrix covers Data-to-Econ, Research-to-Econ, Econ-to-Viz, and Viz-to-Alex, but there is no formal Research-to-Viz path. I propose adding:

   > **From Research Agent to Visualization Agent**
   > - Event timeline for chart annotations (key dates, policy events, regime changes)
   > - Economic context summary (1 paragraph) for chart narrative framing
   > - Naming: `docs/event_timeline_{topic}_{date}.md`

4. **Add a "Blockers Board" section.** The communication rules say "Be explicit about blockers" but there is no designated place to record them. A simple shared blockers log (even just a markdown file at `_pws/_team/blockers.md`) where agents post and resolve blockers would improve visibility. Format: `[date] [agent] BLOCKED: [description] NEEDS: [what from whom]`.

5. **Clarify parallel work expectations.** The protocol says steps 2 and 3 run in parallel, but it does not address what happens when one finishes significantly before the other. Adding guidance like "If the research brief is complete but data is still in progress, the econometrics agent may begin exploratory analysis and specification planning using the research brief alone" would reduce idle time.

6. **Add a cross-agent review norm.** Currently, each agent runs their own quality gates but nobody reviews another agent's output before handoff (except Alex at the end). For critical analyses, a lightweight peer review — e.g., "Econometrics agent reviews data dictionary for missing variables before estimating" or "Research agent reviews chart annotations for factual accuracy" — would catch errors earlier and build team trust.

---

*This review reflects my honest assessment as a research analyst who wants the team to work well together. Every suggestion comes from imagining real scenarios where miscommunication or missing context could slow us down or produce weaker output. The team's SOPs are already strong — these suggestions are about closing the remaining gaps.*
