from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

class LeadMerger:
    def __init__(self, threshold=0.85):
        self.threshold = threshold

    def merge(self, google_leads, registry_leads):
        merged = []
        used_registry_indices = set()

        for g in google_leads:
            best_match = None
            best_score = 0
            best_index = -1

            for idx, r in enumerate(registry_leads):
                if idx in used_registry_indices:
                    continue

                score = similar(g['business_name'], r['business_name'])
                if score > best_score:
                    best_score = score
                    best_match = r
                    best_index = idx

            if best_score >= self.threshold:
                used_registry_indices.add(best_index)
                merged_lead = {**g, **best_match}
                merged_lead['source_count'] = 2
            else:
                merged_lead = g
                merged_lead['source_count'] = 1

            merged.append(merged_lead)

        for idx, r in enumerate(registry_leads):
            if idx not in used_registry_indices:
                r['source_count'] = 1
                merged.append(r)

        return merged

# Example usage:
# merger = LeadMerger()
# combined = merger.merge(google_leads, registry_leads)
# for lead in combined:
#     print(lead)
