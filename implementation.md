# 🧠 IMPLEMENTATION.md — Canadian Linen LeadGen App

This document is the **master implementation brief** for Cursor. It defines the full app logic, architecture, scoring model, and module behavior. Cursor should use this as the source of truth and refer to the already created files in the repo before generating anything new.

---

## 🎯 OBJECTIVE
Build a Streamlit web application that allows Account Executives at Canadian Linen to generate, score, and act on leads based on NAICS + regulatory compliance triggers.

---

## ⚙️ CORE FUNCTIONALITY
1. User inputs postal code + industry keyword + coordinates.
2. App queries Google Places + Calgary Business Registry.
3. Merges, deduplicates, and classifies leads using NAICS.
4. Scores leads using regulatory pressure, data confidence, and zone density.
5. Tags each lead with AWRV potential and cold call script.
6. Displays table with download/export and Google Maps links.

---

## 🧱 FILE ARCHITECTURE (PRE-EXISTING)
```
/leadgen-app/
├── app.py                         # Streamlit frontend UI
├── .env                           # API keys
├── requirements.txt               # Python deps
├── data/
│   └── naics_keywords.json        # NAICS → Compliance reference
├── utils/
│   ├── google_scraper.py          # Pulls from Google Places API
│   ├── registry_fetcher.py        # Queries Calgary Biz Registry
│   ├── lead_merger.py             # Fuzzy match + combine sources
│   ├── lead_scorer.py             # Scores based on formula
│   ├── stats_mapper.py            # Returns postal zone density
│   └── cold_call_generator.py     # Builds tailored scripts
```

---

## 🔄 DATA SOURCES (USED IN EXISTING MODULES)
- Google Places (via keyword + lat/long)
- Calgary Business Registry API (postal → business data)
- Simulated StatsCan NAICS x Postal density (in `stats_mapper.py`)

---

## 📊 LEAD SCORING MODEL (IN `lead_scorer.py`)
```python
score = (compliance_score * 2) + source_match_count + zone_density_score
```
- Compliance score is from mapped regulation severity
- Source match count = how many data sources the lead appeared in
- Zone density is based on business count in postal x NAICS

---

## 🔑 NAICS COMPLIANCE MAPPING (USED IN `naics_keyword_map.py`)
- Industry keywords mapped to NAICS
- NAICS linked to: industry name, compliance tags, recommended garments
- Lives in `data/naics_keywords.json`

---

## 🧠 COLD CALL SCRIPT LOGIC (IN `cold_call_generator.py`)
- CSA → construction/electric
- HACCP → food & processing
- NFPA → fire, FR gear
- Else → Default pitch based on industry

---

## 🧩 USAGE FLOW (IN `app.py`)
1. User enters keyword + location + postal
2. Triggers `google_scraper` and `registry_fetcher`
3. Merges via `lead_merger`
4. Scores via `lead_scorer`
5. Tags via `cold_call_generator`
6. Renders table, download CSV, maps

---

## 📋 OUTPUT FIELDS (IN FINAL TABLE)
| Field | Source | Notes |
|-------|--------|-------|
| business_name | merged | Legal/trade name |
| address | merged | Full address |
| postal_code | registry | Needed for routing |
| industry | NAICS | From keyword mapping |
| compliance | JSON map | CSA, HACCP, etc. |
| naics_code | classifier | From trigger keywords |
| awrv_tier | estimated | High/Med/Low |
| score | calc | Composite value |
| Cold Call Script | generated | Compliance-based script |
| Google Maps Link | geolink | Walk-in tool |

---

## ✅ MODULE GUIDELINES
- All scraping lives in `/utils`
- API keys pulled from `.env`
- Never regenerate existing modules unless explicitly modified
- UI must call these modules only — not re-implement logic inline

---

## 🧼 DEPLOYMENT TARGET
- Streamlit Cloud
- AE-friendly, zero terminal required
- Mobile/tablet-friendly layout

---

## 🔁 NEXT STEPS
Cursor should now:
- Refer to this file before building any new feature
- Only generate new files if not present
- Use naics_keywords.json and utils modules as canonical logic sources
- Treat `app.py` as the interactive shell and final destination

This file replaces long inline prompts and is to be used as Cursor’s implementation base.
