import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Reasoning Models — Live Answer + Thinking", page_icon="🧠", layout="centered")
st.title("🧠 Reasoning Models — Live Answer + Thinking")

# ---- Sidebar controls ----
with st.sidebar:
    st.caption("Models that support reasoning summaries work best here.")
    model = st.selectbox(
        "Model",
        ["gpt-5-thinking", "o3", "o4-mini"],  # include a fast fallback
        index=0,
    )
    effort = st.selectbox("Reasoning effort", ["low", "medium", "high"], index=1)
    show_summary = st.checkbox("Request reasoning summary", value=True)
    go = st.button("Run")

# ---- Prompt input ----
prompt = st.text_area(
    "Your prompt",
    "Solve 24x + 18 = 6(3x + 7) step by step.",
    height=140,
)

# ---- Output areas ----
answer_title = st.markdown("### Answer")
answer_placeholder = st.empty()
with st.expander("Show reasoning (live)", expanded=True):
    reasoning_placeholder = st.empty()

status_placeholder = st.empty()

# ---- Helpers ----
def safe_reasoning_tokens(usage):
    """
    Pull reasoning token counts from usage if present.
    These are counted but not returned as content.
    """
    if usage is None:
        return 0
    # Responses API usage
    det = getattr(usage, "output_tokens_details", None)
    if det is not None and hasattr(det, "reasoning_tokens"):
        return det.reasoning_tokens or 0
    # Chat Completions fallback shape (if you ever switch)
    det = getattr(usage, "completion_tokens_details", None)
    if det is not None and hasattr(det, "reasoning_tokens"):
        return det.reasoning_tokens or 0
    return 0

def make_client():
    # Use st.secrets if available; otherwise fall back to env var
    key = st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") else os.environ.get("OPENAI_API_KEY")
    return OpenAI(api_key=key) if key else OpenAI()

# ---- Run ----
if go and prompt.strip():
    client = make_client()

    thinking_buf = []
    answer_buf = []

    # Ask for a safe reasoning summary if requested
    reasoning_param = {"effort": effort}
    if show_summary:
        reasoning_param["summary"] = "auto"  # best available summary

    try:
        # Stream both: reasoning summary + answer text
        with client.responses.stream(
            model=model,
            input=prompt,
            reasoning=reasoning_param,
        ) as stream:
            for event in stream:
                t = event.type

                # Main answer text (visible to user)
                if t == "response.output_text.delta":
                    answer_buf.append(event.delta or "")
                    answer_placeholder.markdown("".join(answer_buf))

                # Reasoning summary (safe, provider-exposed)
                elif t in ("response.reasoning_summary_text.delta", "response.reasoning_summary.delta"):
                    # .reasoning_summary_text.delta is the plain-text stream.
                    # Some SDKs may surface .reasoning_summary.delta with a `delta` string too.
                    delta = getattr(event, "delta", None)
                    if isinstance(delta, str):
                        thinking_buf.append(delta)
                        reasoning_placeholder.markdown("".join(thinking_buf))

                # Optional: finalized summary text
                elif t == "response.reasoning_summary_text.done":
                    # could mark completion UI if you want
                    pass

                # Optional: handle refusals/errors streamed as events
                elif t == "response.refusal.delta":
                    reasoning_placeholder.markdown("⚠️ The model refused: " + (event.delta or ""))

                elif t == "response.error":
                    status_placeholder.error(getattr(event, "error", "Unknown streaming error"))

            # After stream completes, you can access usage in the final response:
            final = stream.get_final_response()

        usage = getattr(final, "usage", None)
        rtoks = safe_reasoning_tokens(usage)
        if usage:
            status_placeholder.caption(
                f"Reasoning tokens: {rtoks} • Input: {usage.input_tokens} • Output: {usage.output_tokens} • Total: {usage.total_tokens}"
            )

    except Exception as e:
        status_placeholder.error(f"Error: {e}")