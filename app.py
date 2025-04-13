import streamlit as st
import pandas as pd
from utils.google_scraper import GooglePlacesScraper
from utils.registry_fetcher import CalgaryRegistryFetcher
from utils.lead_merger import LeadMerger
from utils.lead_scorer import LeadScorer
from utils.stats_mapper import StatsMapper
from utils.cold_call_generator import ColdCallGenerator
import requests

# App Configuration
st.set_page_config(page_title="Canadian Linen LeadGen", layout="wide")
st.title("🧼 Canadian Linen - Compliance-Based Lead Generator")

# Sidebar Controls
st.sidebar.header("🔍 Lead Generation Controls")
postal_code = st.sidebar.text_input("Postal Code Prefix (e.g. T1Y)", value="T1Y")
industry_keyword = st.sidebar.text_input("Industry Keyword (e.g. electrical contractor)", value="electrical contractor")
latitude = st.sidebar.text_input("Latitude (e.g. 51.0447)", value="51.0447")
longitude = st.sidebar.text_input("Longitude (e.g. -114.0719)", value="-114.0719")
generate_btn = st.sidebar.button("🚀 Generate Lead List")

# Initialize Modules - Wrap in try-except for potential API key issues
try:
    google_scraper = GooglePlacesScraper()
    registry_fetcher = CalgaryRegistryFetcher()
except ValueError as e:
    st.error(f"🚨 Initialization Error: {e}. Please ensure the GOOGLE_API_KEY is set correctly in Streamlit secrets.")
    st.stop() # Stop execution if initialization fails

merger = LeadMerger()
scorer = LeadScorer()
stats_mapper = StatsMapper()
script_gen = ColdCallGenerator()

# Generate Leads and Display Table
if generate_btn:
    st.info("Collecting, merging, and scoring leads... please wait ⏳")

    try:
        # Scraping phase
        google_leads = google_scraper.search_businesses(industry_keyword, f"{latitude},{longitude}")
        registry_leads = registry_fetcher.fetch_by_postal(postal_code)

        # Merge & Deduplicate
        combined_leads = merger.merge(google_leads, registry_leads)

        # Check if leads were found
        if not combined_leads:
            st.warning(f"⚠️ No leads found for '{industry_keyword}' in postal code prefix '{postal_code}'. Try broadening your search criteria.")
            st.stop()

        # Score & Tag
        for lead in combined_leads:
            zone_density = stats_mapper.get_density_score(lead.get("postal_code", postal_code), lead.get("naics_code", ""))
            scorer.score_lead(lead, zone_density_score=zone_density)
            lead["Cold Call Script"] = script_gen.generate(lead)
            lead["Google Maps Link"] = lead.get("maps_link")

        # Convert to DataFrame
        df = pd.DataFrame(combined_leads)

        # Define columns, ensuring essential ones exist even if some are missing
        base_cols = ["business_name", "address", "postal_code", "industry", "compliance", "naics_code", "awrv_tier", "score", "Cold Call Script", "Google Maps Link"]
        display_cols = [col for col in base_cols if col in df.columns]

        st.success(f"✅ Generated {len(df)} leads in {postal_code} for '{industry_keyword}'")
        st.dataframe(df[display_cols], use_container_width=True)

        # Download CSV
        csv_data = df.to_csv(index=False).encode('utf-8') # Ensure UTF-8 encoding
        st.download_button(
            label="📥 Download CSV File",
            data=csv_data,
            file_name=f"leads_{postal_code}_{industry_keyword}.csv",
            mime="text/csv"
        )

        # Optional Walk-In Links (check if column exists and has valid links)
        if "Google Maps Link" in df.columns and df["Google Maps Link"].notna().any():
             with st.expander("🗺️ View Walk-In Route Links"):
                for link in df["Google Maps Link"].dropna():
                    st.markdown(f"[Open in Google Maps]({link})")

    except requests.exceptions.RequestException as e:
        st.error(f"🚨 Network Error: Could not connect to external APIs. Please check your internet connection and try again. Details: {e}")
    except Exception as e: # Catch other potential errors during processing
        st.error(f"🚨 An unexpected error occurred: {e}")

else:
    st.markdown("👈 Enter a postal prefix and keyword to generate your custom lead list.")
