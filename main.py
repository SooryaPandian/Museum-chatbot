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
    generation_config=generation_config
)

# Streamlit app
st.title("Magic Backpack Story Generator")

prompt = st.text_input("Enter a prompt:", "Write a story about a magic backpack.")

if st.button("Generate Story"):
    try:
        chat_session = model.start_chat(
            history=[]
        )
        
        response = chat_session.send_message(prompt)
        
        st.subheader("Generated Story")
        st.write(response.text) 
    except Exception as e:
        st.error(f"An error occurred: {e}")
