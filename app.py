import os
import streamlit as st
import google.generativeai as genai

# Initialize session state for messages if not already done
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from the session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input for user's message
prompt = st.chat_input("Type your message...")

if prompt:
    # Add user's message to chat
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display a loading spinner while waiting for the bot's response
    with st.spinner("Waiting for response..."):
        response = "Hello!"  # Replace this with your actual response generation logic
        # Add bot's response to chat
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})