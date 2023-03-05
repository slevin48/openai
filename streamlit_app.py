import openai
import json
import streamlit as st

# Set the API key for the openai package
openai.api_key = st.secrets['OPEN_AI_KEY']

st.title('🐱 ChatGPT-like bot 🤖')

st.sidebar.button('New Chat 🐱')
st.sidebar.write('💬 convo 1')

# Initialization
if 'convo' not in st.session_state:
    st.session_state.convo = []

def dumb_chat():
  dummy = [{"role": "user", "content": "Hello!"}, 
          {"role": "assistant", "content": "\n\nHello! How can I assist you today?"}]
  return dummy[1]['content']

def chat(text):
  # Generate a response from the ChatGPT model
  completion = openai.ChatCompletion.create(
      model='gpt-3.5-turbo',
        messages= text
  )
  return completion.choices[0].message.content

# Create a text input widget in the Streamlit app
prompt = st.text_input('Enter your message:', 'Hello!' )

st.session_state.convo.append({'role': 'user', 'content': prompt })

# response = dumb_chat()
response = chat(st.session_state.convo)

st.session_state.convo.append({'role': 'assistant', 'content': response })

# Display the response in the Streamlit app
st.write('🤖 ChatGPT:', response)

if st.checkbox('debug'):
  st.write(st.session_state.convo)

# Write the chat log to a json file
with open('chat/convo1.json','w') as f:
    json.dump(st.session_state.convo, f, indent=4)