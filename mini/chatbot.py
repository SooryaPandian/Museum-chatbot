import re
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from payment import display_payment_button


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

def initialize_session():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0
    if "booking_details" not in st.session_state:
        st.session_state.booking_details = {}

def handle_chat_step(prompt):
    try:
        chat_session = st.session_state.get("chat_session", None)
        if st.session_state.current_step == 0:
            chat_session = model.start_chat(history=[])
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.session_state.chat_session = chat_session
            st.session_state.chat_history.append({"role": "assistant", "content": "Welcome! To start the booking process, could you please tell me your full name?"})
            st.session_state.current_step += 1
        elif st.session_state.current_step == 1:
            name = re.sub(r"^(i am|my name is|it's|this is|I am) ", "", prompt, flags=re.I).strip()
            st.session_state.booking_details['name'] = name
            st.session_state.chat_history.append({"role": "assistant", "content": f"Thank you, {name}! What is your gender?"})
            st.session_state.current_step += 1
        elif st.session_state.current_step == 2:
            st.session_state.booking_details['gender'] = prompt
            st.session_state.chat_history.append({"role": "assistant", "content": "How many tickets would you like to book?"})
            st.session_state.current_step += 1
        elif st.session_state.current_step == 3:
            st.session_state.booking_details['num_tickets'] = prompt
            st.session_state.chat_history.append({"role": "assistant", "content": "When would you like to visit the museum? Please enter the date in YYYY-MM-DD format."})
            st.session_state.current_step += 1
        elif st.session_state.current_step == 4:
            st.session_state.booking_details['date_of_visit'] = prompt
            st.session_state.chat_history.append({"role": "assistant", "content": "Could you please provide your email address for the booking confirmation?"})
            st.session_state.current_step += 1
        elif st.session_state.current_step == 5:
            st.session_state.booking_details['email'] = prompt
            st.session_state.chat_history.append({"role": "assistant", "content": "Thank you! Please click the button below to proceed with the payment."})
            st.session_state.current_step += 1
            display_payment_button()
        elif st.session_state.current_step == 6:
            st.session_state.chat_history.append({"role": "assistant", "content": f"Here are the details you've provided:\n\n**Name**: {st.session_state.booking_details['name']}\n**Gender**: {st.session_state.booking_details['gender']}\n**Number of Tickets**: {st.session_state.booking_details['num_tickets']}\n**Date of Visit**: {st.session_state.booking_details['date_of_visit']}\n**Email**: {st.session_state.booking_details['email']}\n\nPlease review the details and proceed with payment."})
            st.session_state.current_step += 1
    except Exception as e:
        st.error(f"An error occurred: {e}")
