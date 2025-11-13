import logging
from typing import Dict, List, Any

from openpyxl import Workbook

logger = logging.getLogger("excel_exporter")

def export_contacts_to_excel(contacts: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export contact dictionaries to an Excel (.xlsx) file.
    """
    if not contacts:
        logger.warning("No contacts provided for Excel export.")
        return

    # Determine all fields across contacts
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

    wb = Workbook()
    ws = wb.active
    ws.title = "Contacts"

    # Write header
    ws.append(fieldnames)

    # Write rows
    for contact in contacts:
        row = [contact.get(field, "") for field in fieldnames]
        ws.append(row)

    try:
        wb.save(output_path)
        logger.info("Excel export completed: %s", output_path)
    except Exception as exc:
        logger.error("Failed to export Excel to '%s': %s", output_path, exc)
        raise