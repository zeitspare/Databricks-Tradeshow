import csv
import json
import random
import uuid
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path

SEED_DIR = Path("./seed_csvs/")


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


INTERACTION_RULES = [
    ("badge_scan_at_booth", "badge_scan_at_booth"),
    ("seminar_attendance", "seminar_attendance"),
    ("meeting_booked_onsite", "meeting_booked_onsite"),
    ("lead_captured_by_staff", "lead_captured_by_staff"),
]

BOOTH_PREFIXES = ["A", "B", "C", "D", "E", "F", "G"]
SPEAKER_IDS = [f"SPK-{i:03d}" for i in range(1, 51)]
SCAN_SOURCES = ["badge_scan", "mobile_app", "staff_entry", "self_checkin"]


def build_rows(n, contacts, exhibitions):
    rows = []

    for _ in range(n):
        contact = rand_choice(contacts)
        exhibition = rand_choice(exhibitions)
        event_name, interaction_type = rand_choice(INTERACTION_RULES)

        row = {
            "event_id": f"EVT-{uuid.uuid4().hex[:12]}",
            "event_ts": rand_ts(20),
            "event_name": event_name,
            "interaction_type": interaction_type,
            "badge_id": f"BDG-{uuid.uuid4().hex[:10]}",
            "contact_id": contact["contact_key"],
            "exhibition_id": exhibition["exhibition_key"],
            "booth_id": f"{random.choice(BOOTH_PREFIXES)}-{random.randint(1, 999)}",
            "session_id": f"SES-{uuid.uuid4().hex[:12]}",
            "speaker_id": random.choice(SPEAKER_IDS) if interaction_type == "seminar_attendance" else "",
            "scan_source": random.choice(SCAN_SOURCES),
        }

        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))

    return rows


def main():
    parser = ArgumentParser()
    parser.add_argument("--rows", type=int, default=700)
    parser.add_argument("--output", type=str, default="raw_event_interaction_events.json")
    args = parser.parse_args()

    contacts = load_csv(SEED_DIR / "dim_contact.csv")
    exhibitions = load_csv(SEED_DIR / "dim_exhibition.csv")

    rows = build_rows(args.rows, contacts, exhibitions)

    write_json(Path(args.output), rows)

    print(f"\nSaved {len(rows)} events to {Path(args.output).resolve()}")


if __name__ == "__main__":
    random.seed(42)
    main()