import argparse
import json
import logging
import os
from typing import Any, Dict, List

from scanners.utils_parser import crawl_website
from scanners.email_scanner import extract_emails
from scanners.phone_scanner import extract_phone_numbers
from scanners.social_scanner import extract_social_profiles
from exporters.csv_exporter import export_contacts_to_csv
from exporters.json_exporter import export_contacts_to_json
from exporters.excel_exporter import export_contacts_to_excel

DEFAULT_SETTINGS = {
    "user_agent": "WebsiteContactGathererBot/1.0 (+https://bitbash.dev)",
    "request_timeout": 10,
    "max_pages": 5,
}

def setup_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

def load_settings(config_path: str | None) -> Dict[str, Any]:
    settings = DEFAULT_SETTINGS.copy()
    if not config_path:
        return settings

    if not os.path.exists(config_path):
        logging.warning("Config file '%s' not found, using default settings.", config_path)
        return settings

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_settings = json.load(f)
        if not isinstance(user_settings, dict):
            logging.warning("Config file '%s' did not contain a JSON object.", config_path)
            return settings
        settings.update(user_settings)
    except Exception as exc:
        logging.error("Failed to read config file '%s': %s", config_path, exc)
    return settings

def read_input_urls(input_path: str) -> List[str]:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' not found.")
    urls: List[str] = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls

def process_url(url: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    logger = logging.getLogger("processor")
    logger.info("Processing URL: %s", url)

    pages_html = crawl_website(
        base_url=url,
        max_pages=int(settings.get("max_pages", DEFAULT_SETTINGS["max_pages"])),
        timeout=int(settings.get("request_timeout", DEFAULT_SETTINGS["request_timeout"])),
        user_agent=str(settings.get("user_agent", DEFAULT_SETTINGS["user_agent"])),
    )

    if not pages_html:
        logger.warning("No HTML pages retrieved for URL: %s", url)

    emails = extract_emails(pages_html)
    phones = extract_phone_numbers(pages_html)
    social_profiles = extract_social_profiles(pages_html, base_url=url)

    result: Dict[str, Any] = {
        "url": url,
        "email": "; ".join(sorted(emails)) if emails else "",
        "phone": "; ".join(sorted(phones)) if phones else "",
        "facebook_profile": "; ".join(sorted(social_profiles.get("facebook_profile", []))),
        "instagram_profile": "; ".join(sorted(social_profiles.get("instagram_profile", []))),
        "linkedin_profile": "; ".join(sorted(social_profiles.get("linkedin_profile", []))),
        "twitter_x_profile": "; ".join(sorted(social_profiles.get("twitter_x_profile", []))),
    }

    logger.debug("Result for %s: %r", url, result)
    return result

def export_results(results: List[Dict[str, Any]], output_path: str, fmt: str) -> None:
    fmt = fmt.lower()
    if fmt == "json":
        export_contacts_to_json(results, output_path)
    elif fmt == "csv":
        export_contacts_to_csv(results, output_path)
    elif fmt in ("xlsx", "excel"):
        export_contacts_to_excel(results, output_path)
    else:
        raise ValueError(f"Unsupported export format: {fmt}")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Website Contact Gatherer - extract emails, phones, and social profiles from websites."
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to text file containing one URL per line.",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path to output file (extension should match format when possible).",
    )
    parser.add_argument(
        "--format",
        "-f",
        default="json",
        choices=["json", "csv", "xlsx", "excel"],
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--config",
        "-c",
        default=os.path.join(
            os.path.dirname(__file__),
            "config",
            "settings.example.json",
        ),
        help="Path to JSON config file (default: bundled settings.example.json).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (use -v or -vv).",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)

    logger = logging.getLogger("main")
    logger.info("Starting Website Contact Gatherer")

    try:
        settings = load_settings(args.config)
    except Exception as exc:
        logging.error("Error loading settings: %s", exc)
        settings = DEFAULT_SETTINGS.copy()

    try:
        urls = read_input_urls(args.input)
    except Exception as exc:
        logger.error("Failed to read input URLs: %s", exc)
        raise SystemExit(1)

    if not urls:
        logger.error("No URLs found in input file '%s'. Exiting.", args.input)
        raise SystemExit(1)

    results: List[Dict[str, Any]] = []
    for url in urls:
        try:
            result = process_url(url, settings)
            results.append(result)
        except Exception as exc:
            logger.error("Error processing URL '%s': %s", url, exc)

    if not results:
        logger.warning("No results to export.")
    else:
        try:
            export_results(results, args.output, args.format)
        except Exception as exc:
            logger.error("Failed to export results: %s", exc)
            raise SystemExit(1)

    logger.info("Completed Website Contact Gatherer run.")

if __name__ == "__main__":
    main()