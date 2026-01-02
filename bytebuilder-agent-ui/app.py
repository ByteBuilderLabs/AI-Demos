import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page branding
st.set_page_config(page_title="ByteBuilder Agent", page_icon="🤖")
st.title("ByteBuilder: Implementation")


# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages from the history on every re-run
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def get_ai_response(messages):
    """A generator function to stream tokens from the LLM"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=True,
    )
    for chunk in response:
        # Check if there is actual content in the delta
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content



# Capture user input
if prompt := st.chat_input("Build something..."):
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent Response block
    with st.chat_message("assistant"):
        # 1. Visualize 'Thought Process'
        with st.status("Analyzing request...", expanded=True) as status:
            st.write("Fetching context from vector store...")
            st.write("Synthesizing reasoning paths...")
            status.update(label="Reasoning Complete", state="complete", expanded=False)
        
        # 2. Stream the final response
        response_placeholder = st.empty()
        full_response = ""
        
        for token in get_ai_response(st.session_state.messages):
            full_response += token
            # Update placeholder with a cursor for 'live' feel
            response_placeholder.markdown(full_response + "▌")
        
        # Final render without cursor
        response_placeholder.markdown(full_response)
    
    # Save the assistant's final response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})