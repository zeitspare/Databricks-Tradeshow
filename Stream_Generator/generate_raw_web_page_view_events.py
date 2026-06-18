import csv
import json
import random
import uuid
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path.cwd().parent

SEED_DIR = BASE_DIR / "seed_csvs"
OUT_DIR = BASE_DIR / "event_jsons" / "raw_web_page_view_events"


def load_csv(path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rand_ts(days_back=30):
    end = datetime.utcnow()
    start = end - timedelta(days=days_back)
    delta = end - start
    ts = start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))
    return ts.replace(microsecond=0).isoformat() + "Z"


def rand_choice(rows):
    return random.choice(rows)


def write_json(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


def find_by_key(rows, key_name, key_value):
    for r in rows:
        if r.get(key_name) == key_value:
            return r
    return None


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
        company = (
            find_by_key(companies, "company_key", contact["company_key"])
            if contact.get("company_key")
            else rand_choice(companies)
        )
        exhibition = rand_choice(exhibitions)
        event_type, page_url = rand_choice(PAGE_RULES)
        anonymous = random.random() < 0.18
        cookie_id = f"ck_{uuid.uuid4().hex[:16]}"

        row = {
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
        }

        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))

    return rows


def main():
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=1000)
    args = parser.parse_known_args()[0]

    contacts = load_csv(SEED_DIR / "dim_contact.csv")
    companies = load_csv(SEED_DIR / "dim_company.csv")
    exhibitions = load_csv(SEED_DIR / "dim_exhibition.csv")

    rows = build_rows(args.rows, contacts, companies, exhibitions)

    file_ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = OUT_DIR / f"raw_web_page_view_events_{file_ts}.json"

    write_json(output_file, rows)

    print(f"\nSaved {len(rows)} events to {output_file.resolve()}")


if __name__ == "__main__":
    random.seed(42)
    main()