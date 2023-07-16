import openai
import json, os
import streamlit as st

st.set_page_config(page_title="Stream",page_icon="🤖")

def chat_stream(text):
  # Generate a response from the ChatGPT model
  messages = [{"role": "user", "content": text}]
  completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= messages,
        stream = True
  )
  return completion 

# def llm_stream(text):
#     completion = openai.Completion.create(
#         model="text-davinci-003",
#         prompt=text,
#         max_tokens=120, 
#         # temperature = 0.5,
#         stream = True)
#     return completion

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role":"assistant", "content":"How can I help you?"}]

# Set the API key for the openai package
openai.api_key = st.secrets["OPEN_AI_KEY"]

st.title("🤖 Stream Response")
st.write("What is the meaning of life?")
prompt = st.chat_input("Ask me anything ...")

if prompt:
    with st.chat_message("user",avatar="🐱"):
        st.write(prompt)
    report = []
    with st.chat_message("assistant",avatar="🤖"):
        res_box = st.empty()
        # Looping over the response
        for resp in chat_stream(prompt):
                if resp.choices[0].finish_reason is None:
                    # join method to concatenate the elements of the list 
                    # into a single string, then strip out any empty strings
                    report.append(resp.choices[0].delta.content)
                    result = "".join(report).strip()
                    result = result.replace("\n", "")        
                    res_box.write(result) 
