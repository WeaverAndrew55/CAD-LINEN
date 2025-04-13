import json
import os

class NAICSKeywordMap:
    def __init__(self, json_path="../data/naics_keywords.json"):
        if not os.path.exists(json_path):
            # Attempt to find the file relative to the script's location
            script_dir = os.path.dirname(__file__)
            abs_json_path = os.path.join(script_dir, json_path)
            if not os.path.exists(abs_json_path):
                 raise FileNotFoundError(f"NAICS keyword map not found at {json_path} or {abs_json_path}")
            self.json_path = abs_json_path
        else:
             self.json_path = json_path

        with open(self.json_path, "r") as f:
            self.map = json.load(f)

    def get_keywords_for_naics(self, naics_code):
        return self.map.get(str(naics_code), {}).get("trigger_keywords", [])

    def get_compliance_for_naics(self, naics_code):
        return self.map.get(str(naics_code), {}).get("compliance_needs", "Unknown")

    def get_industry_by_keyword(self, keyword):
        matches = []
        for code, data in self.map.items():
            if keyword.lower() in [kw.lower() for kw in data.get("trigger_keywords", [])]:
                matches.append({"naics_code": code, "industry": data["industry"], "compliance": data["compliance_needs"]})
        return matches

    def guess_naics_from_text(self, text):
        text = text.lower()
        for code, data in self.map.items():
            if any(kw.lower() in text for kw in data.get("trigger_keywords", [])):
                return code, data["industry"]
        return None, "Unknown"

    def all_naics(self):
        return list(self.map.keys())

    def get_all_data(self):
        return self.map
