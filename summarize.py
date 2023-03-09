import streamlit as st
import webvtt
import openai
from io import StringIO
import tiktoken

st.set_page_config(page_title="Summarize",page_icon="🤖")

st.title('📝 Teams meeting summaryzer')

# Set the API key for the openai package
openai.api_key = st.secrets['OPEN_AI_KEY']

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def summarize(convo: str) -> str:
    """Returns the summary of a text string."""
    context = 'summarize the following conversation'
    completion = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
      messages=[
        {'role': 'system','content': context},
        {'role': 'user', 'content': convo}
            ]
    )
    return completion.choices[0].message.content


file = st.file_uploader('Upload Teams VTT transcript',type='vtt')

if file is not None:
    data = StringIO(file.getvalue().decode('utf-8'))
    chat = webvtt.read_buffer(data)
    # data = file.getvalue().decode('utf-8')
    # with open('vtt/'+file.name,'w') as f:
    #     f.write(data)
    # caption = webvtt.read('vtt/'+file.name)
    part = st.checkbox('include participants')
    time = st.checkbox('include time')
    str = []
    for caption in chat:
        if part & time:
            str.append(f'{caption.start} --> {caption.end}')
            str.append(caption.raw_text)
        elif time:
            str.append(f'{caption.start} --> {caption.end}')
            str.append(caption.text)
        elif part:
            str.append(caption.raw_text)
        else:
            str.append(caption.text)
    sep = '\n'
    convo = sep.join(str)
        
    convo = st.text_area('vtt file content',convo)
    toknum = num_tokens_from_string(convo,'cl100k_base')
    st.write(toknum,'tokens')
    if (toknum//4096 > 0):
        st.write('Text too long please prune to fit under 4096 tokens')
        sum = st.button('summarize',disabled=True)
    else:
        sum = st.button('summarize')
    if sum & (toknum//4096 < 1):
        st.write(summarize(convo))

else:
    with open('vtt/YannMike_2023-03-08.vtt') as f:
        st.download_button(
            label="Sample VTT file",
            data=f,
            file_name="sample.vtt",
            mime="text/vtt"
          )
