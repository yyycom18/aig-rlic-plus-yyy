# Cross-Review: Research Ray (Round 2 -- Ace Onboarding)

**Reviewer:** Research Ray
**Date:** 2026-02-28
**Trigger:** New agent onboarding -- App Dev Ace joins the team

---

## 1. What I Learned About Ace's Workflow and How It Connects to Mine

Ace is the **integration point** for the entire team. He consumes outputs from every agent and assembles them into a Streamlit portal that tells a story to a layperson audience. His portal follows a five-page narrative structure: Hook, Story, Evidence, Strategy, Method.

My primary connection to Ace is through **two deliverables**:

1. **Narrative text sections** (markdown) for each portal page -- especially Page 2 ("The Story"), which is the layperson narrative walkthrough. Ace explicitly expects me to provide plain-English text, structured per portal page, with definitions for technical terms and no unexpanded acronyms.

2. **Storytelling arc** -- the ordering and flow of sections, key transitions between concepts, and audience guidance. This is listed as a *mandatory* input without which Ace will not begin building. If Alex does not provide it, Ace looks to me.

Additionally, Ace needs the **event timeline** I already produce for Vera, to power chart annotations in the portal. This is a shared deliverable -- one table serves both Vera and Ace.

Ace works on a different timescale from the rest of the team: he can scaffold the portal structure during steps 2-4 (while I am researching and Evan is modeling), but he cannot populate content until the rest of us deliver. This means my narrative text is on the critical path for the portal -- delayed narrative = delayed portal.

## 2. Where My Handoffs to Ace Might Cause Friction

### 2a. Narrative text format mismatch

My current SOP does not specify a delivery format for narrative text. I produce research briefs that are structured for Evan and Dana -- they are technical, citation-heavy, and organized by methodology. Ace needs something very different: **layperson prose**, organized by portal page, with progressive disclosure (simple first, detail behind expanders). If I hand Ace a research brief and expect him to extract the layperson narrative, he will waste a full cycle doing editorial work that I should have done.

### 2b. Storytelling arc ambiguity

Ace lists the storytelling arc as a mandatory input. My SOP does not mention producing one. Currently, the arc would come from Alex, but Ace's SOP says "from Alex *or* Ray." If Alex delegates this to me, I need a clear process for defining it -- section order, transitions, key audience moments. Today I have no template or protocol for this.

### 2c. Plain-English definitions

Ace's portal is layperson-first: "No jargon without definition; no acronyms without expansion on first use." My research briefs assume the reader is Evan (an econometrician). If I provide narrative text with terms like "endogeneity," "unit root," or "HAC standard errors" without plain-English glosses, Ace either has to define them himself (risky -- he may get the nuance wrong) or bounce it back to me.

### 2d. Section-per-page delivery

Ace's five-page structure means he needs content chunked per page: Hook, Story, Evidence, Strategy, Method. My current output is a single research brief. I need to either (a) produce separate markdown sections aligned to Ace's page structure, or (b) clearly mark sections in my brief with the page they map to.

## 3. Suggestions for Ace's SOP

1. **Add an intake template for narrative text from Ray.** Just as Vera has an Acknowledgment Template, Ace should define what "narrative text sections in markdown" means concretely: word count per page, tone (AP style? conversational?), whether I should provide the markdown with Streamlit-compatible headers, whether expander content should be marked separately.

2. **Clarify the storytelling arc handoff.** Ace's SOP says "from Alex or Ray" but does not specify what format or level of detail he needs. A brief template would help: thesis statement, 3-5 act structure, key transitions, target reading time.

3. **Add a "Content Refresh" handoff protocol.** When the analysis is updated (new data, revised model), Ace needs updated narrative. His SOP mentions a "content update guide" as a deliverable but not a protocol for receiving updated content from upstream agents.

4. **Reference the event timeline explicitly.** Ace lists "event timeline data for chart annotations" under inputs from Ray, but his portal page descriptions do not mention where these annotations go. Linking the timeline to specific pages (e.g., Page 3 interactive charts) would clarify usage.

## 4. Suggestions for My Own SOP (Blind Spots Revealed)

1. **Add an App Dev Handoff section.** My SOP currently defines handoffs to Evan, Dana, and Vera but not to Ace. I need a structured deliverable specification for narrative text, storytelling arc, and plain-English definitions.

2. **Define a "Portal Narrative" output format.** Separate from the research brief, I should produce a markdown document organized by Ace's portal pages (Hook, Story, Evidence, Strategy, Method) with layperson prose, glossary entries, and expander-ready detail blocks.

3. **Add a Storytelling Arc template.** If Alex delegates narrative architecture to me, I need a lightweight template: thesis, section order, key transitions, audience assumptions.

4. **Strengthen the plain-English commitment.** My Anti-Patterns section should include: "Never deliver narrative text to Ace with undefined jargon. Every technical term must have a parenthetical plain-English definition on first use."

5. **Ensure the event timeline handoff message goes to Ace as well as Vera.** My current handoff step 9 sends the timeline to Vera but not Ace.

## 5. Updates Needed to team-coordination.md

1. **The team structure diagram is correct** -- Ace is shown at the bottom as the integration point receiving from both the Viz and Research branches. No change needed.

2. **Portal Assembly Handoffs section (Research Agent -> App Dev)** is present and accurate. It lists: narrative text, section ordering/storytelling arc, plain-English interpretation. This is good. However, it could benefit from a pointer to a specific handoff template (to be added in my SOP).

3. **Standard Task Flow step 6** correctly notes that Ace assembles with input from steps 2 and 3. It also notes Ace can scaffold during steps 2-4. This is accurate.

4. **Minor addition suggested:** In the Acknowledgment Protocol section, note that Ace's acknowledgment of narrative text should confirm whether the layperson language is clear enough or needs revision. This is a unique quality dimension that other handoffs do not have.

---

## Summary of Action Items

| Item | Owner | Status |
|------|-------|--------|
| Add App Dev Handoff section to Research SOP | Ray | Doing now (Step 3) |
| Add Portal Narrative output format spec | Ray | Doing now (Step 3) |
| Add anti-pattern for undefined jargon in Ace deliverables | Ray | Doing now (Step 3) |
| Include Ace in event timeline handoff notifications | Ray | Doing now (Step 3) |
| Suggest intake template to Ace for narrative text | Ace | Suggestion filed |
| Suggest storytelling arc format to Ace | Ace | Suggestion filed |
| Update memories with cross-review onboarding norm | Ray | Doing now (Step 4) |

---
*Reviewed: 2026-02-28 -- Round 2 (Ace onboarding)*
