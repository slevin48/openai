import openai
import streamlit as st

# Set the API key for the openai package
openai.api_key = st.secrets['OPEN_AI_KEY']

st.title("🤖 ChatGPT-like bot 🐱 ")

# Create a text input widget in the Streamlit app
prompt = st.chat_input("Say something")
if prompt:
    with st.chat_message("🐱"):
        st.write(prompt)

    # Generate a response from the ChatGPT model
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt }
                ]
    )

    # Display the response in the Streamlit app
    with st.chat_message("🤖"):
        st.write(completion.choices[0].message.content)