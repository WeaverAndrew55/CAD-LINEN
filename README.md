# 🧼 Canadian Linen - Compliance-Based Lead Generator

This is a web-based, professional-grade lead generation app built for Account Executives at **Canadian Linen Services**. It generates high-priority business leads based on **regulatory compliance requirements** (CSA, HACCP, NFPA, etc.), industry type, and geography.

Built using **Streamlit + Python**, this tool enables rapid outbound execution via cold calls, emails, and in-person walk-ins.

---

## 🚀 Features
- Generate leads based on postal code + industry keyword
- Pulls from Google Places + Calgary Business Registry
- Merges, de-duplicates, and scores leads
- Tags leads with NAICS code, industry, compliance need, and estimated AWRV
- Auto-generates cold call scripts
- Google Maps links for walk-in targeting
- CSV download of the full lead list

---

## 📦 Project Structure
```
leadgen-app/
├── app.py                        # Streamlit web app interface
├── requirements.txt              # Project dependencies
├── .env                          # API keys
├── data/
│   └── naics_keywords.json       # Industry keyword + compliance map
├── utils/
│   ├── google_scraper.py
│   ├── registry_fetcher.py
│   ├── lead_merger.py
│   ├── lead_scorer.py
│   ├── stats_mapper.py
│   └── cold_call_generator.py
├── README.md
└── CONTEXT.md                    # Full project vision + architecture
```

---

## 🔧 Setup Instructions
1. Clone this repository
```bash
git clone https://github.com/your_username/leadgen-app
cd leadgen-app
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Add your API keys to `.env`
```
GOOGLE_API_KEY=your_google_places_key
LEADMAGIC_API_KEY=optional_enrichment_key
```

5. Run the app
```bash
streamlit run app.py
```

---

## ☁️ Hosting Instructions (Streamlit Cloud)
- Push your code to a public or private GitHub repo
- Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
- Click **"New app"** → Link your GitHub → Point to `app.py`
- Add your `.env` values under **"Secrets"**
- Deploy 🚀

---

## 🧠 Recommended Use
- Every Monday: Run a **Postal Blitz** by postal code + vertical
- Download CSV → Start calling & walking in
- Update CRM or Tracker with pipeline statuses
- Close that $300/week AWRV target 💰

---

## 👨‍💻 Developer Notes
This project is modular and designed to scale:
- Add more NAICS compliance logic in `naics_keywords.json`
- Replace simulated density scores with real StatsCan API integration
- Future integrations: HubSpot, Gmail, Outlook, Enrichment APIs

For questions, support, or contributions, open an issue or fork this repo.

---

## 📣 Built for Canadian Linen AEs. Outbound domination, data-first. Let’s go.
