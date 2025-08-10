from openai import OpenAI
import streamlit as st
import json, datetime, io, zipfile, time

st.set_page_config(page_title='Chat with Bernard', page_icon='🤖')

avatar = {"assistant": "🤖", "user": "🐱"}

client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

# ----------------------------
# Helpers / Functions
# ----------------------------
def new_chat():
    st.session_state.convo = []

def load_model():
    with open('models.txt') as f:
        models_name = f.read().splitlines()
    return models_name

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

def fmt_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}h{m}m{s}s"
    if m:
        return f"{m}m{s}s"
    return f"{s}s"

# ----------------------------
# Initialization
# ----------------------------
if 'convo' not in st.session_state:
    st.session_state.convo = []

st.sidebar.title('Chat 🤖')

# ----------------------------
# Gate with Login
# ----------------------------
if not st.user.is_logged_in:
    st.write("Please login to use the chat (No user data is stored).")
    st.button("Login with Google", on_click=st.login, type="primary")

else:
    # User is logged in
    with st.sidebar:
        st.write(f"Welcome, {st.user.name}! 👋")
        st.image(st.user.picture, width=50)
        st.button("Logout", on_click=st.logout)

        # Advanced mode
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
            # Default to a lightweight general model; you can switch this to a reasoning model if you like
            selected_model = 'gpt-5-mini'

        if st.button('New Chat 🐱'):
            new_chat()

    # ----------------------------
    # Render history
    # ----------------------------
    for line in st.session_state.convo:
        if line['role'] == 'user':
            st.chat_message('user', avatar=avatar['user']).write(line['content'])
        elif line['role'] == 'assistant':
            st.chat_message('assistant', avatar=avatar['assistant']).write(line['content'])

    # ----------------------------
    # Input
    # ----------------------------
    prompt = st.chat_input('Your message')

    if prompt:
        # Add user message
        with st.chat_message('user', avatar='🐱'):
            st.write(prompt)
        st.session_state.convo.append({'role': 'user', 'content': prompt})

        # Assistant response (reasoning summary first, answer second)
        with st.chat_message('assistant', avatar='🤖'):
            thinking_container = st.container()   # appears first
            answer_container = st.container()     # appears below

            # Track timing
            timing = {
                "overall_start": None,
                "overall_end": None,
                "reason_start": None,
                "reason_end": None,
            }
            final_holder = {}

            with thinking_container:
                # Live reasoning summary while we stream the final answer below
                with st.status("Reasoning…", state="running", expanded=True) as status:
                    thinking_placeholder = st.empty()

                    # Build the generator that streams once and feeds both UI areas
                    def answer_stream_gen():
                        """
                        Iterate the OpenAI Responses stream ONCE:
                        - yield answer deltas so st.write_stream renders them
                        - update the status box with reasoning deltas
                        - measure reasoning duration
                        """
                        timing["overall_start"] = time.time()
                        reasoning_buf = []

                        # Request a provider-safe reasoning summary; effort=medium by default
                        reasoning_param = {"effort": "medium", "summary": "auto"}

                        with client.responses.stream(
                            model=selected_model,
                            input=st.session_state.convo,   # your chat history (list of {role, content})
                            reasoning=reasoning_param,
                        ) as stream:
                            for event in stream:
                                et = event.type

                                # Final answer (yield to write_stream)
                                if et == "response.output_text.delta":
                                    yield event.delta or ""

                                # Reasoning summary deltas (safe)
                                elif et in ("response.reasoning_summary_text.delta",
                                            "response.reasoning_summary.delta"):
                                    if timing["reason_start"] is None:
                                        timing["reason_start"] = time.time()
                                    delta = getattr(event, "delta", "") or ""
                                    reasoning_buf.append(delta)
                                    thinking_placeholder.markdown("".join(reasoning_buf))

                                # Mark reasoning end if we see the done event
                                elif et == "response.reasoning_summary_text.done":
                                    if timing["reason_end"] is None:
                                        timing["reason_end"] = time.time()

                                # Optional: refusals show in the status box
                                elif et == "response.refusal.delta":
                                    thinking_placeholder.markdown("⚠️ The model refused: " + (event.delta or ""))

                            # Capture final response and total time
                            final_holder["resp"] = stream.get_final_response()
                            timing["overall_end"] = time.time()
                            # If we saw reasoning start but not done, close it now
                            if timing["reason_start"] is not None and timing["reason_end"] is None:
                                timing["reason_end"] = timing["overall_end"]

                    # Stream the assistant's answer *below* the status box
                    with answer_container:
                        assistant_text = st.write_stream(answer_stream_gen())

                    # Close status with elapsed time
                    if timing["reason_start"] and timing["reason_end"]:
                        elapsed = timing["reason_end"] - timing["reason_start"]
                        label = f"Thought for {fmt_duration(elapsed)}"
                    elif timing["overall_start"] and timing["overall_end"]:
                        elapsed = timing["overall_end"] - timing["overall_start"]
                        label = f"Responded in {fmt_duration(elapsed)}"
                    else:
                        label = "Done."
                    status.update(label=label, state="complete", expanded=False)

        # Save assistant reply to history
        st.session_state.convo.append({'role': 'assistant', 'content': assistant_text})

    # ----------------------------
    # Save chat ZIP
    # ----------------------------
    with st.sidebar:
        st.download_button('Save Chat 📦', data=export_chat_zip(),
                           file_name='chat.zip', mime='application/zip')