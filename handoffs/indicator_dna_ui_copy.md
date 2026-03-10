# Indicator DNA — UI Copy (for Streamlit)

Last updated: 2026-03-08  
Author: Evan (Economic & Quant Analyst)

Usage: Implement these fields on the Indicator DNA card. Each card should show:
- Identity type (chip)  
- Primary use case (chip)  
- Secondary use case (chip)  
- One-line description (bold or prominent)  
- "Why this classification" expandable text (short rationale)  
- Metadata: "Last updated: 2026-03-08 — Evan"

Format example (Streamlit):
Indicator title
[Identity chip] [Primary use case chip] [Secondary use case chip]
One-line description
Why this classification (expandable): one-sentence rationale

---  

Advance Retail Sales: Retail Trade  
Identity: Growth — Primary use case: Consumption gauge — Secondary: Inflation/Prices  
Description: Measures retail sales levels and momentum as a direct read on consumer demand.  
Why this classification: Retail sales are a core component of consumption and GDP; changes signal demand strength and can feed into goods inflation.

University of Michigan: Consumer Sentiment  
Identity: Growth — Primary use case: Demand forward signal — Secondary: Risk & Volatility  
Description: Survey of consumer attitudes that tends to lead spending behaviour.  
Why this classification: Sentiment surveys capture forward consumer intentions and can anticipate changes in consumption; they also reflect sentiment risk which can influence markets.

PHLX Semiconductor Sector Index  
Identity: Sector/Commodity/Structural — Primary use case: Sector cyclical indicator — Secondary: Growth  
Description: Equity index tracking semiconductor sector performance and cyclicality.  
Why this classification: Semiconductors are cyclically sensitive and correlate with tech capex and demand, making them a sector-level activity proxy.

ISM Manufacturing PMI  
Identity: Growth — Primary use case: Real activity monitor — Secondary: Inflation/Prices  
Description: Purchasing managers' survey for manufacturing activity and input prices.  
Why this classification: PMI components reflect production, new orders and input cost pressures—timely indicators of real activity and inflation.

ISM Services PMI  
Identity: Growth — Primary use case: Services activity gauge — Secondary: Inflation/Prices  
Description: Survey of services-sector activity, backlog and prices.  
Why this classification: Services PMI captures demand and price pressures in services—important for modern economies where services dominate GDP.

Gold Copper Ratio  
Identity: Risk/Commodity — Primary use case: Stagflation/stress signal — Secondary: Sector/Commodity  
Description: Ratio of gold to copper prices highlighting safe-haven vs cyclical commodity dynamics.  
Why this classification: Gold often reflects safety demand while copper tracks industrial demand—their ratio signals balance between safe-haven and cyclical forces.

Gold Silver Ratio  
Identity: Risk/Commodity — Primary use case: Safe-haven indicator — Secondary: Sector/Commodity  
Description: Relative pricing between gold and silver, often used as a liquidity/safety proxy.  
Why this classification: Shifts in precious metals relative valuation can reflect market risk appetite and liquidity preference.

New House Sale  
Identity: Sector/Housing — Primary use case: Housing demand — Secondary: Growth  
Description: Monthly measure of new single-family home sales—direct demand indicator for housing.  
Why this classification: New home sales directly reflect buyer demand and are sensitive to rates and consumer confidence.

Building Permits  
Identity: Sector/Housing — Primary use case: Future housing supply — Secondary: Growth  
Description: Authorisations for new residential construction—forward-looking supply metric.  
Why this classification: Permits lead starts and construction activity, indicating pipeline supply and future employment in construction.

(Continues for all indicators... file contains full set)

---  
Notes for Dada (implementation):
- Use `data/indicator_dna_cards.json` as the canonical source for card fields.  
- Expose chips as small UI badges; show description prominently and put the "Why this classification" text behind an expand/collapse.  
- Add metadata line: "Last updated" + author.  
- Allow Davis (Documentation) to edit phrasing if needed for tone.  

Notes for Chris (review):
- Verify factual accuracy and avoid overstating predictive power. Flag any item requiring qualification.  

Notes for Una (UI):
- Design compact desktop and condensed mobile layouts. Keep chips accessible and color-coded by identity type (consistent palette across app). Ensure expand control is obvious and readable.

