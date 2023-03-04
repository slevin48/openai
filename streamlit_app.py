import openai
import streamlit as st

# Set the API key for the openai package
openai.api_key = st.secrets['OPEN_AI_KEY']

st.title("🤖 ChatGPT-like bot 🐱 ")

# Create a text input widget in the Streamlit app
prompt = st.text_input("Enter your message:", "Hello!" )

# Generate a response from the ChatGPT model
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
      messages=[
          {"role": "user", "content": prompt }
            ]
)

# Display the response in the Streamlit app
st.write("🤖 ChatGPT:", completion.choices[0].message.content)

