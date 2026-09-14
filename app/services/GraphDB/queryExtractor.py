import re
import spacy
from typing import Dict

nlp = spacy.load("en_core_web_sm")

def extract_info(query: str) -> Dict:
    doc = nlp(query)

    age = None
    gender = None
    relation = None
    procedure = None
    location = None
    policy_duration = None
    event_time = None

    # --- Age ---
    age_match = re.search(r'(\d{2})[- ]?(year|yr)?[- ]?(old)?', query)
    if age_match:
        age = int(age_match.group(1))

    # --- Policy duration ---
    policy_match = re.search(r'policy (is|was)? ?(\d+)[ -]?(month|months|year|years)', query)
    if policy_match:
        value = int(policy_match.group(2))
        unit = policy_match.group(3)
        policy_duration = value * 12 if 'year' in unit else value

    # --- Event timing (e.g., "2 months ago") ---
    event_match = re.search(r'(\d+)[ -]?(month|months|year|years)[ -]?ago', query)
    if event_match:
        event_time = event_match.group(0)

    # --- Gender & relation ---
    if any(word in query.lower() for word in ["wife", "mother", "daughter", "sister"]):
        gender = "female"
        relation = re.findall(r"wife|mother|daughter|sister", query.lower())[0]

    if any(word in query.lower() for word in ["husband", "father", "son", "brother"]):
        gender = "male"
        relation = re.findall(r"husband|father|son|brother", query.lower())[0]

    # --- Procedure (using keywords) ---
    procedure_keywords = ["surgery", "maternity", "hospitalization", "therapy", "diabetes", "cancer", "covid", "delivery", "transplant"]
    for token in doc:
        if token.text.lower() in procedure_keywords:
            procedure = token.text.lower()
            break

    # --- Location ---
    for ent in doc.ents:
        if ent.label_ == "GPE":
            location = ent.text

    return {
        "age": age,
        "gender": gender,
        "relation": relation,
        "procedure": procedure,
        "location": location,
        "policy_duration_months": policy_duration,
        "event_time": event_time
    }

# 🧪 Example usage
if __name__ == "__main__":
    query = input("Enter natural language query: ")
    data = extract_info(query)
    print("🔍 Extracted Info:\n", data)
