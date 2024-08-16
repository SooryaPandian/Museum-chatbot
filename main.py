import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the API key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Generation configuration settings
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the Generative Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    generation_config=generation_config
)

# Streamlit app
st.title("Museum Ticket Booking Chatbot")

st.write("""
Welcome to the Museum Ticket Booking Chatbot! This chatbot can assist you with booking tickets,
providing information about exhibits, and answering any questions you might have.
Let's get started by entering your request below.
""")

prompt = st.text_input("Ask me anything about the museum or book a ticket:", "I want to book a ticket for tomorrow.")
if st.button("Send"):
    try:
        chat_session = model.start_chat(
            history=[]
        )
        
        response = chat_session.send_message(prompt)
        
        st.subheader("Chatbot Response")
        st.write(response.text)
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.write("---")
st.write("This chatbot is powered by Google Generative AI and is here to make your museum visit easier and more enjoyable.")
