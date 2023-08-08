import openai
import json, os
import streamlit as st

st.set_page_config(page_title="Stream",page_icon="🤖")

# Set the API key for the openai package
openai.api_key = st.secrets["OPEN_AI_KEY"]

def chat_stream(messages):
  # Generate a response from the ChatGPT model
  completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
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

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role":"assistant", "content":"How can I help you?"}]

# Display the response in the Streamlit app
for line in st.session_state["messages"]:
    if line['role'] == 'user':
      with st.chat_message('user',avatar='🐱'):
        st.write(line['content'])
    else:
      with st.chat_message('assistant',avatar='🤖'):
        st.write(line['content'])


prompt = st.chat_input("Ask me anything ...")

if prompt:
    with st.chat_message("user",avatar="🐱"):
        st.write(prompt)
    st.session_state["messages"].append({"role":"user", "content":prompt})
    with st.chat_message("assistant",avatar="🤖"):
        result = chat_stream(st.session_state.messages)        
    st.session_state["messages"].append({"role":"assistant", "content":result})
