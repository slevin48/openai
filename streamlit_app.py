import openai
import json, os
import streamlit as st

# Set the API key for the openai package
openai.api_key = st.secrets['OPEN_AI_KEY']

# Functions
def new_chat(n):
  #  file_path = f'chat/convo{n+1}.json'
  #  open(file_path, 'w').close()
   st.session_state.convo = []
   st.session_state.id += 1

def save_chat(n):
  file_path = f'chat/convo{n}.json'
  with open(file_path,'w') as f:
    json.dump(st.session_state.convo, f, indent=4)

def dumb_chat():
  with open('fake/dummy1.json') as f:
    dummy = json.load(f)
  return dummy[1]['content']

def chat(text):
  # Generate a response from the ChatGPT model
  completion = openai.ChatCompletion.create(
      model='gpt-3.5-turbo',
        messages= text
  )
  return completion.choices[0].message.content


# Initialization
if 'convo' not in st.session_state:
    st.session_state.convo = []

n = len(os.listdir('chat'))
if 'id' not in st.session_state:
    st.session_state.id = n

id = st.session_state.id


st.title('🐱 ChatGPT-like bot 🤖')

if st.sidebar.button('New Chat 🐱'):
   new_chat(n)
for file in sorted(os.listdir('chat')):
  st.sidebar.write('💬',file.replace('.json',''))
# st.sidebar.write(f'💬 convo{id}')
# st.sidebar.write(f'{n} conversations')


# Create a text input widget in the Streamlit app
prompt = st.text_input(f'convo{st.session_state.id}')

if prompt:
  # Append the text input to the conversation
  st.session_state.convo.append({'role': 'user', 'content': prompt })

  # Query the chatbot with the complete conversation
  # response = dumb_chat()
  response = chat(st.session_state.convo)

  # Add response to the conversation
  st.session_state.convo.append({'role': 'assistant', 'content': response })

  save_chat(id)

# Display the response in the Streamlit app
for line in st.session_state.convo:
    if line['role'] == 'user':
      st.write('🐱',line['content'])
    else:
        st.write('🤖',line['content'])

# Debug
# st.write(st.session_state.convo)

# # Write the chat log to a json file
# if st.sidebar.button('Save chat 🐱🤖'):
#   save_chat(id)