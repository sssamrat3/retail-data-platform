import json
from datetime import datetime
from pathlib import Path

from src.clients.api_client import APIClient
from src.clients.s3_client import S3Client
from src.common.logger import logger

RAW_DATA_DIR = Path("data/raw/orders")
PAGE_SIZE = 10  # small on purpose, so you can SEE pagination kick in


def fetch_all_products(client: APIClient) -> list:
    """
    Fetch all pages from the products endpoint, following total/skip/limit.
    """
    all_records = []
    skip = 0

    while True:
        page = client.get("products", params={"limit": PAGE_SIZE, "skip": skip})
        records = page.get("products", [])
        total = page.get("total", 0)

        logger.info(f"Fetched page: skip={skip}, got {len(records)} records (total={total})")

        all_records.extend(records)
        skip += PAGE_SIZE

        if skip >= total:
            break

    return all_records


def validate_records(records: list):
    """
    Basic sanity checks before trusting the dataset enough to persist it.
    """
    if not records:
        logger.error("No records fetched — aborting.")
        raise ValueError("Empty dataset from source API")

    required_fields = {"id", "title"}
    missing = required_fields - records[0].keys()
    if missing:
        logger.error(f"Missing expected fields: {missing}")
        raise ValueError(f"Schema mismatch: missing {missing}")

    logger.info(f"Validation passed: {len(records)} records look well-formed.")


def build_partitioned_key(now: datetime) -> str:
    return (
        f"raw/products/year={now.year}/month={now.month:02d}/day={now.day:02d}/"
        f"products_{now.strftime('%Y%m%d_%H%M%S')}.json"
    )


def fetch_orders():
    logger.info("Starting orders ingestion...")

    client = APIClient()
    records = fetch_all_products(client)

    validate_records(records)

    now = datetime.now()
    json_bytes = json.dumps(records, indent=2).encode("utf-8")

    # Local write
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    local_path = RAW_DATA_DIR / f"orders_{timestamp}.json"
    with open(local_path, "wb") as f:
        f.write(json_bytes)
    logger.info(f"Raw data written locally to {local_path} ({len(records)} records)")

    # S3 write
    s3_client = S3Client()
    s3_key = build_partitioned_key(now)
    s3_uri = s3_client.upload_json(json_bytes, s3_key)

    return {"local_path": local_path, "s3_uri": s3_uri}


if __name__ == "__main__":
    fetch_orders()