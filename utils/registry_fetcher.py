import requests
import os
from .naics_keyword_map import NAICSKeywordMap

class CalgaryRegistryFetcher:
    def __init__(self, api_url=None):
        self.api_url = api_url or "https://data.calgary.ca/resource/k7p9-kppz.json"
        self.naics_map = NAICSKeywordMap()

    def fetch_by_postal(self, postal_prefix, limit=1000):
        params = {
            "$limit": limit,
            "$where": f"community_postal_code like '{postal_prefix}%'"
        }
        response = requests.get(self.api_url, params=params)
        response.raise_for_status()
        return self._process_results(response.json())

    def _process_results(self, records):
        results = []
        for record in records:
            name = record.get("trade_name") or record.get("legal_name")
            address = record.get("business_location")
            postal = record.get("community_postal_code")
            license_description = record.get("license_description", "")

            naics_code, industry = self.naics_map.guess_naics_from_text(name + " " + license_description)
            compliance = self.naics_map.get_compliance_for_naics(naics_code)

            results.append({
                "business_name": name,
                "address": address,
                "postal_code": postal,
                "license_description": license_description,
                "naics_code": naics_code,
                "industry": industry,
                "compliance": compliance,
                "source": "Calgary Registry"
            })
        return results

# Example usage:
# fetcher = CalgaryRegistryFetcher()
# leads = fetcher.fetch_by_postal("T1Y")
# for lead in leads:
#     print(lead)
