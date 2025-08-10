# pip install openai streamlit
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Reasoning Demo", page_icon="🧠", layout="wide")

st.title("🧠 Reasoning Models — Live Thinking + Answer")


with st.sidebar:
    model = st.selectbox("Model", ["gpt-5", "o3", "o4-mini"], index=0)
    effort = st.selectbox("Reasoning effort", ["low", "medium", "high"], index=1)
    prompt = st.text_area("Your prompt", "Solve 24x + 18 = 6(3x + 7) step by step.", height=120)
    go = st.button("Run")

with st.expander("Show reasoning (live)", expanded=True):
    reasoning_placeholder = st.empty()

answer_placeholder = st.empty()

if go and prompt.strip():
    client = OpenAI()  # uses OPENAI_API_KEY (env var or st.secrets)

    thinking_buf = []
    answer_buf = []

    # Stream both: reasoning summary + answer text
    with client.responses.stream(
        model=model,
        input=prompt,
        reasoning={"effort": effort, "summary": "auto"},  # ask for a safe reasoning summary
        text={"format": {"type": "text"}},                 # normal text output
    ) as stream:
        for event in stream:
            t = event.type
            if t == "response.reasoning_summary_text.delta":
                thinking_buf.append(event.delta)
                reasoning_placeholder.markdown("".join(thinking_buf))
            elif t == "response.output_text.delta":
                answer_buf.append(event.delta)
                answer_placeholder.markdown("".join(answer_buf))
        final = stream.get_final_response()