import streamlit as st
import pandas as pd
from utils.google_scraper import GooglePlacesScraper
from utils.registry_fetcher import CalgaryRegistryFetcher
from utils.lead_merger import LeadMerger
from utils.lead_scorer import LeadScorer
from utils.stats_mapper import StatsMapper
from utils.cold_call_generator import ColdCallGenerator
import requests
from utils.naics_keyword_map import NAICSKeywordMap
from datetime import datetime

# App Configuration
st.set_page_config(page_title="Canadian Linen LeadGen", layout="wide")
st.title("🧼 Canadian Linen - Compliance-Based Lead Generator")

# Initialize NAICS Map
naics_mapper = NAICSKeywordMap()

# Sidebar Controls
st.sidebar.header("📍 Territory Selection")
postal_codes_input = st.sidebar.text_input("Postal Code Prefixes (comma-separated, e.g. T1Y, T2A)", value="T1Y")
latitude = st.sidebar.text_input("Center Latitude (for Google Search)", value="51.0447")
longitude = st.sidebar.text_input("Center Longitude (for Google Search)", value="-114.0719")

st.sidebar.header("🏭 Industry Selection")
industry_options = naics_mapper.get_display_options()
selected_industries = st.sidebar.multiselect(
    "Select Target Industries/Compliance:",
    options=industry_options,
    default=None # Or set a default if needed
)

st.sidebar.header("🚀 Generate")
generate_btn = st.sidebar.button("Generate Lead List")

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

    # --- Input Validation ---
    # Parse postal codes
    postal_prefixes = [p.strip().upper() for p in postal_codes_input.split(',') if p.strip()]
    if not postal_prefixes:
        st.error("🚨 Please enter at least one valid postal code prefix.")
        st.stop()

    # Validate selected industries
    if not selected_industries:
        st.error("🚨 Please select at least one industry.")
        st.stop()

    # --- Prepare Search Keywords from selected industries ---
    google_search_keywords = []
    for option in selected_industries:
        details = naics_mapper.get_details_from_display_option(option)
        if details and details.get('keywords'):
            google_search_keywords.extend(details['keywords'])
    # Use unique keywords, join them for Google search (or search iteratively?)
    # For simplicity, let's combine unique keywords or use the first selection's keywords
    # Taking keywords from the first selected industry for now:
    first_selection_details = naics_mapper.get_details_from_display_option(selected_industries[0])
    search_keyword_string = " ".join(first_selection_details.get('keywords', [selected_industries[0]])) if first_selection_details else selected_industries[0]

    st.info("Collecting, merging, and scoring leads... please wait ⏳")

    try:
        # Scraping phase
        st.write(f"Searching Google for: '{search_keyword_string}' near {latitude},{longitude}")
        google_leads = google_scraper.search_businesses(search_keyword_string, f"{latitude},{longitude}")

        st.write(f"Searching Calgary Registry for postal prefixes: {', '.join(postal_prefixes)}")
        registry_leads = registry_fetcher.fetch_by_postal(postal_prefixes) # Pass the list

        # Merge & Deduplicate
        combined_leads = merger.merge(google_leads, registry_leads)

        # Check if leads were found
        if not combined_leads:
            st.warning(f"⚠️ No leads found for '{search_keyword_string}' in postal code prefix '{postal_prefixes[0]}'.")
            st.stop()

        # Score & Tag
        for lead in combined_leads:
            # Find the best matching selected NAICS code for scoring/tagging
            lead_text = f"{lead.get('business_name', '')} {lead.get('industry', '')}"
            matched_naics = naics_mapper.guess_naics_from_text(lead_text)
            lead['naics_code'] = matched_naics[0] if matched_naics else lead.get('naics_code') # Update NAICS if found
            lead['industry'] = matched_naics[1] if matched_naics else lead.get('industry') # Update industry if found

            zone_density = stats_mapper.get_density_score(lead.get("postal_code", postal_prefixes[0]), lead.get("naics_code", "")) # Use first postal for density if needed
            scorer.score_lead(lead, zone_density_score=zone_density)
            lead["Cold Call Script"] = script_gen.generate(lead) # Script relies on lead['compliance'] tag from scorer/merger
            lead["Google Maps Link"] = lead.get("maps_link")

        # Convert to DataFrame
        df = pd.DataFrame(combined_leads)

        # Define columns, ensuring essential ones exist even if some are missing
        base_cols = ["business_name", "address", "postal_code", "industry", "compliance", "naics_code", "awrv_tier", "score", "Cold Call Script", "Google Maps Link"]
        display_cols = [col for col in base_cols if col in df.columns]

        st.success(f"✅ Generated {len(df)} leads in {', '.join(postal_prefixes)} for selected industries")
        st.dataframe(df[display_cols], use_container_width=True)

        # Download CSV
        csv_data = df.to_csv(index=False).encode('utf-8') # Ensure UTF-8 encoding
        download_filename = f"leads_{'_'.join(postal_prefixes)}_{datetime.now().strftime('%Y%m%d')}.csv"
        st.download_button(
            label="📥 Download CSV File",
            data=csv_data,
            file_name=download_filename,
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
    st.markdown("👈 Select territory and industry filters to generate your custom lead list.")
