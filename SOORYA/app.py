import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import re  # Import regex for basic NLP

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

# Initialize session state for tracking conversation
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "booking_details" not in st.session_state:
    st.session_state.booking_details = {}

# Streamlit app
st.set_page_config(
    page_title="Museum Ticket Booking Chatbot",
    page_icon="🖼️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("🎟️ Museum Ticket Booking Chatbot")

st.markdown("""
<style>
.chat-box {
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.user-message {
    background-color: #DCF8C6;
    color: #000;
    text-align: left;
}
.bot-message {
    background-color: #F1F0F0;
    color: #000;
    text-align: left;
}
.paypal_button {
    background-color: #0070ba;
    color: white;
    padding: 10px 20px;
    font-size: 16px;
    border-radius: 5px;
    border: none;
    cursor: pointer;
}
.paypal_button:hover {
    background-color: #005a99;
}
</style>
""", unsafe_allow_html=True)

st.write("""
Welcome to the Museum Ticket Booking Chatbot! This chatbot can assist you with booking tickets,
providing information about exhibits, and answering any questions you might have.
Let's get started by entering your request below.
""")

# Prompt user for input
prompt = st.text_input("Ask me anything about the museum or book a ticket:", "")

if st.button("Send"):
    try:
        # Start chat session if this is the first step
        if st.session_state.current_step == 0:
            chat_session = model.start_chat(history=[])
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.session_state.chat_session = chat_session
        else:
            chat_session = st.session_state.chat_session
        
        # Handle different steps of the booking process
        if st.session_state.current_step == 0:
            st.session_state.chat_history.append({"role": "assistant", "content": "Welcome! To start the booking process, could you please tell me your full name?"})
            st.session_state.current_step += 1

        elif st.session_state.current_step == 1:
            # Extract the name, removing any common phrases like "I am"
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

            # Display PayPal payment button
            st.markdown(f"""
                <form action="https://www.sandbox.paypal.com/cgi-bin/webscr" method="post" target="_top">
                    <input type="hidden" name="cmd" value="_xclick">
                    <input type="hidden" name="business" value="YOUR_PAYPAL_BUSINESS_EMAIL">
                    <input type="hidden" name="item_name" value="Museum Ticket">
                    <input type="hidden" name="amount" value="10.00">
                    <input type="hidden" name="currency_code" value="USD">
                    <input type="hidden" name="quantity" value="{st.session_state.booking_details['num_tickets']}">
                    <input type="hidden" name="return" value="http://localhost:8501/thank_you">
                    <input type="hidden" name="cancel_return" value="http://localhost:8501/cancel">
                    <input type="submit" value="Pay Now" class="paypal_button">
                </form>
            """, unsafe_allow_html=True)

        elif st.session_state.current_step == 6:
            # Final step: Summarize user details
            st.session_state.chat_history.append({"role": "assistant", "content": f"Here are the details you've provided:\n\n**Name**: {st.session_state.booking_details['name']}\n**Gender**: {st.session_state.booking_details['gender']}\n**Number of Tickets**: {st.session_state.booking_details['num_tickets']}\n**Date of Visit**: {st.session_state.booking_details['date_of_visit']}\n**Email**: {st.session_state.booking_details['email']}\n\nPlease review the details and proceed with payment."})
            st.session_state.current_step += 1

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Display chat history
for entry in st.session_state.chat_history:
    if entry["role"] == "user":
        st.markdown(f"<div class='chat-box user-message'><strong>You:</strong> {entry['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-box bot-message'><strong>Bot:</strong> {entry['content']}</div>", unsafe_allow_html=True)

st.write("---")
st.write("This chatbot is powered by Google Generative AI and is here to make your museum visit easier and more enjoyable.")
