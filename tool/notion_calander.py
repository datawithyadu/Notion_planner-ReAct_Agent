import os
from langchain.tools import tool
import requests 

# Get event
@tool
def get_event(date)->dict:
    """This tool will get the calander events for a spacific date (YYYY-MM-DD) from Notion"""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_CALENDAR_DB_ID")
    data_source_id = os.getenv("NOTION_CALENDAR_DATA_SOURCE_ID")
    url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"   # search URL, top of func  # for searching — near the top, like find_tool
    if not api_key or not db_id or not data_source_id:
        return {"Error": "MISSING ENVIRONMENT VARIABLES OF NOTION API KEY; DB ID; DATA SOURCE ID"}
    headers ={
    "content-type": "application/json",
    "authorization": f"Bearer {api_key}",
    "Notion-Version": "2026-03-11"
    }
    payload = {  
        "filter": {
        "property": "Date",
        "date": {"equals": date}
        }
    }

    try:
        response = requests.post(url,headers = headers, json = payload, timeout=10)
        response.raise_for_status()
        data = response.json()
    
        events = []
        for page in data.get("results",[]):
            props = page.get("properties", {})

            # Extracting the event title
            event_title_list = props.get("Event", {}).get("title",[])
            event_name = event_title_list[0].get("text",{}).get('content', "") if event_title_list else "Untitled event"

            # Extracting the Event time
            time_list = props.get("Time", {}). get("rich_text", [])
            event_time = time_list[0].get("text", {}).get("content", "") if time_list else "All_day"
            events.append({"Event": event_name, 'event_time':event_time})
        return {"events": events, "date": date}
    except requests.exceptions.RequestException as e:
        print(response.text)
        return f"Error fetching calendar event: {str(e)}"

# Create calander_event
@tool
def new_event(event_name, date, time, status)->dict:
    """This tool will create a new event for the input date"""
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_CALENDAR_DB_ID")
    data_source_id = os.getenv("NOTION_CALENDAR_DATA_SOURCE_ID")
    url = f"https://api.notion.com/v1/pages"   # create event
    if not api_key or not db_id or not data_source_id:
        return {"Error": "MISSING ENVIRONMENT VARIABLES OF NOTION API KEY; DB ID; DATA SOURCE ID"}
    headers ={
    "content-type": "application/json",
    "authorization": f"Bearer {api_key}",
    "Notion-Version": "2026-03-11"
    } 
    start_datetime = f"{date}T{time}:00+02:00" if time else date 
    payload = {
        "parent": {"type": "data_source_id", "data_source_id":data_source_id}, 
        "properties":{
               "Event": {"title": [{'text':{'content': event_name}}]},
               "Date": {"date":{"start": start_datetime}},
               "Time": {"rich_text": [{"text": {"content": time}}]},
               "Status": {"select": {"name": status}}
        }
    }
    try:
        response = requests.post(url,headers = headers, json = payload, timeout=10)
        response.raise_for_status()
        if not api_key or not db_id or not data_source_id:
                return {"Error": "MISSING ENVIRONMENT VARIABLES OF NOTION API KEY; DB ID; DATA SOURCE ID"}
        data = response.json()
        # We have get_notes and lets create the add_notes 
        return f"Event added successfully with name: {event_name},Start_Time: {time}, Date: {date}"
    except requests.exceptions.RequestException as e:
        print(response.text) 
        return f"Error creating event: {str(e)}"

# Trash event
@tool
def trash_event(event_name)-> str:
    "this tool will identify and trash the created event"
    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_CALENDAR_DB_ID")
    data_source_id = os.getenv("NOTION_CALENDAR_DATA_SOURCE_ID")
    url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"   # query endpoint
    if not api_key or not db_id or not data_source_id:
        return {"Error": "MISSING ENVIRONMENT VARIABLES OF NOTION API KEY; DB ID; DATA SOURCE ID"}
    headers ={
    "content-type": "application/json",
    "authorization": f"Bearer {api_key}",
    "Notion-Version": "2026-03-11"
    } 
    payload = {
        "filter" : {
            "property":"Event",
            "title": {"equals" : event_name}
        }
    }
    try:
        response = requests.post(url,headers = headers, json = payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results",[])
        if not results:
            return "Error: Unable to find the event"
        page_id = results[0].get("id","") # getting the first match from the query
        trash_url = f"https://api.notion.com/v1/pages/{page_id}"  # trash URL, AFTER page_id exist
        trash_payload = {"in_trash": True}
        trash_response = requests.patch(trash_url,headers = headers, json = trash_payload, timeout=10)
        trash_response.raise_for_status()
        return f"Event '{event_name}' has been moved to trash."
    except requests.exceptions.RequestException as e:
        print(response.text)
        return f"Error on trashing the event: {str(e)}"





















