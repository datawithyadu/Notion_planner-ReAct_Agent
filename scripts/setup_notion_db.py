import os
import re
import requests
from dotenv import load_dotenv

NOTION_VERSION = "2025-09-03"  # required for the new multi-source database model


def create_databases():
    load_dotenv()

    api_key = os.getenv("NOTION_API_KEY")

    print("--- Setup Notion Databases ---")

    if not api_key:
        print("NOTION_API_KEY not found in .env")
        print("Please set it in your .env file first.")
        return

    print(f"Using API Key: {api_key[:4]}...{api_key[-4:]}")

    print("\nTo create databases, we need a Parent Page ID.")
    print("1. Create a new Page in Notion (e.g., 'Smart Task Planner').")
    print("2. Share this page with your Integration (Add connections).")
    print("3. Copy the Page ID from the URL (the long string at the end).")
    print("   Example URL: https://www.notion.so/My-Page-1234567890abcdef1234567890abcdef")
    print("   The ID is: 1234567890abcdef1234567890abcdef")
    user_input = input("\nEnter Parent Page ID or URL: ").strip()

    def extract_page_id(input_str):
        if "?" in input_str:
            input_str = input_str.split("?")[0]

        if "notion.so" in input_str:
            parts = input_str.split("/")
            last_part = parts[-1]
            match = re.search(r'([a-fA-F0-9]{32})', last_part)
            if match:
                return match.group(1)
            return last_part

        return input_str.replace("-", "")

    parent_page_id = extract_page_id(user_input)

    if len(parent_page_id) != 32:
        print(f"Warning: The ID '{parent_page_id}' doesn't look like a standard 32-char UUID.")
        print("Attempting to use it anyway...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }

    def create_database(title: str, data_source_properties: dict):
        """
        Creates a database + its initial data source in one call.
        Under 2025-09-03+, `properties` for the initial data source must be
        nested under `initial_data_source`, not top-level.
        Returns (database_id, data_source_id) or (None, None) on failure.
        """
        payload = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "initial_data_source": {
                "properties": data_source_properties
            },
        }
        response = requests.post(
            "https://api.notion.com/v1/databases", headers=headers, json=payload
        )
        if response.status_code != 200:
            print(f"Failed to create '{title}': {response.text}")
            return None, None

        data = response.json()
        db_id = data["id"]
        # The initial data source id comes back in the `data_sources` list.
        data_source_id = data["data_sources"][0]["id"]
        print(f"Created '{title}'! database_id={db_id}  data_source_id={data_source_id}")
        return db_id, data_source_id

    print("\nCreating 'Smart Task Planner Calendar'...")
    cal_db_id, cal_ds_id = create_database(
        "Smart Task Planner Calendar",
        {
            "Event": {"title": {}},
            "Date": {"date": {}},
            "Time": {"rich_text": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Upcoming", "color": "gray"},
                        {"name": "In Progress", "color": "blue"},
                        {"name": "Done", "color": "green"},
                        {"name": "Cancelled", "color": "red"},
                    ]
                }
            },
        },
    )

    print("\nCreating 'Smart Task Planner Notes'...")
    notes_db_id, notes_ds_id = create_database(
        "Smart Task Planner Notes",
        {
            "Note": {"title": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Pending", "color": "yellow"},
                        {"name": "Done", "color": "green"},
                    ]
                }
            },
        },
    )

    print("\n--- Setup Complete ---")
    if cal_db_id and notes_db_id:
        print("Please update your .env file with these IDs:")
        print(f"NOTION_CALENDAR_DB_ID={cal_db_id}")
        print(f"NOTION_CALENDAR_DATA_SOURCE_ID={cal_ds_id}")
        print(f"NOTION_NOTES_DB_ID={notes_db_id}")
        print(f"NOTION_NOTES_DATA_SOURCE_ID={notes_ds_id}")
        print(
            "\nNote: going forward, use the DATA_SOURCE_ID (not the DB ID) "
            "when querying or creating pages, e.g.:"
        )
        print("  PATCH /v1/data_sources/{data_source_id}/query")
        print("  POST  /v1/pages  with parent: {\"type\": \"data_source_id\", \"data_source_id\": \"...\"}")
        print("\nThen restart the application.")
    else:
        print("One or both databases failed to create — check the errors above.")


if __name__ == "__main__":
    create_databases()