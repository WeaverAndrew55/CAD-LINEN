# 📘 CONTEXT.md — Canadian Linen Lead Gen App (Ultimate Edition)

---

## 🧠 PROJECT OVERVIEW

This is a web-based, outbound lead generation and territory management tool designed for **field Account Executives at Canadian Linen**. It is optimized to help reps discover, prioritize, and convert businesses that require uniform and facility services due to **compliance regulations** like **CSA Z96, NFPA 70E/2112, CAT 2/3, HACCP, and GMP**.

The tool leverages multiple data sources (Google Places, Calgary Business Registry, StatsCan) to score, sort, and serve actionable leads that can be used in cold calls, walk-ins, or email outreach.

---

## 🧑‍💼 USER PROFILE
- Role: Account Executive (AE)
- Company: Canadian Linen Services
- Goal: Book accounts that generate at least **$300/week in Average Weekly Rental Volume (AWRV)**
- Tactics: Cold calling, walk-ins, and outbound email
- Territory: Calgary, Alberta — defined by a list of postal codes

---

## 🎯 PROJECT GOALS
- Discover compliance-sensitive businesses by NAICS verticals
- Prioritize based on compliance urgency, business legitimacy, and revenue potential
- Blitz local zones weekly for outbound efficiency
- Auto-generate personalized cold call/email scripts
- Track pipeline status (To Call, Walked In, Quoted, Closed)
- Export leads to CSV and view on Google Maps

---

## 🛠️ TECH STACK
| Layer | Technology | Notes |
|-------|------------|-------|
| Frontend | Streamlit | Fast prototyping, low-code UI |
| Backend | Python | Scraping, scoring, enrichment |
| Hosting | Streamlit Cloud + GitHub | Free tier + rapid deployment |
| APIs | Google Places API, Calgary Business Registry API, StatsCan | Core data sources |
| Enrichment | (Optional) LeadMagic API | Contact data enrichment |

---

## 📁 FILE STRUCTURE
```
/leadgen-app/
├── app.py                          # Streamlit app UI
├── requirements.txt                # Python dependencies
├── .env                            # API keys
├── utils/
│   ├── google_scraper.py           # Google Places queries
│   ├── registry_fetcher.py         # Pulls from Calgary Registry API
│   ├── naics_keyword_map.py        # Maps NAICS to search keywords + compliance
│   ├── lead_merger.py              # Deduplication and match logic
│   ├── lead_scorer.py              # Compliance + AWRV scoring logic
│   └── stats_mapper.py             # Pulls StatsCan business counts per postal/NAICS
├── data/
│   └── naics_keywords.json         # Human-friendly NAICS dictionary
├── README.md
├── project_rules.md
└── setup_steps.md
```

---

## 🔌 API KEYS FORMAT (.env)
```env
GOOGLE_API_KEY=your_google_key
LEADMAGIC_API_KEY=your_leadmagic_key (optional)
```

---

## 🔎 DATA SOURCES USED
| Source | Type | Use Case |
|--------|------|----------|
| Google Places API | Live | Real-world visibility, keywords |
| Calgary Business Registry | Public API | Verified business registrations |
| StatsCan NAICS Counts | CSV/API | Postal zone prioritization by industry density |

---

## 📊 NAICS TO COMPLIANCE TARGETING (FINALIZED STRATEGY)
We created a comprehensive NAICS-to-Compliance Targeting Sheet that maps:
- NAICS code → Industry keyword matches
- Compliance tags → CSA, NFPA, HACCP, CAT levels
- Estimated AWRV tier → Low / Medium / High
- Common trigger phrases for cold call personalization

This sheet is critical to:
- Search queries
- Lead classification
- Script generation
- Scoring

Stored in: `naics_keyword_map.py` and `naics_keywords.json`

---

## ⚖️ LEAD SCORING FORMULA (CONFIRMED)
```python
score = (
    (compliance_score * 2) + 
    source_match_count + 
    zone_density_score
)
```
- **Compliance Score**: 1–5 based on regulatory pressure
- **Source Match**: How many datasets the lead appears in (1–3)
- **Zone Density**: Derived from StatsCan (business concentration)

---

## 💼 OUTPUT FIELDS PER LEAD
| Field | Description |
|-------|-------------|
| Business Name | From Registry or Google |
| Address | Full address with postal code |
| Phone | Best phone from Registry/Google |
| Website | If available |
| Postal Code | Used for zone blitzing |
| Industry | Based on NAICS guess |
| NAICS | Matched via keywords |
| Compliance Tag | CSA Z96, NFPA 2112, etc. |
| AWRV Tier | Low / Medium / High |
| Source Count | 1–3 (Google, Registry, StatsCan) |
| Composite Score | 1–10 for lead priority |
| Google Maps Link | Auto-generated for walk-ins |
| Status | To Call, Walked In, Quoted, Closed |

---

## 🧠 SCRIPT GENERATION (COLD CALL + EMAIL)
Scripts are generated based on:
- Industry vertical (NAICS)
- Compliance tag (CSA / HACCP / FR / CAT)
- Trigger phrases from targeting sheet

Examples:
```text
"Hi, this is [Name] with Canadian Linen—I help food processors stay HACCP-aligned with weekly uniform delivery and compliance tracking. Who currently manages your facility compliance gear?"
```

---

## 🧭 USER FLOW (START TO FINISH)
1. AE logs into web app
2. Selects postal codes and NAICS verticals
3. App pulls Google + Registry + StatsCan data
4. Leads are merged, scored, tagged with compliance
5. AE views sortable table and script generator
6. AE downloads CSV or opens maps for walk-ins
7. Tracks lead status internally (To Call, In Progress, Quoted, Closed)

---

## 🎛️ UI STRUCTURE (Streamlit Frontend)
- **Sidebar**
  - Postal selector
  - NAICS selector
  - Compliance filters (CSA, HACCP, FR)
  - Generate Lead List
- **Main Panel**
  - Lead results table
  - Expandable script box
  - Download CSV, Open Map
- **Status column** to update lead tracking

---

## 📋 MUST-HAVE FEATURES
| Feature | Description |
|---------|-------------|
| Blitz Mode | Target one postal zone + vertical per week |
| Cold Script Generator | Uses compliance tags and industry terms |
| Multi-Source Merger | Confidence rating based on Google + Registry |
| Route Planner | Walk-in clustering based on Maps links |
| Score Sorter | Lead priority list (AWRV + compliance urgency) |
| Follow-Up Tracker | Pipeline logic inside app |

---

## 📈 AWRV TIER ESTIMATES (FOR SCORING)
| Business Type | Est. AWRV |
|---------------|------------|
| Auto Shop | $60–80/wk |
| Food Processor | $100–150/wk |
| Electrical Contractor | $200+/wk |
| Chemical Facility | $300+/wk |

---

## ✅ DEPLOYMENT & USAGE
- Hosted on GitHub
- Deployed on Streamlit Cloud
- No CLI required for end user
- Ready for AE use on laptop, mobile, or tablet

---

## 🔧 MODULE BUILD ORDER
1. `naics_keyword_map.py`
2. `google_scraper.py`
3. `registry_fetcher.py`
4. `lead_merger.py`
5. `lead_scorer.py`
6. `stats_mapper.py`
7. `cold_call_generator.py`
8. `route_optimizer.py` (optional)

---

This file is your full master blueprint. Cursor should treat this as its **source of truth** for structure, logic, user behavior, and output formatting.
