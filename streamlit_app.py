from openai import OpenAI
import streamlit as st
import json, datetime, io, zipfile

st.set_page_config(page_title='Chat 48',page_icon='🤖')

avatar = {"assistant": "🤖", "user": "🐱"}

client = OpenAI(
    api_key=st.secrets['OPENAI_API_KEY'],
)

# Functions
def new_chat():
   st.session_state.convo = []
  
def load_model():
  with open('models.txt') as f:
    models_name = f.read().splitlines()
  return models_name

def chat_stream(messages,model='gpt-4o-mini'):
  completion = client.chat.completions.create(
        model=model,
        messages= messages,
        stream = True
  )
  report = []
  res_box = st.empty()
  for resp in completion:
      if resp.choices[0].finish_reason is None:
          report.append(resp.choices[0].delta.content)
          result = ''.join(report).strip()
          result = result.replace('\n', '')        
          res_box.write(result) 
  return result

def export_chat_zip():
    # Create an in-memory ZIP with the conversation JSON
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
         timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
         file_name = f'chat_{timestamp}.json'
         chat_json = json.dumps(st.session_state.convo, indent=4)
         zf.writestr(file_name, chat_json)
    mem_zip.seek(0)
    return mem_zip.getvalue()

# Initialization: use session_state for conversation only
if 'convo' not in st.session_state:
    st.session_state.convo = []

st.sidebar.title('Chat 🤖')


# Gate with Login
if not st.user.is_logged_in:
    st.write("Please login to use the chat (No user data is stored).")
    st.button("Login with Google", on_click=st.login, type="primary")
else:
    # User is logged in
    with st.sidebar:
        st.write(f"Welcome, {st.user.name}! 👋")
        st.image(st.user.picture, width=50)
        st.button("Logout", on_click=st.logout)

        # Add a toggle to enable advanced mode
        advanced_mode = st.toggle('Advanced mode')
        if advanced_mode:
          password = st.text_input('Enter password', type='password')
          if password == st.secrets['PASSWORD']:
            st.session_state.advanced_mode = True
          else:
            st.warning('Incorrect password')

        if st.session_state.get('advanced_mode'):
          models_name = load_model()
          selected_model = st.selectbox('Select OpenAI model', models_name)
        else:
          selected_model = 'gpt-4o-mini'

        if st.button('New Chat 🐱'):
          new_chat()

    # Display the response in the Streamlit app
    for line in st.session_state.convo:
        # st.chat_message(line.role,avatar=avatar[line.role]).write(line.content)
        if line['role'] == 'user':
          st.chat_message('user',avatar=avatar['user']).write(line['content'])
        elif line['role'] == 'assistant':
          st.chat_message('assistant',avatar=avatar['assistant']).write(line['content'])

    # Create a text input widget in the Streamlit app
    prompt = st.chat_input('Your message')

    if prompt:
      # Append the text input to the conversation
      with st.chat_message('user',avatar='🐱'):
        st.write(prompt)
      st.session_state.convo.append({'role': 'user', 'content': prompt })
      # Query the chatbot with the complete conversation
      with st.chat_message('assistant',avatar='🤖'):
        result = chat_stream(st.session_state.convo, selected_model)
        #  result = dumb_chat()
      # Add response to the conversation
      st.session_state.convo.append({'role':'assistant', 'content':result})
          
    # Debug
    # st.sidebar.write(st.session_state.convo)

    # Add a button to save the chat as a ZIP file
    with st.sidebar:
        st.download_button('Save Chat 📦', data=export_chat_zip(), file_name='chat.zip', mime='application/zip')