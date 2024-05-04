# Learn more: https://python.langchain.com/docs/integrations/toolkits/python/
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_experimental.tools import PythonREPLTool
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import StreamlitCallbackHandler
import streamlit as st

st.set_page_config(page_title="Python and Chat",page_icon="🐍")

# Set the API key for the openai package
openai_api_key = st.secrets["OPENAI_API_KEY"]
instructions = """You are an agent designed to write and execute python code to answer questions.
You have access to a python REPL, which you can use to execute python code.
If you get an error, debug your code and try again.
Only use the output of your code to answer the question. 
You might know the answer without running any code, but you should still run the code to get the answer.
If it does not seem like you can write code to answer the question, just return "I don't know" as the answer.
"""
base_prompt = hub.pull("langchain-ai/openai-functions-template")
prompt = base_prompt.partial(instructions=instructions)
tools = [PythonREPLTool()]
avatar = {"assistant": "🐍", "user": "🐱"}
llm =ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613", streaming=True)
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

st.sidebar.title("🐍 Python and Chat 🐱")
st.sidebar.write("*Example:*")
st.sidebar.write("What is the 10th fibonacci number?")
st.sidebar.write("""Understand, write a single neuron neural network in PyTorch.
Take synthetic data for y=2x. Train for 1000 epochs and print every 100 epochs.
Return prediction for x = 5""")

# st.sidebar.write(st.session_state.messages)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"],avatar=avatar[msg["role"]]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user",avatar=avatar["user"]).write(prompt)
    with st.chat_message("assistant",avatar=avatar["assistant"]):
        st_callback = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)
        response = agent_executor.invoke({"input":prompt}, callbacks=[st_callback])
        st.session_state.messages.append({"role": "assistant", "content": response["output"]})
        st.write(response["output"])
