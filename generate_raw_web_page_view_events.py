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

PAGE_RULES = [
    ("homepage_visit", "/"),
    ("exhibitor_directory_view", "/exhibitors"),
    ("ticket_page_visit", "/tickets"),
    ("booth_inquiry_page_visit", "/exhibitor/inquiry"),
]

DEVICE_TYPES = ["desktop", "mobile", "tablet"]
REFERRERS = [
    "google", "bing", "linkedin", "email", "direct", "partner-site", "newsletter"
]
MARKET_FALLBACK = ["Food & Beverage", "Technology", "Healthcare", "Retail", "Media"]

def build_rows(n, contacts, companies, exhibitions):
    rows = []
    for _ in range(n):
        contact = rand_choice(contacts)
        company = find_by_key(companies, "company_key", contact["company_key"]) if contact.get("company_key") else rand_choice(companies)
        exhibition = rand_choice(exhibitions)
        event_type, page_url = rand_choice(PAGE_RULES)
        anonymous = random.random() < 0.18
        cookie_id = f"ck_{uuid.uuid4().hex[:16]}"
        rows.append({
            "event_id": f"EVT-{uuid.uuid4().hex[:12]}",
            "event_ts": rand_ts(45),
            "session_id": f"ses_{uuid.uuid4().hex[:14]}",
            "cookie_id": cookie_id,
            "contact_id_or_anonymous_id": f"anon_{uuid.uuid4().hex[:12]}" if anonymous else contact["contact_key"],
            "page_url": page_url,
            "page_type": event_type,
            "market": exhibition["market"] or company["industry"] or random.choice(MARKET_FALLBACK),
            "device_type": random.choice(DEVICE_TYPES),
            "referrer": random.choice(REFERRERS),
        })
    return rows

def main():
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--output", type=str, default="raw_web_page_view_events.csv")
    args = parser.parse_args()

    contacts = load_csv(SEED_DIR / "dim_contact.csv")
    companies = load_csv(SEED_DIR / "dim_company.csv")
    exhibitions = load_csv(SEED_DIR / "dim_exhibition.csv")

    rows = build_rows(args.rows, contacts, companies, exhibitions)
    write_csv(Path(args.output), [
        "event_id", "event_ts", "session_id", "cookie_id", "contact_id_or_anonymous_id",
        "page_url", "page_type", "market", "device_type", "referrer"
    ], rows)

if __name__ == "__main__":
    random.seed(42)
    main()
