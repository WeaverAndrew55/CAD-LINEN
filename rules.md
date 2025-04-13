# 📋 RULES.md — Canadian Linen LeadGen App

These are the internal rules and standards to be followed when maintaining, extending, or deploying this application.

---

## ⚙️ App Functionality Rules
1. All outbound leads must be classified by NAICS and tagged with a relevant compliance need (CSA, HACCP, NFPA, etc).
2. No cold script should be generated without knowing the compliance need.
3. Google Places and Calgary Business Registry data must be merged and deduplicated before a lead is considered valid.
4. Scoring logic must follow this formula (unless explicitly changed):
```python
score = (compliance_score * 2) + source_match_count + zone_density_score
```
5. AWRV tiers must be estimated using NAICS-industry mapping and remain consistent with the targeting sheet.

---

## 🧱 Development & Structure Rules
1. All major functions must be modular (utils folder), not embedded in `app.py`.
2. API keys must **never** be hardcoded. Always use `.env`.
3. All new compliance types must be added to `naics_keywords.json` with corresponding keywords.
4. Use `requirements.txt` to track all external Python dependencies.
5. Any updates to NAICS logic must preserve backward compatibility with existing code.

---

## 💼 UI/UX Principles
1. UI must remain simple, readable, and mobile-friendly.
2. Lead tables must always show: business name, industry, postal code, compliance tag, score.
3. Cold call scripts must be directly accessible per lead.
4. Download buttons and map links must be highly visible.
5. Never block the user from generating leads due to minor missing data (fallbacks allowed).

---

## ☁️ Deployment Rules
1. App must always be deployable via Streamlit Cloud with one-click setup.
2. GitHub repo must always include README.md, CONTEXT.md, RULES.md, and setup instructions.
3. `.env` values must be added to Streamlit secrets (never uploaded to GitHub).
4. The app must remain usable by non-technical salespeople — zero terminal commands post-deploy.

---

## 🔒 Security & Privacy
1. No personal data should be stored, cached, or exported.
2. Do not store enriched lead data beyond local session.
3. All external API use must comply with terms of service.

---

Failure to follow these rules may result in bad data, poor targeting, broken compliance logic, or app downtime. Maintain with care.

Built to support high-output Account Executives. Close fast, stay sharp.
