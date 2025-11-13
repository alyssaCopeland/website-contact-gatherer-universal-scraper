import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger("json_exporter")

def export_contacts_to_json(contacts: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export contact dictionaries to a JSON file.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=4, ensure_ascii=False)
        logger.info("JSON export completed: %s", output_path)
    except Exception as exc:
        logger.error("Failed to export JSON to '%s': %s", output_path, exc)
        raise