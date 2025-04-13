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
import time # For potential delays or spinners
import re # For extracting postal codes

# --- App Configuration ---
st.set_page_config(page_title="Canadian Linen LeadGen", layout="wide")
st.title("🧼 Canadian Linen - Compliance-Based Lead Generator")

# --- Initialize Modules ---
# Wrap in try-except for potential API key issues or file not found
try:
    naics_mapper = NAICSKeywordMap()
    google_scraper = GooglePlacesScraper()
    registry_fetcher = CalgaryRegistryFetcher()
    merger = LeadMerger()
    scorer = LeadScorer()
    stats_mapper = StatsMapper()
    script_gen = ColdCallGenerator()
except ValueError as e:
    st.error(f"🚨 Initialization Error: {e}. Please ensure the GOOGLE_API_KEY is set correctly in Streamlit secrets.")
    st.stop()
except FileNotFoundError as e:
     st.error(f"🚨 Initialization Error: {e}. Ensure 'data/naics_keywords.json' exists.")
     st.stop()
except Exception as e:
     st.error(f"🚨 An unexpected error occurred during initialization: {e}")
     st.stop()


# --- Helper Function for Postal Code Extraction ---
def extract_postal_code(address):
    if not isinstance(address, str):
        return None
    # Canadian Postal Code Regex (allows for formats like T2X 1Y4 or T2X1Y4)
    match = re.search(r'[ABCEGHJKLMNPRSTVXY]\d[A-Z]\s?\d[A-Z]\d', address.upper())
    return match.group(0).replace(" ", "") if match else None # Return normalized (no space)

# --- Cached Data Loading and Classification Function ---
@st.cache_data(ttl=3600, show_spinner="Fetching and classifying businesses in territory...") # Cache for 1 hour
def load_and_classify_leads(_postal_prefixes, _location):
    """
    Fetches leads from Google (broadly) and Registry, merges them,
    classifies using NAICS map, and returns a DataFrame.
    Underscores in args tell Streamlit cache to ignore them if they are mutable lists/dicts.
    """
    print(f"CACHE MISS: Loading data for postal prefixes: {_postal_prefixes}, location: {_location}") # Log cache miss
    google_leads = []
    registry_leads = []
    try:
        # Google Scraping (Broad) - Radius can be adjusted
        google_leads = google_scraper.search_businesses_broadly(_location, radius=10000) # Using the new broad search
        st.write(f"Found {len(google_leads)} potential leads from Google.") # Progress update

        # Registry Fetching
        registry_leads = registry_fetcher.fetch_by_postal(_postal_prefixes)
        st.write(f"Found {len(registry_leads)} potential leads from Calgary Registry.") # Progress update

    except requests.exceptions.RequestException as e:
        st.error(f"🚨 Network Error during data fetching: {e}. Please check connection and API keys.")
        return pd.DataFrame() # Return empty DataFrame on error
    except Exception as e:
        st.error(f"🚨 Error during data fetching: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

    # Merge & Deduplicate
    st.write("Merging and deduplicating leads...")
    combined_leads = merger.merge(google_leads, registry_leads)
    st.write(f"Total unique leads after merging: {len(combined_leads)}")

    if not combined_leads:
        st.warning("⚠️ No leads found for the specified territory.")
        return pd.DataFrame()

    # Classify, Add Compliance, and Extract Postal Codes
    st.write("Classifying leads by industry (NAICS)...")
    processed_leads = []
    for lead in combined_leads:
        # Ensure essential fields exist
        lead_text = f"{lead.get('business_name', '')} {lead.get('address', '')}"
        naics_code, industry, compliance_tags = naics_mapper.guess_naics_from_text(lead_text)

        lead['naics_code'] = naics_code
        lead['industry'] = industry if industry else "Unknown" # Default to Unknown if None
        # Get additional details based on guessed NAICS
        naics_details = naics_mapper.get_details_from_naics(naics_code) if naics_code else None
        lead['compliance'] = naics_details.get('compliance', []) if naics_details else [] # Store as list
        lead['awrv_tier'] = naics_details.get('awrv_tier', 'Unknown') if naics_details else 'Unknown'

        # Standardize/Extract Postal Code
        if 'postal_code' not in lead or not lead['postal_code']:
             lead['postal_code'] = extract_postal_code(lead.get('address',''))

        processed_leads.append(lead)

    df = pd.DataFrame(processed_leads)
    # Ensure key columns exist, even if empty after processing
    required_cols = ["business_name", "address", "postal_code", "industry", "compliance", "naics_code", "awrv_tier", "maps_link", "source"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None if col != 'compliance' else pd.Series([[] for _ in range(len(df))]) # Initialize compliance as empty list

    return df


# --- Sidebar Controls ---
st.sidebar.header("📍 Territory Selection")
postal_codes_input = st.sidebar.text_input("Postal Code Prefixes (comma-separated, e.g. T1Y, T2A)", value="T1Y,T2A") # Example default
try:
    default_lat, default_lon = "51.0447", "-114.0719" # Calgary defaults
    latitude = st.sidebar.text_input("Center Latitude (for Google Search)", value=default_lat)
    longitude = st.sidebar.text_input("Center Longitude (for Google Search)", value=default_lon)
    # Validate lat/lon format (simple check)
    location = f"{float(latitude):.4f},{float(longitude):.4f}"
except ValueError:
     st.sidebar.error("🚨 Invalid Latitude/Longitude format. Please enter numbers.")
     st.stop()


st.sidebar.header("🚀 Load Territory Data")
generate_btn = st.sidebar.button("Load Businesses in Territory")

# Initialize session state for loaded data and filters if they don't exist
if 'all_leads_df' not in st.session_state:
    st.session_state.all_leads_df = pd.DataFrame()
if 'selected_industries_filter' not in st.session_state:
    st.session_state.selected_industries_filter = []
if 'selected_compliance_filter' not in st.session_state:
    st.session_state.selected_compliance_filter = []
if 'selected_postal_filter' not in st.session_state:
    st.session_state.selected_postal_filter = []
if 'loaded_postal_prefixes' not in st.session_state:
    st.session_state.loaded_postal_prefixes = []


# --- Load Data Logic ---
if generate_btn:
    # --- Input Validation ---
    postal_prefixes = [p.strip().upper() for p in postal_codes_input.split(',') if p.strip()]
    if not postal_prefixes:
        st.error("🚨 Please enter at least one valid postal code prefix.")
        st.stop()

    # Call the cached function to load/classify data
    all_leads_df = load_and_classify_leads(tuple(sorted(postal_prefixes)), location) # Use tuple for cache key

    if not all_leads_df.empty:
        st.session_state.all_leads_df = all_leads_df
        st.session_state.loaded_postal_prefixes = postal_prefixes
        # Clear previous filters when new data is loaded
        st.session_state.selected_industries_filter = []
        st.session_state.selected_compliance_filter = []
        st.session_state.selected_postal_filter = postal_prefixes # Default to showing all loaded postals
        st.success(f"✅ Loaded and classified {len(st.session_state.all_leads_df)} potential leads in {', '.join(postal_prefixes)}. Use filters below to refine.")
        # Rerun script to immediately show filters and data
        st.rerun()
    else:
        st.session_state.all_leads_df = pd.DataFrame() # Clear if loading failed
        st.warning("No leads found or error during loading.")


# --- Filtering and Display Logic ---
if not st.session_state.all_leads_df.empty:
    df_loaded = st.session_state.all_leads_df

    st.sidebar.header("📊 Filter Loaded Leads")

    # --- Filter Widgets ---
    # Industry Filter
    available_industries = sorted(df_loaded['industry'].dropna().unique())
    if not available_industries:
        st.sidebar.caption("No industries classified.")
    else:
        selected_industries = st.sidebar.multiselect(
            "Filter by Industry:",
            options=available_industries,
            key='selected_industries_filter' # Use session state key
        )

    # Compliance Filter
    # Explode compliance list and get unique tags
    try:
        all_compliance_tags = df_loaded['compliance'].explode().dropna().unique()
        available_compliance = sorted([tag for tag in all_compliance_tags if tag]) # Filter out empty strings/None
    except Exception: # Handle cases where explode might fail if data isn't list-like
        available_compliance = []

    if not available_compliance:
        st.sidebar.caption("No compliance tags found.")
    else:
         selected_compliance = st.sidebar.multiselect(
            "Filter by Compliance:",
            options=available_compliance,
            key='selected_compliance_filter' # Use session state key
        )

    # Postal Code Filter
    available_postals = sorted(df_loaded['postal_code'].dropna().unique())
    if not available_postals:
         st.sidebar.caption("No postal codes found.")
    else:
        selected_postals = st.sidebar.multiselect(
            "Filter by Postal Code:",
            options=available_postals,
            key='selected_postal_filter' # Use session state key
        )


    # --- Apply Filters ---
    df_filtered = df_loaded.copy() # Start with a copy of all loaded data

    if st.session_state.selected_industries_filter: # Check session state directly
        df_filtered = df_filtered[df_filtered['industry'].isin(st.session_state.selected_industries_filter)]

    if st.session_state.selected_compliance_filter: # Check session state directly
        # Filter rows where the list in 'compliance' contains any of the selected tags
        df_filtered = df_filtered[df_filtered['compliance'].apply(lambda tags: isinstance(tags, list) and any(tag in st.session_state.selected_compliance_filter for tag in tags))]

    if st.session_state.selected_postal_filter: # Check session state directly
        df_filtered = df_filtered[df_filtered['postal_code'].isin(st.session_state.selected_postal_filter)]


    # --- Process and Display Filtered Data ---
    st.subheader(f"Displaying {len(df_filtered)} Filtered Leads")

    if df_filtered.empty:
        st.warning("No leads match the current filter criteria.")
    else:
        # Score, Generate Scripts for the filtered data
        processed_leads_display = []
        df_display_input = df_filtered.copy() # Work on a copy for processing

        with st.spinner("Scoring leads and generating scripts..."):
            # Using apply might be cleaner but requires scorer/script_gen adjustments. Loop for now.
            for index, lead_row in df_display_input.iterrows():
                 lead_dict = lead_row.to_dict()
                 try:
                     # Get zone density for scoring
                     zone_density = stats_mapper.get_density_score(lead_dict.get("postal_code", ""), lead_dict.get("naics_code", ""))
                     # Score lead (assuming score_lead returns the updated dict)
                     # Pass a copy to avoid modifying the original dict within the loop implicitly
                     scored_lead = scorer.score_lead(lead_dict.copy(), zone_density_score=zone_density)
                     # Generate script (assuming generate returns the script string)
                     # Pass a copy of the *scored* lead data
                     scored_lead["Cold Call Script"] = script_gen.generate(scored_lead.copy())
                     processed_leads_display.append(scored_lead)
                 except Exception as e:
                     st.error(f"Error processing lead {lead_dict.get('business_name')}: {e}")
                     processed_leads_display.append(lead_dict) # Append original dict on error


        if processed_leads_display:
             df_display = pd.DataFrame(processed_leads_display)
        else:
             # If processing failed for all, show the filtered columns but no data
             df_display = pd.DataFrame(columns=df_filtered.columns)


        # Define columns for display, ensuring essential ones exist
        base_cols = ["business_name", "address", "postal_code", "industry", "compliance", "naics_code", "awrv_tier", "score", "Cold Call Script", "Google Maps Link"]
        # Filter base_cols to only those actually present in the final DataFrame
        display_cols = [col for col in base_cols if col in df_display.columns]

        # Ensure 'compliance' column is display-friendly (e.g., comma-separated string)
        if 'compliance' in df_display.columns:
             df_display['compliance_display'] = df_display['compliance'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
             # Put compliance_display after industry if possible
             if 'industry' in display_cols:
                 idx = display_cols.index('industry')
                 if 'compliance' in display_cols: display_cols.remove('compliance') # Remove original list column
                 if 'compliance_display' not in display_cols: display_cols.insert(idx + 1, 'compliance_display')
             elif 'compliance_display' not in display_cols:
                  display_cols.append('compliance_display') # Add if industry wasn't there


        st.dataframe(df_display[display_cols].fillna('N/A'), use_container_width=True) # Fill NA for display

        # --- Download CSV ---
        csv_data = df_display[display_cols].to_csv(index=False).encode('utf-8')
        download_filename = f"filtered_leads_{'_'.join(st.session_state.loaded_postal_prefixes)}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        st.download_button(
            label="📥 Download Filtered Leads (CSV)",
            data=csv_data,
            file_name=download_filename,
            mime="text/csv",
            key="download_csv_button"
        )

        # --- Optional Walk-In Links ---
        if "Google Maps Link" in df_display.columns and df_display["Google Maps Link"].notna().any():
             with st.expander("🗺️ View Walk-In Route Links for Filtered Leads"):
                # Sort by postal code for potentially better routing sequence
                sorted_links = df_display.sort_values(by='postal_code')[["business_name","Google Maps Link"]].dropna()
                for index, row in sorted_links.iterrows():
                    st.markdown(f"[{row['business_name']}]({row['Google Maps Link']})")

else:
    # Initial state before any data is loaded
    st.markdown("👈 Select territory filters in the sidebar and click 'Load Businesses in Territory'.")
    st.markdown("Once loaded, further filters for industry, compliance, and postal code will appear.")
