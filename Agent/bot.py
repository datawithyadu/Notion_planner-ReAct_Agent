import os
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.tools import tool
from tool.weather import get_weather
from tool.notion_notes import get_notes, add_notes,trash_tool
from tool.notion_calander import get_event, new_event, trash_event
from utils.logger import get_logger

logger = get_logger(__name__) # During the compilation agent will see this name as agent.bot

# Initialize the llm 
def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("Groq API not set")
        raise ValueError("Groq API not set") # Implimented this because logger will not stop the execution it only log the error
    return ChatGroq(
        model = "openai/gpt-oss-20b",
        temperature=0, 
        api_key= api_key,
        max_tokens=1600  
    )
# Define agent 
def create_react_agent():
    logger.info("initializing agent")
    llm = get_llm()
    tools = [get_weather, get_notes, add_notes, trash_tool, new_event, get_event, trash_event]

    try:
        agent = create_agent(model= llm, tools = tools)
        logger.info("The agent creation initialized")
        return agent
    except TypeError as e:
        logger.error(f"Failed to create agent: {e}")
        raise e
    


