import streamlit as st

def load_styles():
    st.markdown("""
    <style>
    body {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        margin: 0;
        padding: 0;
    }

    .main {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
    }

    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding-bottom: 20px;
    }

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

    .input-container {
        position: sticky;
        bottom: 0;
        background-color: white;
        padding-top: 10px;
        padding-bottom: 20px;
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
