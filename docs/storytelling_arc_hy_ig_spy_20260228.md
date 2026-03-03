# Storytelling Arc: HY-IG Credit Spread vs S&P 500 Returns

**From:** Ray (Research Agent)
**To:** Ace (App Dev), Alex (Lead)
**Date:** 2026-02-28

---

**Hook:** "The bond market saw the 2008 crash coming months before stocks collapsed."

**Thesis:** Credit spreads — the gap between risky and safe bond yields — contain early warning signals for equity investors, but the signal is regime-dependent, nonlinear, and most powerful precisely when it is most needed: during periods of financial stress.

**Audience:** Layperson / institutional investor

**Reading time target:** 5 minutes for Pages 1-2, 15 minutes for all 5 pages

---

## Arc Structure

### 1. The Hook (Page 1 — Executive Summary)

**Grabber:** "In mid-2007, while stock markets were reaching all-time highs and Wall Street was celebrating record profits, something quiet was happening in the bond market. The cost of insuring risky corporate debt had begun climbing steadily — a signal that bond investors were getting nervous about something stock investors had not yet noticed. Five months later, the stock market began its worst crash since the Great Depression."

**Purpose:** Immediately establish that the bond market carries predictive information that equity markets miss. Create curiosity: *Why does this happen? Can we use it?*

**KPI cards** give the audience concrete numbers to anchor the narrative: credit led equity by ~5 months in 2008; spreads moved from 300 to 2,000+ bps; the signal predicted 3 of 4 major drawdowns.

### 2. The Context (Page 2 — The Story)

**Core narrative:** Explain *why* credit and equity markets are connected but process information differently. Three layers:

- **Layer 1 — The basics:** What credit spreads are, why they exist, and why they move. (Accessible to anyone.)
- **Layer 2 — The asymmetry:** Why bond investors are structurally more attuned to risk than stock investors. Bond investors can only lose principal; stock investors can profit from growth. This creates an asymmetry where credit markets are faster to detect deterioration.
- **Layer 3 — The informed trading channel:** Banks that lend to companies have private information. When they start hedging in credit markets, spread movements can precede equity moves.

**Historical walk-through:** Four episodes (dot-com bust, GFC, COVID, 2022 rate shock) told as mini-stories, each illustrating a different facet of the credit-equity relationship.

**Key insight:** The relationship is not constant — it changes depending on the regime. During calm markets, stocks lead bonds. During stress, bonds lead stocks. This is why simple trading rules fail.

### 3. The Evidence (Page 3 — Analytical Detail)

**Bridge from story to data:** "These patterns are not just historical anecdotes. We subjected 25 years of daily data to rigorous statistical testing — and the results confirm that credit spreads carry genuine predictive information for stock returns, especially during stress periods."

**What we show:**
- Causality tests confirm bidirectional information flow, with credit-to-equity strengthening during stress.
- Impulse responses show that a credit spread shock predicts negative stock returns that build over 1-5 weeks.
- Regime models identify distinct "stress" and "calm" states with fundamentally different dynamics.
- The signal's predictive power is concentrated in the left tail of the return distribution — it warns of bad outcomes, not good ones.

**Tournament results:** "We tested over 1,000 different strategy combinations to find the most robust way to translate the credit signal into an actionable equity strategy."

### 4. The Implication (Page 4 — Strategy)

**Bridge:** "So what should an investor do with this information?"

**Core message:** Credit spreads are most useful as a **risk management tool** — a way to reduce equity exposure when financial conditions deteriorate, rather than a high-frequency trading signal. The strategy is conceptually simple: stay invested when credit conditions are normal, reduce exposure when they are stressed.

**Practical details:** Strategy rules stated in plain English. Performance metrics compared to buy-and-hold. Caveats clearly stated (transaction costs, execution delay, past performance).

**Honest assessment:** The signal does not work every time. It is not a crystal ball. But for investors who want to improve their risk-adjusted returns by paying attention to what the bond market is saying, it provides a disciplined, evidence-based framework.

### 5. The Method (Page 5 — Technical Appendix)

**Bridge:** "For the skeptical reader — and healthy skepticism is essential in finance — here is exactly how we arrived at these conclusions."

**What we show:** Data sources with exact identifiers. Econometric methods with citations. Diagnostic tests confirming model validity. Sensitivity analysis showing robustness (and where results are fragile). Full reference list.

**Tone shift:** This page is more technical than the others, written for the reader who wants to verify the work. It serves as a trust anchor — proof that the accessible story told on Pages 1-4 rests on rigorous methodology.

---

## Key Transitions

### Page 1 to Page 2
"These numbers tell a compelling story, but to understand *why* credit spreads carry this predictive power — and when the signal works vs. when it doesn't — we need to look deeper into how bond and stock markets are connected."

### Page 2 to Page 3
"History suggests a real connection, but anecdotes are not evidence. We subjected 25 years of daily data to a battery of statistical tests to separate genuine predictive power from coincidence."

### Page 3 to Page 4
"The statistical evidence confirms that credit spreads carry genuine predictive information for stock returns. The practical question is: can investors use this signal to improve their outcomes?"

### Page 4 to Page 5
"For readers who want to understand exactly how we reached these conclusions — or who want to replicate and extend the analysis — the methodology section provides full details on data, methods, and diagnostics."

---

## Narrative Design Notes for Ace

1. **Progressive disclosure:** Each page goes deeper. Page 1 is headlines. Page 2 is the story. Page 3 is the evidence. Page 4 is the strategy. Page 5 is the proof. Readers can stop at any point and still have a complete (if less detailed) understanding.

2. **Expander blocks:** Used in Page 2 for technical definitions (credit spreads, Merton model, regimes, quality spread) and in Page 4 for z-score definition. These should be `st.expander()` components — visible only when clicked.

3. **Tone calibration:** Pages 1-2 are conversational and jargon-free. Page 3 bridges to semi-technical. Page 4 returns to practical. Page 5 is fully technical. The glossary (bottom of Page 2 or a sidebar tab) defines every technical term used.

4. **Visual anchors:** Every section should have at least one chart or metric card. The hero chart on Page 1 (dual-axis spread vs. SPY) is the most important single visual. Page 3 should feature impulse response plots and regime probability timelines. Page 4 should show strategy equity curves.

5. **Color coding:** Suggest using a consistent color palette where orange/red = credit stress / spread widening and blue = equity market. NBER recessions in gray shading. This creates visual consistency across all charts.
