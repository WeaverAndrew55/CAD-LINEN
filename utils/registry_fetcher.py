import requests
import os
from .naics_keyword_map import NAICSKeywordMap

class CalgaryRegistryFetcher:
    # Using Calgary Open Data API for business licenses
    BASE_URL = "https://data.calgary.ca/resource/pkth-465i.json"
    # Limit results per call for pagination/performance
    LIMIT = 5000

    def __init__(self):
        # Optionally load API key/token if needed in the future
        # self.api_token = os.getenv("CALGARY_API_TOKEN")
        self.naics_mapper = NAICSKeywordMap() # Reuse the map for industry classification

    def fetch_by_postal(self, postal_prefixes: list[str]) -> list[dict]:
        """Fetches business licenses starting with the given postal code prefixes."""
        all_results = []
        unique_businesses = set() # To track unique business names/addresses for deduplication

        if not isinstance(postal_prefixes, list):
            postal_prefixes = [postal_prefixes] # Ensure it's a list

        for prefix in postal_prefixes:
            prefix = prefix.strip().upper()
            if not prefix or len(prefix) < 3:
                print(f"Skipping invalid postal prefix: {prefix}")
                continue

            print(f"Fetching from Calgary Registry for postal prefix: {prefix}...")
            offset = 0
            while True:
                params = {
                    "$where": f"startswith(postal_code, '{prefix}')",
                    "$limit": self.LIMIT,
                    "$offset": offset
                }
                try:
                    response = requests.get(self.BASE_URL, params=params)
                    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                    data = response.json()

                    if not data:
                        break # No more data for this prefix

                    for item in data:
                        # Basic deduplication based on name and address
                        business_key = (item.get('tradename'), item.get('address'))
                        if business_key in unique_businesses:
                            continue
                        unique_businesses.add(business_key)

                        # Map to standardized lead format
                        lead = self._format_lead(item)
                        all_results.append(lead)

                    offset += self.LIMIT

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching Calgary Registry data for {prefix}: {e}")
                    break # Stop fetching for this prefix on error
                except Exception as e:
                    print(f"Error processing Calgary Registry data for {prefix}: {e}")
                    break # Stop processing on other errors

        print(f"Fetched {len(all_results)} potential leads from Calgary Registry for prefixes: {postal_prefixes}")
        return all_results

    def _format_lead(self, item: dict) -> dict:
        name = item.get("trade_name") or item.get("legal_name")
        address = item.get("business_location")
        postal = item.get("community_postal_code")
        license_description = item.get("license_description", "")

        naics_code, industry = self.naics_mapper.guess_naics_from_text(name + " " + license_description)
        compliance = self.naics_mapper.get_compliance_for_naics(naics_code)

        return {
            "business_name": name,
            "address": address,
            "postal_code": postal,
            "license_description": license_description,
            "naics_code": naics_code,
            "industry": industry,
            "compliance": compliance,
            "source": "Calgary Registry"
        }

# Example usage:
# fetcher = CalgaryRegistryFetcher()
# leads = fetcher.fetch_by_postal(["T1Y", "T2Y"])
# for lead in leads:
#     print(lead)
