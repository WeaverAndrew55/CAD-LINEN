class LeadScorer:
    def __init__(self):
        self.awrv_map = {
            "Auto Shop": "Low",
            "Food Processor": "Medium",
            "Electrical Contractor": "High",
            "Chemical Facility": "High"
        }

        self.compliance_scores = {
            "CSA Z96": 5,
            "NFPA 2112": 5,
            "NFPA 70E": 4,
            "HACCP": 4,
            "CFIA": 3,
            "WHMIS": 3,
            "GMP": 3,
            "Unknown": 1
        }

    def estimate_awrv_tier(self, industry):
        for keyword, tier in self.awrv_map.items():
            if keyword.lower() in industry.lower():
                return tier
        return "Medium"

    def score_lead(self, lead, zone_density_score=1):
        compliance = lead.get("compliance", "Unknown")
        compliance_score = 0

        for key, val in self.compliance_scores.items():
            if key.lower() in compliance.lower():
                compliance_score = max(compliance_score, val)

        lead["compliance_score"] = compliance_score
        lead["awrv_tier"] = self.estimate_awrv_tier(lead.get("industry", ""))
        lead["zone_density_score"] = zone_density_score
        lead["score"] = (compliance_score * 2) + lead.get("source_count", 1) + zone_density_score

        return lead

# Example usage:
# scorer = LeadScorer()
# for lead in leads:
#     print(scorer.score_lead(lead, zone_density_score=2))
