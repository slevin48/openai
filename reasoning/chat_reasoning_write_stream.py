# chat_reasoning_write_stream.py
# pip install openai streamlit

import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Chat + Reasoning (write_stream)", page_icon="🧠")

st.title("🧠 Chat with Reasoning Summary")
SYSTEM_PROMPT = "You are a helpful assistant. Keep answers clear and correct."

# ---------------------------
# Sidebar controls
# ---------------------------
with st.sidebar:
    st.caption("Models that expose a reasoning summary work best.")
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

def make_client():
    key = (getattr(st, "secrets", {}) or {}).get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
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

    # 2) Build conversation for the Responses API
    convo = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in st.session_state.messages:
        convo.append({"role": m["role"], "content": m["content"]})

    client = make_client()
    reasoning_param = {"effort": effort}
    if show_summary:
        reasoning_param["summary"] = "auto"  # request provider-safe summary

    # 3) Assistant message UI — thinking/status first, answer second
    with st.chat_message("assistant"):
        thinking_container = st.container()   # shows first
        answer_container = st.container()     # shows below

        final_holder = {}  # to capture the final response object for usage

        with thinking_container:
            with st.status("Reasoning…", state="running", expanded=True) as status:
                thinking_placeholder = st.empty()

                def answer_stream_gen():
                    """
                    Iterate the OpenAI Responses stream ONCE:
                    - yield answer deltas so st.write_stream renders them
                    - update the status box with reasoning deltas
                    """
                    reasoning_buf = []
                    with client.responses.stream(
                        model=model,
                        input=convo,
                        reasoning=reasoning_param,
                    ) as stream:
                        for event in stream:
                            et = event.type

                            # Stream the *final answer* as text chunks
                            if et == "response.output_text.delta":
                                yield event.delta or ""

                            # Stream the *reasoning summary* into the status box
                            elif et in ("response.reasoning_summary_text.delta",
                                        "response.reasoning_summary.delta"):
                                delta = getattr(event, "delta", "") or ""
                                reasoning_buf.append(delta)
                                thinking_placeholder.markdown("".join(reasoning_buf))

                            # Optional: surface refusals
                            elif et == "response.refusal.delta":
                                thinking_placeholder.markdown("⚠️ The model refused: " + (event.delta or ""))

                        # Capture the final response for token accounting
                        final_holder["resp"] = stream.get_final_response()

                # 4) Stream the assistant's answer *below* the status box
                with answer_container:
                    assistant_text = st.write_stream(answer_stream_gen())

                # 5) Close the status with token info
                final = final_holder.get("resp")
                usage = getattr(final, "usage", None)
                rtoks = safe_reasoning_tokens(usage)
                tok_line = (
                    f"Reasoning tokens: {rtoks}"
                    + (f" • Input: {usage.input_tokens} • Output: {usage.output_tokens} • Total: {usage.total_tokens}"
                       if usage else "")
                )
                status.update(label=f"Reasoning complete. {tok_line}", state="complete", expanded=False)

    # 6) Persist assistant message
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
