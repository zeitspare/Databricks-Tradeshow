import csv
import json
import random
import uuid
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path

from azure.eventhub import EventHubProducerClient, EventData

BASE_DIR = Path.cwd().parent

SEED_DIR = BASE_DIR / "seed_csvs"
OUT_DIR = BASE_DIR / "event_jsons" / "raw_crm_contact_events"

# Azure Event Hubs settings
EVENT_HUB_CONNECTION_STR = ""
EVENT_HUB_NAME = "crm-contact-eventhub"


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


def write_json(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


def send_json_file_to_eventhub(json_file_path):
    """
    Reads the saved JSON array file and sends each object as one Event Hubs event.
    """
    with open(json_file_path, "r", encoding="utf-8") as f:
        rows = json.load(f)

    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR,
        eventhub_name=EVENT_HUB_NAME,
    )

    with producer:
        batch = producer.create_batch()
        batch_has_events = False

        for row in rows:
            event = EventData(json.dumps(row, ensure_ascii=False))

            try:
                batch.add(event)
                batch_has_events = True
            except ValueError:
                if batch_has_events:
                    producer.send_batch(batch)

                batch = producer.create_batch()
                batch.add(event)
                batch_has_events = True

        if batch_has_events:
            producer.send_batch(batch)


def find_by_key(rows, key_name, key_value):
    for r in rows:
        if r.get(key_name) == key_value:
            return r
    return None


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

        row = {
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
        }

        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))

    return rows


def main():
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=600)
    args = parser.parse_known_args()[0]

    contacts = load_csv(SEED_DIR / "dim_contact.csv")
    companies = load_csv(SEED_DIR / "dim_company.csv")

    rows = build_rows(args.rows, contacts, companies)

    file_ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = OUT_DIR / f"raw_crm_contact_events_{file_ts}.json"

    write_json(output_file, rows)
    send_json_file_to_eventhub(output_file)

    print(f"\nSaved {len(rows)} events to {output_file.resolve()}")
    print("Sent events to Azure Event Hubs.")


if __name__ == "__main__":
    random.seed(42)
    main()