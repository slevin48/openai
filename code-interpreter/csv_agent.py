from langchain.agents import create_csv_agent
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import StreamlitCallbackHandler
import streamlit as st

st.set_page_config(page_title="CSV Agent",page_icon="📄")

# Set the API key for the openai package
openai_api_key = st.secrets["OPEN_AI_KEY"]

avatar = {"assistant": "🤖", "user": "🐱"}
# Set the API key for the openai package
openai_api_key = st.secrets["OPEN_AI_KEY"]

st.sidebar.title("📄 CSV Agent")

file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if file:
    file_path = "data/"+file.name
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    agent = create_csv_agent(
        llm=ChatOpenAI(
            temperature=0, 
            model="gpt-3.5-turbo-0613", 
            openai_api_key=openai_api_key,
            streaming=True,
            ),
        path=file_path,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )
    file_upload = True
    text = "Ask a question about the data"
else:
    file_upload = False
    text = "Upload a CSV file to get started"

st.sidebar.write("*Example:*")
st.sidebar.write("how many rows are there?")
st.sidebar.write("how many people have more than 3 siblings")
st.sidebar.write("whats the square root of the average age?")

if prompt := st.chat_input(placeholder=text,disabled= not file_upload):
    st.chat_message("user",avatar=avatar["user"]).write(prompt)
    with st.chat_message("assistant",avatar=avatar["assistant"]):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(prompt, callbacks=[st_callback])
        st.write(response)