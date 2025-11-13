import csv
import logging
from typing import Dict, List, Any

logger = logging.getLogger("csv_exporter")

def export_contacts_to_csv(contacts: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export contact dictionaries to a CSV file.
    """
    if not contacts:
        logger.warning("No contacts provided for CSV export.")
        return

    base_fields = [
        "url",
        "email",
        "phone",
        "facebook_profile",
        "instagram_profile",
        "linkedin_profile",
        "twitter_x_profile",
    ]

    extra_fields = sorted(
        {key for contact in contacts for key in contact.keys()} - set(base_fields)
    )
    fieldnames = base_fields + extra_fields

    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for contact in contacts:
                writer.writerow(contact)
        logger.info("CSV export completed: %s", output_path)
    except Exception as exc:
        logger.error("Failed to export CSV to '%s': %s", output_path, exc)
        raise