import streamlit as st
from openai import OpenAI
import time
import datetime

st.sidebar.title('🤖 GPTs')
avatar = {"assistant": "🤖", "user": "🐱"}
tools = {"code_interpreter": "🐍", "retrieval": "🔎"}
client = OpenAI(
    api_key=st.secrets['OPEN_AI_KEY'],
)

if 'messages' not in st.session_state:
    st.session_state.messages = None
if 'run' not in st.session_state:
    st.session_state.run = None
if 'thread' not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread = thread
thread = st.session_state.thread

st.sidebar.write('## Assistants')
list_of_assistants = client.beta.assistants.list()
# st.write(list(list_of_assistants))

# assistant_id = st.sidebar.selectbox('Select Assistant', [assistant.id for assistant in list_of_assistants])
assistant = st.sidebar.selectbox('Select Assistant', list_of_assistants, format_func=lambda assistant: assistant.name)
# st.sidebar.write(assistant)
# my_assistant = client.beta.assistants.retrieve(assistant.id)
# st.sidebar.write(my_assistant)
assistant_tools = [tool.type for tool in assistant.tools]
assistant_tools_emojis = [tools[tool.type] for tool in assistant.tools]

# st.write(f'# {assistant.name}')
st.sidebar.write(f'*({assistant.id})*')
st.sidebar.write(f'**Instructions**:\n{assistant.instructions}')
st.sidebar.write(f'**Model**:\n{assistant.model}')
st.sidebar.write(f'**Tools**:\n{list(zip(assistant_tools, assistant_tools_emojis))}')

## 1 - Create Thread
# if st.sidebar.button('Create Thread'):
#     thread = client.beta.threads.create()
#     st.session_state.thread = thread
#     st.sidebar.write(thread.id)

st.sidebar.write('## Thread')
# st.sidebar.write(thread)
st.sidebar.write(f'*{thread.id}*')
st.sidebar.write(f'Created at {datetime.datetime.fromtimestamp(thread.created_at)}')

## 2 - Add a message
# if prompt := st.chat_input():
prompt = st.text_input('Prompt')
if st.button('Add message'):
    messages = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )
    st.session_state.messages = messages
    st.write(messages)

## 3 - Run
if st.button('Run the thread'):
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        # instructions="Please address the user as Jane Doe. The user has a premium account."
    )
    st.session_state.run = run
    st.write(run)

if st.session_state.run is not None:
    ## 4 - Get run's steps
    if st.button('Get steps'):
        run_steps = client.beta.threads.runs.steps.list(
            thread_id=thread.id,
            run_id=st.session_state.run.id
        )
        st.write(run_steps.data[0].dict())

    ## 5 - Get run's status
    if st.button('Get status'):
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=st.session_state.run.id
        )
        st.write(run.status)

## 6 - Get messages
if st.button('Get Messages'):
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    st.session_state.messages = messages
    # st.write(messages.data[-1])
    # st.write(messages.data[::-1])
    for line in messages.data[::-1]:
        st.chat_message(line.role,avatar=avatar[line.role]).write(line.content[0].text.value)
        

## X - More

st.sidebar.expander('Messages').write(st.session_state.messages)

st.sidebar.expander('Run').write(st.session_state.run)

st.sidebar.write('## Prompt examples')
st.sidebar.write("How to write text in string arrays with MATLAB?")
st.sidebar.write("How to solve the equation `3x + 11 = 14`?")