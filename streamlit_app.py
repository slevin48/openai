import openai
import json, os
import streamlit as st

st.set_page_config(page_title="Chat 48",page_icon="🤖")

# Set the API key for the openai package
openai.api_key = st.secrets['OPEN_AI_KEY']

# Functions
def new_chat():
   st.session_state.convo = []
   st.session_state.id += 1

def save_chat(n):
  file_path = f'chat/convo{n}.json'
  with open(file_path,'w') as f:
    json.dump(st.session_state.convo, f, indent=4)

def select_chat(file):
  st.session_state.convo = []
  with open(f'chat/{file}') as f:
    st.session_state.convo = json.load(f)
  st.session_state.id = int(file.replace('.json','').replace('convo',''))

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
    st.session_state.id = n+1

id = st.session_state.id

if 'edit' not in st.session_state:
    st.session_state.edit = False

st.title('🐱 ChatGPT-like bot 🤖')

if st.button('edit'):
  st.session_state.edit = not st.session_state.edit

if st.session_state.edit:
# if st.checkbox('edit'):
  # # change to st.form
  # col1,col2 = st.columns([1,1])
  # with col1:
  #   name = st.text_input('Change name',label_visibility='collapsed',value=f'convo{st.session_state.id}')
  # with col2:
  #   if st.button('Save name'):
  #     os.rename(f'chat/convo{st.session_state.id}.json', f'chat/{name}.json')
  # with st.form('edit'):
  #   col1,col2 = st.columns([1,1])
  #   with col1:
  #     name = st.text_input('Change name',label_visibility='collapsed',value=f'convo{st.session_state.id}')
  #   with col2:
  #     changed = st.form_submit_button(label='Submit')
  with st.form('change'):
    name = st.text_input('Change name',label_visibility='collapsed',value=f'convo{st.session_state.id}')
    changed = st.form_submit_button(label='Submit')
    if changed:
      os.rename(f'chat/convo{st.session_state.id}.json', f'chat/{name}.json')

if st.sidebar.button('New Chat 🐱'):
   new_chat()
for file in sorted(os.listdir('chat')):
  filename = file.replace('.json','')
  if st.sidebar.button(f'💬 {filename}'):
     select_chat(file)


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

# # Debug
# st.write(st.session_state.convo)

# # Write the chat log to a json file
# if st.sidebar.button('Save chat 🐱🤖'):
#   save_chat(id)