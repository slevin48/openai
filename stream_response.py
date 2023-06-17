import openai
import json, os
import streamlit as st

st.set_page_config(page_title="Stream",page_icon="🤖")

# Set the API key for the openai package
openai.api_key = st.secrets['OPEN_AI_KEY']

st.title('🤖 Stream Response')

user_input = st.text_input("You: ",placeholder = "Ask me anything ...", key="input")

if st.button("Submit", type="primary"):
    # st.markdown("----")
    res_box = st.empty()
    report = []
    # Looping over the response
    for resp in openai.Completion.create(model='text-davinci-003',
                                        prompt=user_input,
                                        max_tokens=120, 
                                        # temperature = 0.5,
                                        stream = True):
        # join method to concatenate the elements of the list 
        # into a single string, then strip out any empty strings
        report.append(resp.choices[0].text)
        result = "".join(report).strip()
        result = result.replace("\n", "")        
        res_box.markdown(f'*{result}*') 