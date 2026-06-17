import csv
import random
import uuid
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path

SEED_DIR = Path(__file__).resolve().parent / "seed_csvs"

def load_csv(path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def iso_now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def rand_ts(days_back=30):
    end = datetime.utcnow()
    start = end - timedelta(days=days_back)
    delta = end - start
    ts = start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))
    return ts.replace(microsecond=0).isoformat() + "Z"

def rand_choice(rows):
    return random.choice(rows)

def rand_from(weights):
    items = list(weights.keys())
    probs = list(weights.values())
    return random.choices(items, weights=probs, k=1)[0]

def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def find_by_key(rows, key_name, key_value):
    for r in rows:
        if r.get(key_name) == key_value:
            return r
    return None

def get_existing_or_random_contact(contacts):
    return rand_choice(contacts)

def get_existing_or_random_company(companies):
    return rand_choice(companies)

def get_existing_or_random_exhibition(exhibitions):
    return rand_choice(exhibitions)

def get_existing_or_random_campaign(campaigns):
    return rand_choice(campaigns)

FORM_RULES = [
    ("download_exhibitor_list", "download_exhibitor_list"),
    ("request_callback", "request_callback"),
    ("event_brochure_download", "event_brochure_download"),
    ("contact_us_submission", "contact_us_submission"),
]
SOURCE_CHANNELS = ["web", "partner", "email", "social", "direct"]

def build_rows(n, contacts, companies, campaigns):
    rows = []
    for _ in range(n):
        contact = rand_choice(contacts)
        company = find_by_key(companies, "company_key", contact["company_key"]) if contact.get("company_key") else rand_choice(companies)
        campaign = rand_choice(campaigns)
        form_id = f"FORM-{uuid.uuid4().hex[:10]}"
        interest_type, event_name = rand_choice(FORM_RULES)
        rows.append({
            "event_id": f"EVT-{uuid.uuid4().hex[:12]}",
            "event_ts": rand_ts(45),
            "form_id": form_id,
            "contact_email": contact["email"],
            "contact_first_name": contact["first_name"],
            "contact_last_name": contact["last_name"],
            "company_name": company["company_name"],
            "country": contact["country"],
            "interest_type": interest_type,
            "event_name": event_name,
            "source_channel": random.choice(SOURCE_CHANNELS) if random.random() < 0.65 else campaign["channel"],
        })
    return rows

def main():
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=800)
    parser.add_argument("--output", type=str, default="raw_form_submission_events.csv")
    args = parser.parse_args()

    contacts = load_csv(SEED_DIR / "dim_contact.csv")
    companies = load_csv(SEED_DIR / "dim_company.csv")
    campaigns = load_csv(SEED_DIR / "dim_campaign.csv")

    rows = build_rows(args.rows, contacts, companies, campaigns)
    write_csv(Path(args.output), [
        "event_id", "event_ts", "form_id", "contact_email", "contact_first_name",
        "contact_last_name", "company_name", "country", "interest_type", "event_name",
        "source_channel"
    ], rows)

if __name__ == "__main__":
    random.seed(42)
    main()
