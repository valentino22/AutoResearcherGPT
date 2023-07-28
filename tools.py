import os
from langchain.agents.agent_toolkits import create_python_agent
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType
from langchain.tools.python.tool import PythonREPLTool
from langchain.chat_models import ChatOpenAI
import langchain
from dotenv import load_dotenv
from langchain.agents import tool
from datetime import date

load_dotenv()

llm = ChatOpenAI(temperature=0)
tools = load_tools(["llm-math","wikipedia"], llm=llm) # using built in agents, wikipedia needs an install

agent= initialize_agent(
    tools, 
    llm, 
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose = True)

# question = "What books did Noah Yuval Harari wrote?"
# question = "What is the 25% of 300?"
# result = agent(question) 

pythonAgent = create_python_agent(
    llm,
    tool=PythonREPLTool(),
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    handle_parsing_errors=True
)

customer_list = [["Harrison", "Chase"], 
                 ["Lang", "Chain"],
                 ["Dolly", "Too"],
                 ["Elle", "Elem"], 
                 ["Geoff","Fusion"], 
                 ["Trance","Former"],
                 ["Jen","Ayai"]
                ]

langchain.debug=True
# pythonAgent.run(f"""Sort these customers by last name and then first name and print the output: {customer_list}""")
langchain.debug=False

# defining my own tools
@tool
def time(text: str) -> str:
    """Returns todays date, use this for any questions related to knowing todays date. The input should always be an empty string, and this function will always return todays date - any date mathmatics should occur outside this function."""
    return str(date.today())

agent= initialize_agent(
    tools + [time], 
    llm, 
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose = True)
    
question = "What books did Noah Yuval Harari wrote for kids?"
# question = "whats the date today?"

try:
    result = agent(question) 
except: 
    print("exception on external access")