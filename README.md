# 🤖 OpenAI

🐱ChatGPT-like Bot🤖 with OpenAI API

[chat48.streamlit.app](https://chat48.streamlit.app/)

## ChatGPT (New GPT 3.5 turbo API) [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chat48.streamlit.app/)

https://user-images.githubusercontent.com/12418115/222990188-9cb2ee4a-29c6-4822-995e-f89b1f3225c1.webm

```python
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
```

## Summary [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://teams-summarizer.streamlit.app/)

https://user-images.githubusercontent.com/12418115/229315555-c9d2077a-a2ed-4538-816c-ce0b9cece761.webm

## Question Answering [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ask-impromptu.streamlit.app/)

https://github.com/slevin48/openai/assets/12418115/b37ec63c-1a7d-4c81-a4b0-5f10f7ceb428

## Functions Calling [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ask-smith.streamlit.app/)

https://github.com/slevin48/openai/assets/12418115/f8e0a3e6-50c9-4eb9-961f-177000a2d7f4

## [DALL-E](DallE/README.md) [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://openai-image.streamlit.app/)

![corgi](img/funny%20corgi%20in%20a%20cartoon%20style.png)

## Resources:

* [Introducing ChatGPT and Whisper APIs](https://openai.com/blog/introducing-chatgpt-and-whisper-apis)
* [Chat completions](https://platform.openai.com/docs/guides/chat/introduction)
* [Awesome ChatGPT API](https://awesome-chatgpt-api.top/posts/the-awesome/)