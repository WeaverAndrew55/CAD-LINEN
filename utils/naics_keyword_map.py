import json
import os
import re # For parsing display options
from fuzzywuzzy import process, fuzz # You might need to install python-Levenshtein for speed

class NAICSKeywordMap:
    def __init__(self, json_path="data/naics_keywords.json"):
        # Construct the absolute path relative to this file's directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        absolute_json_path = os.path.join(base_dir, '..', json_path) # Go up one level from utils/

        try:
            with open(absolute_json_path, 'r') as f:
                self.naics_data = json.load(f)
            # Pre-process for faster lookups: create keyword -> naics mapping and display options
            self._build_mappings()
        except FileNotFoundError:
            print(f"Error: NAICS JSON file not found at {absolute_json_path}")
            self.naics_data = {}
            self.keyword_to_naics = {}
            self.display_options = []
            self.display_option_to_details = {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {absolute_json_path}")
            self.naics_data = {}
            self.keyword_to_naics = {}
            self.display_options = []
            self.display_option_to_details = {}

    def _build_mappings(self):
        self.keyword_to_naics = {}
        self.display_options = []
        self.display_option_to_details = {}
        for naics_code, details in self.naics_data.items():
            keywords = details.get("keywords", [])
            industry = details.get("industry", "Unknown Industry")
            compliance = details.get("compliance", [])
            display_option = f"{industry} ({naics_code}) - Compliance: {', '.join(compliance) if compliance else 'N/A'}"
            self.display_options.append(display_option)
            self.display_option_to_details[display_option] = {
                "naics_code": naics_code,
                "industry": industry,
                "keywords": keywords,
                "compliance": compliance
            }
            for keyword in keywords:
                # Store the most relevant NAICS code for each keyword (can be refined)
                if keyword.lower() not in self.keyword_to_naics:
                    self.keyword_to_naics[keyword.lower()] = naics_code

    def get_keywords_for_naics(self, naics_code):
        return self.naics_data.get(str(naics_code), {}).get("trigger_keywords", [])

    def get_compliance_for_naics(self, naics_code):
        return self.naics_data.get(str(naics_code), {}).get("compliance_needs", "Unknown")

    def get_industry_by_keyword(self, keyword):
        matches = []
        for code, data in self.naics_data.items():
            if keyword.lower() in [kw.lower() for kw in data.get("trigger_keywords", [])]:
                matches.append({"naics_code": code, "industry": data["industry"], "compliance": data["compliance_needs"]})
        return matches

    def get_naics_from_keyword(self, keyword):
        """Finds the best matching NAICS code for a given keyword."""
        if not self.keyword_to_naics: return None
        # Simple exact match first
        match = self.keyword_to_naics.get(keyword.lower())
        if match:
            return match
        # Add fuzzy matching if exact fails (optional, can be slow)
        # best_match, score = process.extractOne(keyword.lower(), self.keyword_to_naics.keys())
        # if score > 80: # Adjust threshold as needed
        #     return self.keyword_to_naics[best_match]
        return None

    def get_details_from_naics(self, naics_code):
        """Returns the full details dictionary for a given NAICS code."""
        return self.naics_data.get(naics_code)

    def get_display_options(self):
        """Returns a list of strings formatted for display in dropdowns/multiselects."""
        return sorted(self.display_options)

    def get_details_from_display_option(self, display_option):
        """Retrieves the details dictionary based on the selected display option string."""
        return self.display_option_to_details.get(display_option)

    def guess_naics_from_text(self, text, threshold=80):
        """
        Attempts to guess the most relevant NAICS code and industry name
        based on keywords found within the input text (e.g., business name, description).
        Returns a tuple: (best_naics_code, best_industry_name, associated_compliance_tags) or (None, None, [])
        """
        if not text or not self.naics_data:
            return None, None, []

        text_lower = text.lower()
        best_match_naics = None
        highest_score = 0
        matched_keyword = None

        # Iterate through all keywords defined in the JSON
        for naics_code, details in self.naics_data.items():
            for keyword in details.get("keywords", []):
                keyword_lower = keyword.lower()
                # Check if keyword is in text (simple substring match)
                if keyword_lower in text_lower:
                    # Use fuzzy matching score for better relevance check
                    # score = fuzz.partial_ratio(keyword_lower, text_lower) # Check how much keyword matches part of text
                    # Use a simpler score: prioritize longer keyword matches or exact word matches
                    score = len(keyword_lower) # Simple score: longer keywords are more specific
                    if f" {keyword_lower} " in f" {text_lower} ": # Prioritize whole word match
                         score += 100

                    if score > highest_score:
                        highest_score = score
                        best_match_naics = naics_code
                        matched_keyword = keyword_lower

        if best_match_naics:
            details = self.naics_data.get(best_match_naics, {})
            industry = details.get("industry", "Unknown Industry")
            compliance = details.get("compliance", [])
            # print(f"Debug: Matched '{matched_keyword}' to NAICS {best_match_naics} ({industry}) with score {highest_score} in text: '{text}'") # Debug print
            return best_match_naics, industry, compliance
        else:
            # print(f"Debug: No keywords matched well in text: '{text}'") # Debug print
            return None, None, []

    def all_naics(self):
        return list(self.naics_data.keys())

    def get_all_data(self):
        return self.naics_data

    def get_broad_search_categories(self):
        """
        Returns a list of broad, high-level business types relevant for initial,
        less targeted scraping (especially for Google Places).
        This helps balance coverage and API usage.
        """
        # These should be distinct, common types covering major Canadian Linen verticals
        return [
            "restaurant",         # Food Service (HACCP)
            "manufacturing",      # Industrial, Production (CSA, FR)
            "automotive repair",  # Mechanics, Shops (General Safety)
            "medical clinic",     # Healthcare (Specific requirements)
            "construction",       # Building sites (CSA Z96)
            "food processing",    # Food Production (HACCP, GMP)
            "industrial supply",  # Related industrial businesses
            "hotel",              # Hospitality
            "machine shop",       # Specific Manufacturing (FR, Safety)
            "electrical contractor" # Trades (NFPA 70E)
        ]
