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

ACTIVITY_TYPES = ["call completed", "meeting scheduled", "quote requested", "follow-up sent"]
OUTCOMES = ["positive", "neutral", "negative", "pending", "rescheduled"]
NEXT_STEPS = [
    "send proposal", "schedule demo", "share pricing", "qualify requirements",
    "follow up in 3 days", "book onsite meeting"
]

def build_rows(n, contacts, companies):
    rows = []
    for _ in range(n):
        contact = rand_choice(contacts)
        company = find_by_key(companies, "company_key", contact["company_key"]) if contact.get("company_key") else rand_choice(companies)
        activity_type = rand_choice(ACTIVITY_TYPES)
        due = datetime.utcnow() + timedelta(days=random.randint(1, 21))
        rows.append({
            "event_id": f"EVT-{uuid.uuid4().hex[:12]}",
            "event_ts": rand_ts(25),
            "activity_type": activity_type,
            "contact_id": contact["contact_key"],
            "account_id": company["company_key"],
            "sales_rep_id": f"REP-{random.randint(100,999)}",
            "next_step": random.choice(NEXT_STEPS),
            "outcome": random.choice(OUTCOMES),
            "due_date": due.date().isoformat(),
        })
    return rows

def main():
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=500)
    parser.add_argument("--output", type=str, default="raw_sales_activity_events.csv")
    args = parser.parse_args()

    contacts = load_csv(SEED_DIR / "dim_contact.csv")
    companies = load_csv(SEED_DIR / "dim_company.csv")

    rows = build_rows(args.rows, contacts, companies)
    write_csv(Path(args.output), [
        "event_id", "event_ts", "activity_type", "contact_id", "account_id",
        "sales_rep_id", "next_step", "outcome", "due_date"
    ], rows)

if __name__ == "__main__":
    random.seed(42)
    main()
