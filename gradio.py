# https://github.com/freddyaboulton/gradio-tools
from gradio_tools import (StableDiffusionTool, StableDiffusionPromptGeneratorTool, TextToVideoTool)
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()

llm = OpenAI(temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history")

tools = [StableDiffusionTool().langchain, StableDiffusionPromptGeneratorTool().langchain, TextToVideoTool().langchain]

agent = initialize_agent(tools, llm, memory=memory, agent="conversational-react-description", verbose=True)

output = agent.run(input=("Please create a photo of a cat eating a hot dog"
                          "but improve my prompt prior to using an image generator."
                          "Please create a video for it using the improved prompt."))