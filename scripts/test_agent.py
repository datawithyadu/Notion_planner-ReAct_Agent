from Agent.bot import create_react_agent
from dotenv import load_dotenv
def main():
    load_dotenv()
    agent = create_react_agent()
    query = 'What is the weather of berlin now'
    response = agent.invoke({"messages": [("user", query)]})
    print("\n Agent Response")
    print(response)
if __name__ == "__main__":
    main()

