import csv
import json
import random
import uuid
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path


BASE_DIR = Path.cwd().parent

SEED_DIR = BASE_DIR / "seed_csvs"
OUT_DIR = BASE_DIR / "event_jsons" / "raw_form_submission_events"



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
        company = (
            find_by_key(companies, "company_key", contact["company_key"])
            if contact.get("company_key")
            else rand_choice(companies)
        )
        campaign = rand_choice(campaigns)

        form_id = f"FORM-{uuid.uuid4().hex[:10]}"
        interest_type, event_name = rand_choice(FORM_RULES)

        row = {
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
        }

        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))

    return rows


def main():
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=800)
    args = parser.parse_known_args()[0]

    contacts = load_csv(SEED_DIR / "dim_contact.csv")
    companies = load_csv(SEED_DIR / "dim_company.csv")
    campaigns = load_csv(SEED_DIR / "dim_campaign.csv")

    rows = build_rows(args.rows, contacts, companies, campaigns)

    file_ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = OUT_DIR / f"raw_form_submission_events_{file_ts}.json"

    write_json(output_file, rows)

    print(f"\nSaved {len(rows)} events to {output_file.resolve()}")


if __name__ == "__main__":
    random.seed(42)
    main()