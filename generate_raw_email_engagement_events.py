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

EMAIL_TYPES = ["sent", "delivered", "opened", "clicked", "unsubscribed"]

def build_rows(n, contacts, campaigns, companies):
    rows = []
    for _ in range(n):
        contact = rand_choice(contacts)
        company = find_by_key(companies, "company_key", contact["company_key"]) if contact.get("company_key") else rand_choice(companies)
        campaign = rand_choice(campaigns)
        event_type = rand_from({"sent": 30, "delivered": 28, "opened": 20, "clicked": 12, "unsubscribed": 1})
        rows.append({
            "event_id": f"EVT-{uuid.uuid4().hex[:12]}",
            "event_ts": rand_ts(60),
            "campaign_id": campaign["campaign_key"],
            "contact_id": contact["contact_key"],
            "email_address": contact["email"],
            "event_type": event_type,
            "message_id": f"MSG-{uuid.uuid4().hex[:14]}",
            "campaign_name": campaign["campaign_name"],
            "market": campaign["market"] or company["industry"],
        })
    return rows

def main():
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=1200)
    parser.add_argument("--output", type=str, default="raw_email_engagement_events.csv")
    args = parser.parse_args()

    contacts = load_csv(SEED_DIR / "dim_contact.csv")
    campaigns = load_csv(SEED_DIR / "dim_campaign.csv")
    companies = load_csv(SEED_DIR / "dim_company.csv")

    rows = build_rows(args.rows, contacts, campaigns, companies)
    write_csv(Path(args.output), [
        "event_id", "event_ts", "campaign_id", "contact_id", "email_address",
        "event_type", "message_id", "campaign_name", "market"
    ], rows)

if __name__ == "__main__":
    random.seed(42)
    main()
