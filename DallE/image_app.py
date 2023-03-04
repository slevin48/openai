import openai
import streamlit as st

# Set the API key for the openai package
openai.api_key = st.secrets['OPEN_AI_KEY']

st.title("🤖 OpenAI Image")

# Create a text input widget in the Streamlit app
prompt = st.text_input("Enter your message:",
    "a funny corgi")

# Generate an image from the DALL-E model
model = openai.Image.create(
    model="image-alpha-001",
    prompt=prompt,
    n=1,
    size="512x512",
    response_format="url"
)

# Display the generated image in the Streamlit app
st.image(model['data'][0]['url'])