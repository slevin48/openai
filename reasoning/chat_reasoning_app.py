# chat_reasoning_app.py
# pip install openai streamlit

import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Chat + Reasoning (Streamlit + OpenAI Responses)", page_icon="🧠")

st.title("🧠 Chat with Reasoning Summary")

# ---------------------------
# Sidebar controls
# ---------------------------
with st.sidebar:
    st.caption("Models that support reasoning summaries work best here.")
    model = st.selectbox("Model", ["gpt-5", "o3", "o4-mini"], index=0)
    effort = st.selectbox("Reasoning effort", ["low", "medium", "high"], index=1)
    show_summary = st.checkbox("Show reasoning summary (safe)", value=True)
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------
# Session state
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

SYSTEM_PROMPT = "You are a helpful assistant. Keep answers clear and correct."

def make_client():
    key = None
    if hasattr(st, "secrets"):
        key = st.secrets.get("OPENAI_API_KEY", None)
    key = key or os.environ.get("OPENAI_API_KEY")
    return OpenAI(api_key=key) if key else OpenAI()

def safe_reasoning_tokens(usage):
    if not usage:
        return 0
    det = getattr(usage, "output_tokens_details", None)
    if det is not None and hasattr(det, "reasoning_tokens"):
        return det.reasoning_tokens or 0
    det = getattr(usage, "completion_tokens_details", None)  # fallback shape
    if det is not None and hasattr(det, "reasoning_tokens"):
        return det.reasoning_tokens or 0
    return 0

def render_history():
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

render_history()

# ---------------------------
# Chat input
# ---------------------------
if user_text := st.chat_input("Type your message"):
    # 1) Echo user
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # 2) Prepare streaming response
    client = make_client()
    reasoning_param = {"effort": effort}
    if show_summary:
        reasoning_param["summary"] = "auto"  # request provider-safe summary

    # Build conversation for the Responses API
    convo = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in st.session_state.messages:
        convo.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        # 1) Lay out the UI order: thinking/status first, answer second
        thinking_container = st.container()   # appears first
        answer_container = st.container()     # appears below

        # Create the answer placeholder *now* (so we can stream into it),
        # but it will render *below* because of the container order.
        answer_placeholder = answer_container.empty()

        # 2) Open the status box in the thinking container and stream
        with thinking_container:
            with st.status("Reasoning…", state="running", expanded=True) as status:
                thinking_placeholder = st.empty()

                assistant_text = []
                reasoning_text = []

                # 3) Stream the responses
                with client.responses.stream(
                    model=model,
                    input=convo,
                    reasoning=reasoning_param,
                ) as stream:
                    for event in stream:
                        et = event.type

                        # Stream the final answer (shows below the status box)
                        if et == "response.output_text.delta":
                            delta = event.delta or ""
                            assistant_text.append(delta)
                            answer_placeholder.markdown("".join(assistant_text))

                        # Stream the reasoning summary (inside the status box)
                        elif et in ("response.reasoning_summary_text.delta",
                                    "response.reasoning_summary.delta"):
                            delta = getattr(event, "delta", "") or ""
                            reasoning_text.append(delta)
                            thinking_placeholder.markdown("".join(reasoning_text))

                    final = stream.get_final_response()

                # Mark status done
                usage = getattr(final, "usage", None)
                rtoks = safe_reasoning_tokens(usage)
                tok_line = (
                    f"Reasoning tokens: {rtoks}"
                    + (f" • Input: {usage.input_tokens} • Output: {usage.output_tokens} • Total: {usage.total_tokens}"
                    if usage else "")
                )
                status.update(label=f"Reasoning complete. {tok_line}", state="complete", expanded=False)

    # 4) Save assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": "".join(assistant_text)})
