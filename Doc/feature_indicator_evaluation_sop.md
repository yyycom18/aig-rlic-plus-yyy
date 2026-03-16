# Feature SOP: Indicator Evaluation Components for Main Dashboard Integration

**Project:** aig-rlic-plus-yyy (YYY repository)
**Date:** 2026-03-08

---

## 1. Overview of the Indicator Evaluation Framework

This SOP describes three new evaluation components developed to explain financial indicators in the dashboard.
These components enable users to immediately understand each indicator’s economic classification, environment interaction, and strategy relevance—prior to exploring detailed research pages.
All components are implemented in the "apps" section at the top level of the indicator overview page (not inside story/evidence/strategy/methods pages). There is no impact on main dashboard structure or legacy research modules.

---

## 2. Component Descriptions

### 1️⃣ Indicator Identity & Use Case Layer
**Purpose:**
- Provides a standardized economic/financial identity (labeling system) for each indicator; functions as an indicator classification layer and will scale to the full indicator library.

#### Subcomponent A — Indicator Labeling System
- Assigns each indicator to a small taxonomy (e.g., "Credit & Financial Stress," "Relative Credit Premium," "Risk & Volatility").
- Used as color-coded badges in the dashboard UI.

#### Subcomponent B — Use Case Classification
- Displays the main intended use case(s) of the indicator:
  - **Primary Use Case:** Describes principal signal role (e.g., "Crisis risk reduction").
  - **Secondary Use Case:** Describes secondary/integration role (e.g., "Regime filter for equity allocation").

---

### 2️⃣ Environment Interaction Radar (Radar Visualization)
**Purpose:**
- Summarizes how the indicator behaves, aligns, or correlates with benchmark market environments (e.g., S&P 500, SPY).
- Provides instant visual evidence for user hypothesis generation.

**Radar Axes:**
- Correlation with benchmark
- Lead/Lag timing advantage
- Sensitivity to market stress
- Causality strength

**Data Sources:**
- Pipeline output including correlations, cross-correlation functions, stress analyses, and Granger/transfer entropy causality.

**UI/UX:**
- Evidence badge + expandable panel with full file provenance and analyst name/date
- Inline microcopy for “Why this score?” per axis
- Numeric summary for radar accessibility
- All mappings and calculation logic are visible in the evidence panel

---

### 3️⃣ Strategy Survival Radar (Radar Visualization)
**Purpose:**
- Assesses the viability of strategies built using this indicator (robustness, performance, deployability).
- Aggregates out-of-sample (OOS) tournament results for transparent, scenario-driven context.

**Radar Axes:**
- Return Advantage
- Sharpe Advantage
- Drawdown Control
- Consistency
- Deployability

**Data Source:**
- Tournament results: `results/tournament_results_YYYYMMDD.csv`
- Top-20 OOS Sharpe strategies are selected; axis values are medians among these strategies.

**UI/UX:**
- Displayed after Environment Radar in the overview workflow.
- Links into deeper strategy research modules (not replaced; supplements for storytelling context).

---

## 3. Data Sources & Calculation Logic
- Environment Radar: Calculated from evidence research pipeline outputs (see data pipeline for correlation, stress, and causality methods; exact mapping rules are JSON-auditable in results/).
- Strategy Radar: Aggregation (median) across Top-20 OOS Sharpe tournament strategies from results/ file; axes reflect performance and robustness, not a single strategy.
- Mapping rules, file paths, and calculation details are included in the provenance panel/JSON for each radar and indicator.

---

## 4. UI Placement in the Dashboard
- Component group is placed at the very top of each indicator overview (“apps”) page.
- Precedes (“floats above”) all subsections: story, evidence, strategy, and methodology.
- Serves as an orientation and visual summary to guide the user narrative from the outset.

---

## 5. Mapping to Main Repository Architecture
- No files or structure in main are affected by this feature in its staging form.
- The three components will later be integrated by:
  - Placing their code into the apps section of each indicator overview page in main
  - Ensuring existing research/evidence/strategy sections remain unchanged and accessible
  - Fully linking provenance and axis mapping logic to established data pipelines in the main branch
- All calculation logic and UI structure are modular and compliant for this eventual integration.

---

**[END SOP – Ready for product/development review and later integration into Main Dashboard repository.]**
