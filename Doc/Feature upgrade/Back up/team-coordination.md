# Team Coordination Protocol

(rest of original content from main repo)

## [NEW COMPONENT – Indicator Evaluation Framework]
> The Indicator Evaluation Framework is a new layer in the dashboard architecture, sitting above research, data, econometric, and visualization pipelines to aggregate, summarize, and render indicator classification, evidence alignment, and strategy viability before deep-dive analysis. It provides a single summary entrypoint for coordinated decision making and user narrative orientation at the top of each indicator overview.

**Primary ownership of the evaluation layer belongs to the App Dev agent, which orchestrates the assembly of indicator identity, environment interaction scores, and strategy survival scores into the dashboard interface.**

While all agents contribute upstream artifacts, the App Dev layer is responsible for ensuring the evaluation framework correctly aggregates these outputs and presents normalized indicator summaries.

**Team Coordination Considerations**:
- No existing pipeline or agent workflow is altered—all handoffs and artifact standards remain.
- Each agent’s outputs flow into the new framework through standardized result files, taxonomies, and summary panels managed by App Dev.
- Collaboration focus: keep indicator taxonomy and mapping logic documented, regularly update provenance/calculation rules, and align narrative text with evolving research/strategy insights.
- For integration with Main, all agents should review and maintain mapping from source (YYY) files to Main repo structures.
