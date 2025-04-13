import requests
import time
import os
from urllib.parse import urlencode, quote_plus
from .naics_keyword_map import NAICSKeywordMap

class GooglePlacesScraper:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required.")

        self.base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.naics_map = NAICSKeywordMap()

    def _make_request(self, params):
        """Helper function to make a request and handle errors."""
        url = f"{self.base_url}?{urlencode(params)}"
        try:
            response = requests.get(url, timeout=10) # Add timeout
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error during Google Places API request: {e}")
            return None # Return None on error

    def search_businesses_broadly(self, location, radius=10000, max_results_per_category=60):
        """
        Searches for businesses using broad categories within a location.
        Handles pagination up to a limit (to control API usage).
        Returns a deduplicated list of basic business info.
        """
        broad_categories = self.naics_map.get_broad_search_categories()
        all_results = []
        seen_place_ids = set()
        max_pages = max_results_per_category // 20 # Google returns up to 20 per page

        print(f"Starting broad Google scrape for categories: {', '.join(broad_categories)}") # Log start

        for category in broad_categories:
            print(f"  Scraping category: {category}...")
            page_count = 0
            next_page_token = None

            while page_count < max_pages:
                params = {
                    "query": category,
                    "location": location,
                    "radius": radius,
                    "key": self.api_key
                }
                if next_page_token:
                    params["pagetoken"] = next_page_token
                    # Google requires a short delay before using the next page token
                    time.sleep(2)

                data = self._make_request(params)

                if not data: # Handle request errors
                    print(f"    Error fetching data for {category}. Skipping.")
                    break # Stop processing this category on error

                if data.get("status") != "OK" and data.get("status") != "ZERO_RESULTS":
                     print(f"    Google API Error for category '{category}': {data.get('status')} - {data.get('error_message', 'No error message')}")
                     # Consider breaking or continuing based on the error type
                     if data.get("status") == "OVER_QUERY_LIMIT":
                         print("    Hit query limit. Stopping Google scrape.")
                         return all_results # Stop all scraping if limit is hit
                     break # Stop this category otherwise


                for place in data.get("results", []):
                    place_id = place.get("place_id")
                    if place_id and place_id not in seen_place_ids:
                        seen_place_ids.add(place_id)
                        name = place.get("name")
                        address = place.get("formatted_address")
                        lat = place.get("geometry", {}).get("location", {}).get("lat")
                        lng = place.get("geometry", {}).get("location", {}).get("lng")
                        # Use place_id for a more stable Maps link if available
                        maps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(name)}&query_place_id={place_id}" if place_id else None
                        # Fallback if place_id is missing but we have coords
                        if not maps_url and lat and lng:
                             maps_url = f"https://www.google.com/maps?q={lat},{lng}"


                        # Append basic info only - classification happens later
                        all_results.append({
                            "business_name": name,
                            "address": address,
                            "latitude": lat,
                            "longitude": lng,
                            "maps_link": maps_url,
                            "source": "Google" # Add source marker
                        })

                page_count += 1
                next_page_token = data.get("next_page_token")

                if not next_page_token:
                    break # No more pages for this category

            print(f"    Finished category '{category}'. Found {len(data.get('results',[]))} results on last page. Total unique results so far: {len(all_results)}")

        print(f"Finished broad Google scrape. Total unique results found: {len(all_results)}")
        return all_results

# Example usage (REMOVE or comment out before deployment):
# if __name__ == '__main__':
#     # Load environment variables if using .env locally
#     # from dotenv import load_dotenv
#     # load_dotenv()
#     scraper = GooglePlacesScraper()
#     # Make sure GOOGLE_API_KEY is set in your environment
#     leads = scraper.search_businesses_broadly("51.0447,-114.0719", radius=5000) # Example: Calgary, 5km radius
#     print(f"\n--- Found {len(leads)} unique leads ---")
#     # for i, lead in enumerate(leads[:5]): # Print first 5
#     #     print(f"{i+1}: {lead['business_name']} - {lead['address']}")
