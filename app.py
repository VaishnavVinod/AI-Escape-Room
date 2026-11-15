from __future__ import annotations
import streamlit as st
from game_engine import new_state, resolve_action, state_summary
from llm import generate, gemini_available

st.set_page_config(page_title="AI Escape Room", page_icon="🗝️", layout="centered")
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background: radial-gradient(ellipse at top, #202a44 0%, #111827 60%, #0b1020 100%); color:#f5f3ed}
.block-container {max-width: 920px; padding-top: 2rem}
.stChatMessage {border:1px solid #39445d; border-radius:14px}
[data-testid="stSidebar"] {background:#111827}
</style>
""", unsafe_allow_html=True)
st.title("🗝️ The Last Library")
st.caption("A small AI-powered escape room — compare the freeform Version 1 with the rule-checked Version 2.")

with st.sidebar:
    st.subheader("How to play")
    st.write("Describe what you want to do in plain language. Examine the room, find the drawer combination, collect the key, discover the exit code, then escape.")
    st.info("Version 1 lets the AI Game Master decide outcomes. Version 2 validates every game action in Python before the AI narrates it.")
    if gemini_available(): st.success("Gemini connected")
    else: st.warning("Gemini key not set — local narration is active")
    st.caption("Never put your API key in source code. Use the local .env file.")

v1, v2 = st.tabs(["Version 1 · Freeform", "Version 2 · Rule-checked"])

if "v1_history" not in st.session_state:
    st.session_state.v1_history = [{"role":"assistant", "content":"You wake in a locked library. A desk, bookshelf, painting, locked drawer and heavy exit door surround you. What do you do?"}]
if "v1_turns" not in st.session_state: st.session_state.v1_turns = []
if "v2_state" not in st.session_state: st.session_state.v2_state = new_state()
if "v2_history" not in st.session_state:
    st.session_state.v2_history = [{"role":"assistant", "content":"You wake in a locked library. A desk, bookshelf, painting, locked drawer and heavy exit door surround you. What do you do?"}]

with v1:
    st.markdown("#### Version 1: AI Game Master")
    st.write("The model receives the story and conversation, then decides how to respond. This version is intentionally less constrained.")
    if st.button("Restart Version 1", key="restart1"):
        st.session_state.v1_history = [{"role":"assistant", "content":"A new game begins. You wake in the locked library. What do you do?"}]
        st.session_state.v1_turns = []
        st.rerun()
    for m in st.session_state.v1_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    prompt = st.chat_input("What do you do?", key="chat1")
    if prompt:
        st.session_state.v1_history.append({"role":"user", "content":prompt})
        instructions = ("You are the Game Master for a library escape-room game. The room contains a desk, bookshelf, painting, locked drawer, and keypad exit door. "
          "The intended path is: examine bookshelf to find drawer code 2413; open drawer with that code to get a brass key; examine painting to find exit code 0412; use key and code 0412 to escape. "
          "Keep the tone atmospheric and remember conversation context. Respond to the player's latest action. Do not give away the solution unless the player discovers it.")
        answer = generate(instructions + "\nPlayer action: " + prompt, "A floorboard creaks in the quiet library. You can examine the desk, bookshelf, painting, drawer or exit door.", st.session_state.v1_history[:-1])
        st.session_state.v1_history.append({"role":"assistant", "content":answer})
        st.session_state.v1_turns.append(prompt)
        st.rerun()

with v2:
    st.markdown("#### Version 2: Python checks the rules")
    st.write("Python owns the inventory, clues, puzzle results and exit lock. The model can only phrase the outcome of a validated action.")
    with st.expander("Current structured state"):
        st.json({k:v for k,v in st.session_state.v2_state.items() if k != "actions"})
    if st.button("Restart Version 2", key="restart2"):
        st.session_state.v2_state = new_state()
        st.session_state.v2_history = [{"role":"assistant", "content":"A new game begins. You wake in the locked library. What do you do?"}]
        st.rerun()
    for m in st.session_state.v2_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    prompt2 = st.chat_input("What do you do?", key="chat2")
    if prompt2:
        st.session_state.v2_history.append({"role":"user", "content":prompt2})
        outcome = resolve_action(st.session_state.v2_state, prompt2)
        # Rules and outcome are fixed by Python. Gemini may add style only; its output is not parsed as a game action.
        narration = generate(
            "Rewrite this game outcome in one or two atmospheric sentences. Preserve every fact exactly. Do not add objects, clues, items, codes, actions, or state changes.\n"
            f"Authoritative outcome: {outcome.text}\nGame state: {state_summary(st.session_state.v2_state)}",
            outcome.text,
        )
        st.session_state.v2_history.append({"role":"assistant", "content":narration})
        st.rerun()

st.divider()
st.caption("Designed for a course assignment. Gemini is optional; local deterministic responses work without credentials.")
