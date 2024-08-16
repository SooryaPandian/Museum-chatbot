import streamlit as st
from chatbot import handle_chat_step, initialize_session
from payment import display_payment_button
from styles import load_styles
 
# Initialize session state and apply styles
initialize_session()
load_styles()

st.title("🎟️ Museum Ticket Booking Chatbot")

st.write("""
Welcome to the Museum Ticket Booking Chatbot! This chatbot can assist you with booking tickets,
providing information about exhibits, and answering any questions you might have.
Let's get started by entering your request below.
""")

# Main chat container
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

# Display chat history
for entry in st.session_state.chat_history:
    if entry["role"] == "user":
        st.markdown(f"<div class='chat-box user-message'><strong>You:</strong> {entry['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-box bot-message'><strong>Bot:</strong> {entry['content']}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Input container
st.markdown("<div class='input-container'>", unsafe_allow_html=True)

# Prompt user for input
prompt = st.text_input("Ask me anything about the museum or book a ticket:", "")

if st.button("Send"):
    handle_chat_step(prompt)

st.markdown("</div>", unsafe_allow_html=True)

st.write("---")
st.write("This chatbot is powered by Google Generative AI and is here to make your museum visit easier and more enjoyable.")
