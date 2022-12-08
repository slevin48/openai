import openai
import streamlit as st

# Set the API key for the openai package
openai.api_key = st.secrets['OPEN_AI_KEY']

st.title("🤖 GPT Chat ")

# Create a text input widget in the Streamlit app
prompt = st.text_input("Enter your message:")

# Generate a response from the ChatGPT model
completion = openai.Completion.create(
    engine="text-davinci-002",
    prompt=prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.5,
)

# Display the response in the Streamlit app
st.write("ChatGPT:", completion.choices[0].text)

