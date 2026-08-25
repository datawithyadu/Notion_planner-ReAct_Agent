from contextlib import asynccontextmanager      # provides @asynccontextmanager, needed to define a lifespan handler
from fastapi import FastAPI, HTTPException       # FastAPI itself, plus HTTPException for clean error responses
from pydantic import BaseModel                    # validates and auto-converts incoming request data
from Agent.bot import create_react_agent          # our own function that builds the ReAct agent
from utils.logger import get_logger               # our own logging setup

logger = get_logger(__name__)                     # one logger for this file, tagged with its module name

agent = None  # placeholder — real agent is built at startup, not at import time

@asynccontextmanager                              # marks this function as a startup/shutdown handler
async def lifespan(app: FastAPI):                 # runs once at startup, then again at shutdown (split by `yield`)
    global agent                                  # modify the agent defined outside this function, not create a new local one
    try:
        agent = create_react_agent()              # the actual setup work — builds LLM connection + tools
        logger.info("Agent initialized successfully")  # confirms success in the logs
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")  # records the real failure reason
        raise                                      # stop the server from starting in a broken state
    yield                                          # hands control to the running server; requests get handled here
    # (code after this line would run on shutdown, if cleanup were needed)

app = FastAPI(title="ReAct Agent API", lifespan=lifespan)  # app created here, wired to the lifespan handler above

class ChatRequest(BaseModel):                      # defines the expected shape of a /chat request body
    query: str                                     # must contain a single string field called "query"

@app.get("/health")                                # a simple GET endpoint to check the server is alive
def health():
    return {"status": "ok"}

@app.post("/chat")                                 # the main endpoint — accepts a query, returns the agent's answer
def chat(request: ChatRequest):                    # FastAPI validates the incoming body against ChatRequest automatically
    logger.info(f"Received query: {request.query}")  # log every incoming request for traceability
    try:
        response = agent.invoke({"messages": [("user", request.query)]})  # same shape used throughout the notebook today
        final_message = response["messages"][-1].content  # the agent's final answer is the last message in the list
        return {"response": final_message}          # send just the clean answer back, not the full internal message log
    except Exception as e:
        logger.error(f"Chat request failed: {e}")   # technical detail, for you/developer, stays in the logs only
        raise HTTPException(                         # what the caller of your API actually sees — clean, no internals
            status_code=500,
            detail="Something went wrong while processing your request. Please try again."
        )



from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_index():
    return FileResponse("static/index.html")