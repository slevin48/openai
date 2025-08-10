# chat_reasoning_write_stream_time.py
# pip install openai streamlit

import os
import time
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

def render_history():
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

def fmt_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}h{m}m{s}s"
    if m:
        return f"{m}m{s}s"
    return f"{s}s"

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

        final_holder = {}    # capture final response
        timing = {           # capture timing
            "overall_start": None,
            "overall_end": None,
            "reason_start": None,
            "reason_end": None,
        }

        with thinking_container:
            # Live reasoning summary in a status box
            with st.status("Reasoning…", state="running", expanded=True) as status:
                thinking_placeholder = st.empty()

                def answer_stream_gen():
                    """
                    Iterate the OpenAI Responses stream ONCE:
                    - yield answer deltas so st.write_stream renders them
                    - update the status box with reasoning deltas
                    - record timing for reasoning window and overall
                    """
                    timing["overall_start"] = time.time()
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
                                if timing["reason_start"] is None:
                                    timing["reason_start"] = time.time()
                                delta = getattr(event, "delta", "") or ""
                                reasoning_buf.append(delta)
                                thinking_placeholder.markdown("".join(reasoning_buf))

                            # Mark end when we see the done event
                            elif et == "response.reasoning_summary_text.done":
                                if timing["reason_end"] is None:
                                    timing["reason_end"] = time.time()

                            # Optional: surface refusals
                            elif et == "response.refusal.delta":
                                thinking_placeholder.markdown("⚠️ The model refused: " + (event.delta or ""))

                        # Capture final response and overall end time
                        final_holder["resp"] = stream.get_final_response()
                        timing["overall_end"] = time.time()
                        # If we had reasoning deltas but no "done" event, close now
                        if timing["reason_start"] is not None and timing["reason_end"] is None:
                            timing["reason_end"] = timing["overall_end"]

                # 4) Stream the assistant's answer *below* the status box
                with answer_container:
                    assistant_text = st.write_stream(answer_stream_gen())

                # 5) Close the status with elapsed time
                # Prefer pure reasoning window; otherwise fall back to overall
                if timing["reason_start"] and timing["reason_end"]:
                    elapsed = timing["reason_end"] - timing["reason_start"]
                    label = f"Thought for {fmt_duration(elapsed)}"
                elif timing["overall_start"] and timing["overall_end"]:
                    elapsed = timing["overall_end"] - timing["overall_start"]
                    label = f"Responded in {fmt_duration(elapsed)}"
                else:
                    label = "Done."

                status.update(label=label, state="complete", expanded=False)

    # 6) Persist assistant message
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})