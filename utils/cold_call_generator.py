class ColdCallGenerator:
    def __init__(self):
        self.templates = {
            "CSA": "Hi, this is {rep_name} with Canadian Linen—we help teams like yours stay CSA-compliant with certified workwear and safety-first service. Who handles your safety uniforms?",
            "HACCP": "Hi, this is {rep_name} with Canadian Linen—I specialize in HACCP-aligned uniform and towel services for food processors. Can I ask who oversees your sanitation compliance?",
            "NFPA": "Hi, this is {rep_name} with Canadian Linen—we support industrial crews with FR gear that meets NFPA 70E and 2112. Who manages your PPE contracts right now?",
            "Default": "Hi, this is {rep_name} with Canadian Linen—we help businesses in {industry} improve safety, appearance, and compliance with weekly uniform service. Who would I speak to about that?"
        }

    def generate(self, lead, rep_name="Your Name"):
        compliance = lead.get("compliance", "").upper()
        industry = lead.get("industry", "your field").lower()

        if "CSA" in compliance:
            template = self.templates["CSA"]
        elif "HACCP" in compliance or "CFIA" in compliance:
            template = self.templates["HACCP"]
        elif "NFPA" in compliance:
            template = self.templates["NFPA"]
        else:
            template = self.templates["Default"]

        return template.format(rep_name=rep_name, industry=industry)

# Example usage:
# generator = ColdCallGenerator()
# print(generator.generate({"compliance": "CSA Z96", "industry": "electrical contracting"}))
