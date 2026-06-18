import csv
import json
import random
import uuid
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path.cwd().parent

SEED_DIR = BASE_DIR / "seed_csvs"
OUT_DIR = BASE_DIR / "event_jsons" / "raw_sales_activity_events"



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


ACTIVITY_TYPES = ["call completed", "meeting scheduled", "quote requested", "follow-up sent"]
OUTCOMES = ["positive", "neutral", "negative", "pending", "rescheduled"]
NEXT_STEPS = [
    "send proposal",
    "schedule demo",
    "share pricing",
    "qualify requirements",
    "follow up in 3 days",
    "book onsite meeting",
]


def build_rows(n, contacts, companies):
    rows = []

    for _ in range(n):
        contact = rand_choice(contacts)
        company = (
            find_by_key(companies, "company_key", contact["company_key"])
            if contact.get("company_key")
            else rand_choice(companies)
        )
        activity_type = rand_choice(ACTIVITY_TYPES)
        due = datetime.utcnow() + timedelta(days=random.randint(1, 21))

        row = {
            "event_id": f"EVT-{uuid.uuid4().hex[:12]}",
            "event_ts": rand_ts(25),
            "activity_type": activity_type,
            "contact_id": contact["contact_key"],
            "account_id": company["company_key"],
            "sales_rep_id": f"REP-{random.randint(100,999)}",
            "next_step": random.choice(NEXT_STEPS),
            "outcome": random.choice(OUTCOMES),
            "due_date": due.date().isoformat(),
        }

        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))

    return rows


def main():
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=500)
    args = parser.parse_known_args()[0]

    contacts = load_csv(SEED_DIR / "dim_contact.csv")
    companies = load_csv(SEED_DIR / "dim_company.csv")

    rows = build_rows(args.rows, contacts, companies)

    file_ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = OUT_DIR / f"raw_sales_activity_events_{file_ts}.json"

    write_json(output_file, rows)

    print(f"\nSaved {len(rows)} events to {output_file.resolve()}")


if __name__ == "__main__":
    random.seed(42)
    main()