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

LIFECYCLE_STAGES = ["new", "engaged", "mql", "sql", "opportunity", "customer", "inactive"]
LEAD_STATUSES = ["open", "qualified", "rejected", "working", "nurture", "converted"]
CHANGE_TYPES = ["new contact created", "lead qualified", "lead rejected", "opportunity created", "owner changed"]
SOURCE_SYSTEMS = ["SAP Sales Cloud V2", "Marketing Cloud", "CRM Sync", "Manual Entry"]
OWNER_PREFIX = ["USR", "REP", "SALES"]

def build_rows(n, contacts, companies):
    rows = []
    for _ in range(n):
        contact = rand_choice(contacts)
        company = find_by_key(companies, "company_key", contact["company_key"]) if contact.get("company_key") else rand_choice(companies)
        change_type = rand_choice(CHANGE_TYPES)
        if change_type == "new contact created":
            lifecycle = "new"
            lead_status = "open"
        elif change_type == "lead qualified":
            lifecycle = "sql"
            lead_status = "qualified"
        elif change_type == "lead rejected":
            lifecycle = "inactive"
            lead_status = "rejected"
        elif change_type == "opportunity created":
            lifecycle = "opportunity"
            lead_status = "working"
        else:
            lifecycle = random.choice(LIFECYCLE_STAGES)
            lead_status = random.choice(LEAD_STATUSES)

        rows.append({
            "event_id": f"EVT-{uuid.uuid4().hex[:12]}",
            "event_ts": rand_ts(35),
            "contact_id": contact["contact_key"],
            "account_id": company["company_key"],
            "lifecycle_stage": lifecycle,
            "lead_status": lead_status,
            "owner_user_id": f"{random.choice(OWNER_PREFIX)}-{random.randint(100,999)}",
            "last_activity_ts": rand_ts(20),
            "source_system": random.choice(SOURCE_SYSTEMS),
            "change_type": change_type,
        })
    return rows

def main():
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=600)
    parser.add_argument("--output", type=str, default="raw_crm_contact_events.csv")
    args = parser.parse_args()

    contacts = load_csv(SEED_DIR / "dim_contact.csv")
    companies = load_csv(SEED_DIR / "dim_company.csv")

    rows = build_rows(args.rows, contacts, companies)
    write_csv(Path(args.output), [
        "event_id", "event_ts", "contact_id", "account_id", "lifecycle_stage",
        "lead_status", "owner_user_id", "last_activity_ts", "source_system",
        "change_type"
    ], rows)

if __name__ == "__main__":
    random.seed(42)
    main()
