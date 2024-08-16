import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
 
  system_instruction="you're a chatbot that assists people to book ticket in a museum. you have to answer the doubts of the user about the museum and available ticket options. if the user says the number of people(adult and  children)count and the ticket option you have to call the function with thm as arguments ",
)


history=[
    {
      "role": "user",
      "parts": [
        "hi",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Hello! 👋  Welcome to the [Museum Name] ticketing service. I'm here to help you book your tickets.  \n\nWhat can I help you with today? Are you interested in learning more about the museum,  checking ticket prices, or booking your visit? 😊 \n",
      ],
    },
  ]




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
    chat_session = model.start_chat(history=history)
    # Add user's message to chat
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    history.append({
      "role": "user",
      "parts": [
        prompt,
      ],
    })
    print(history)
    # Display a loading spinner while waiting for the bot's response
    with st.spinner("Waiting for response..."):
        response = chat_session.send_message(prompt)  # Replace this with your actual response generation logic
        history.append({
      "role": "model",
      "parts": [
        response.text,
      ],
    })
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text}) 