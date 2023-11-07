from openai import OpenAI
import json, os
import streamlit as st

st.set_page_config(page_title='Chat 48',page_icon='🤖')

avatar = {"assistant": "🤖", "user": "🐱"}

# Set the API key for the openai package
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=st.secrets['OPEN_AI_KEY'],
)

# Debug
# st.sidebar.write(st.session_state.convo)

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
  st.write(dummy[1]['content'])
  return dummy[1]['content']

def load_model():
  # models = list(client.models.list())
  # models_name = [model.id for model in models]
  with open('models.txt') as f:
    models_name = f.read().splitlines()
  return models_name

def chat_stream(messages,model='gpt-3.5-turbo'):
  # Generate a response from the ChatGPT model
  completion = client.chat.completions.create(
        model=model,
        messages= messages,
        stream = True
  )
  report = []
  res_box = st.empty()
  # Looping over the response
  for resp in completion:
      if resp.choices[0].finish_reason is None:
          # join method to concatenate the elements of the list 
          # into a single string, then strip out any empty strings
          report.append(resp.choices[0].delta.content)
          result = ''.join(report).strip()
          result = result.replace('\n', '')        
          res_box.write(result) 
  return result


# Initialization
if 'convo' not in st.session_state:
    st.session_state.convo = []

n = len(os.listdir('chat'))
if 'id' not in st.session_state:
    st.session_state.id = n+1

id = st.session_state.id

if 'advanced_mode' not in st.session_state:
  st.session_state.advanced_mode = False

st.sidebar.title('ChatGPT-like bot 🤖')

# Add a toggle to enable advanced mode
advanced_mode = st.sidebar.toggle('Advanced mode')
if advanced_mode:
  password = st.sidebar.text_input('Enter password', type='password')
  if password == st.secrets['PASSWORD']:
    st.session_state.advanced_mode = True
  else:
    st.sidebar.warning('Incorrect password')

if st.session_state.advanced_mode:
  models_name = load_model()
  selected_model = st.sidebar.selectbox('Select OpenAI model', models_name)
  # st.write('Selected model:', selected_model)
else:
  selected_model = 'gpt-3.5-turbo'

if st.sidebar.button('New Chat 🐱'):
   new_chat()
for file in sorted(os.listdir('chat')):
  filename = file.replace('.json','')
  if st.sidebar.button(f'💬 {filename}'):
     select_chat(file)

# Display the response in the Streamlit app
for line in st.session_state.convo:
    # st.chat_message(line.role,avatar=avatar[line.role]).write(line.content)
    if line['role'] == 'user':
      st.chat_message('user',avatar=avatar['user']).write(line['content'])
    elif line['role'] == 'assistant':
      st.chat_message('assistant',avatar=avatar['assistant']).write(line['content'])

# Create a text input widget in the Streamlit app
prompt = st.chat_input(f'convo{st.session_state.id}')

if prompt:
  # Append the text input to the conversation
  with st.chat_message('user',avatar='🐱'):
    st.write(prompt)
  st.session_state.convo.append({'role': 'user', 'content': prompt })
  # Query the chatbot with the complete conversation
  with st.chat_message('assistant',avatar='🤖'):
     result = chat_stream(st.session_state.convo,selected_model)
    #  result = dumb_chat()
  # Add response to the conversation
  st.session_state.convo.append({'role':'assistant', 'content':result})
  save_chat(id)

# # Write the chat log to a json file
# if st.sidebar.button('Save chat 🐱🤖'):
#   save_chat(id)