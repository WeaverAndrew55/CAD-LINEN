import requests
import time
import os
from urllib.parse import urlencode
from .naics_keyword_map import NAICSKeywordMap

class GooglePlacesScraper:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required.")

        self.base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.naics_map = NAICSKeywordMap()

    def search_businesses(self, query, location, radius=10000):
        params = {
            "query": query,
            "location": location,  # Format: "51.0447,-114.0719" (Calgary)
            "radius": radius,
            "key": self.api_key
        }
        url = f"{self.base_url}?{urlencode(params)}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        results = []
        for place in data.get("results", []):
            name = place.get("name")
            address = place.get("formatted_address")
            lat = place.get("geometry", {}).get("location", {}).get("lat")
            lng = place.get("geometry", {}).get("location", {}).get("lng")
            maps_url = f"https://www.google.com/maps?q={lat},{lng}" if lat and lng else None

            naics_code, industry = self.naics_map.guess_naics_from_text(name + " " + address)
            compliance = self.naics_map.get_compliance_for_naics(naics_code)

            results.append({
                "business_name": name,
                "address": address,
                "latitude": lat,
                "longitude": lng,
                "maps_link": maps_url,
                "naics_code": naics_code,
                "industry": industry,
                "compliance": compliance
            })

        return results

# Example usage:
# scraper = GooglePlacesScraper(api_key="YOUR_GOOGLE_API_KEY")
# leads = scraper.search_businesses("electrical contractor", "51.0447,-114.0719")
# for lead in leads:
#     print(lead)
