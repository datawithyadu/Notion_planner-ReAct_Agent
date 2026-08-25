import os
from langchain.tools import tool
import requests 

# Get notes
@tool
def get_notes()-> list:
    """Get all pending notes from the notion database"""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_NOTES_DB_ID")
    data_source_id = os.getenv("NOTION_NOTES_DATA_SOURCE_ID")
    url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
    if not api_key or not db_id or not data_source_id:
        return {"Error": "MISSING ENVIRONMENT VARIABLES OF NOTION API KEY; DB ID; DATA SOURCE ID"}
    headers = {
    "content-type": "application/json",
    "authorization": f"Bearer {api_key}",
    "Notion-Version": "2026-03-11"
    }
    payload = {  # Apply the filter in which the status is pending
        "filter": {
        "property": "Status",
        "select": {"equals":"Pending"}
        }
    }
    # Making the api request
    try:
        response = requests.post(url,headers = headers, json = payload)
        response.raise_for_status()
        data = response.json()
        # Get all the necessery data inside variables and append to the notes.
        notes = []
        for page in data.get('results',[]):
            page_id = page.get('id', "")
            props = page.get('properties',{})
            title_list = props.get('Note',{}).get('title',{})
            Note_content = title_list[0]. get('text', {}).get('content', "") if title_list else "untitled_note"
            notes.append({"content": Note_content, "id": page_id})
        return notes if notes else ["No pending notes found."]
    except requests.exceptions.RequestException as e:
        return {"Error": f"Faild to fetch the Notes: {e}"}

# Add note
@tool
def add_notes(note_title, note_content, status)-> str:
    """Get all pending notes from the notion database"""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_NOTES_DB_ID")
    data_source_id = os.getenv("NOTION_NOTES_DATA_SOURCE_ID")
    url = f"https://api.notion.com/v1/pages"
    if not api_key or not db_id or not data_source_id:
        return {"Error": "MISSING ENVIRONMENT VARIABLES OF NOTION API KEY; DB ID; DATA SOURCE ID"}
    headers ={
    "content-type": "application/json",
    "authorization": f"Bearer {api_key}",
    "Notion-Version": "2026-03-11"
    }

    payload = {
    "parent": {"type": "data_source_id", "data_source_id": data_source_id},
    "properties": {
        "Note": {"title": [{"text": {"content": note_title}}]},
        "note_content": {"rich_text": [{"text": {"content": note_content}}]},
        "Status": {"select": {"name": status}}
    }
}

    try:
        response = requests.post(url,headers = headers, json = payload)
        response.raise_for_status()
        data = response.json()
        if not api_key or not db_id or not data_source_id:
                return {"Error": "MISSING ENVIRONMENT VARIABLES OF NOTION API KEY; DB ID; DATA SOURCE ID"}
        data = response.json()
        # We have get_notes and lets create the add_notes 
        return f"Note added successfully with ID: {data['id']},status: {status}"
    except requests.exceptions.RequestException as e:
        return f"Error on adding the Note: {str(e)}"

# find the page
@tool
def find_tool(note_name)->str:
    """Search for a note by its exact title and return its page ID."""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_NOTES_DB_ID")
    data_source_id = os.getenv("NOTION_NOTES_DATA_SOURCE_ID")
    url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
    if not api_key or not db_id or not data_source_id:
        return {"Error": "MISSING ENVIRONMENT VARIABLES OF NOTION API KEY; DB ID; DATA SOURCE ID"}
    headers ={
    "content-type": "application/json",
    "authorization": f"Bearer {api_key}",
    "Notion-Version": "2026-03-11"
    }
    payload = {  # Apply the filter in which get the note name which is searching
        "filter": {
        "property": "Note",
        "title": {"equals": note_name}
        }
    }
    try:
        response = requests.post(url,headers = headers, json = payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results",[])
        if not results:
            return "Error: Unable to find the page"
        page_id = results[0].get("id","") # getting the first match from the query
        
        # We have get_notes and lets create the add_notes 
        return f"Found note with page ID: {page_id}"
    except requests.exceptions.RequestException as e:
        return f"Error on finding the Note: {str(e)}"


# trash tool
@tool
def trash_tool(note_name)->str:
    """Search for a note by its exact title and move it to trash if found."""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_NOTES_DB_ID")
    data_source_id = os.getenv("NOTION_NOTES_DATA_SOURCE_ID")
    url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"   # search URL, top of func  # for searching — near the top, like find_tool
    if not api_key or not db_id or not data_source_id:
        return {"Error": "MISSING ENVIRONMENT VARIABLES OF NOTION API KEY; DB ID; DATA SOURCE ID"}
    headers ={
    "content-type": "application/json",
    "authorization": f"Bearer {api_key}",
    "Notion-Version": "2026-03-11"
    }
    payload = {  # Apply the filter in which get the note name which is searching
        "filter": {
        "property": "Note",
        "title": {"equals": note_name}
        }
    }
    try:
        response = requests.post(url,headers = headers, json = payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results",[])
        if not results:
            return "Error: Unable to find the page"
        page_id = results[0].get("id","") # getting the first match from the query
        trash_url = f"https://api.notion.com/v1/pages/{page_id}"   # trash URL, AFTER page_id exist
        trash_payload = {"in_trash": True}
        trash_response = requests.patch(trash_url,headers = headers, json = trash_payload, timeout=10)
        trash_response.raise_for_status()
        return f"Note '{note_name}' has been moved to trash."
    except requests.exceptions.RequestException as e:
        return f"Error on trashing the Note: {str(e)}"















