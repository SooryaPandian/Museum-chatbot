import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit.components.v1 as components
from fpdf import FPDF
import random
import string
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pymongo import MongoClient
from bson.objectid import ObjectId

load_dotenv()
# MongoDB setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client["museum_db"]
users_collection = db["users"]

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
if "history" not in st.session_state:
    st.session_state.history = [
        {
            "role": "user",
            "parts": ["hi"],
        },
        {
            "role": "model",
            "parts": [
                "Hello! 👋  Welcome to the National Museum Delhi ticketing service. I'm here to help you book your tickets.  \n\nWhat can I help you with today? Are you interested in learning more about the museum, checking ticket prices, or booking your visit? 😊 \n",
            ],
        },
    ]

if "messages" not in st.session_state:
    st.session_state.messages = []

def send_feedback(feedback: str) -> str:
    if "user" not in st.session_state:
        st.error("Please log in to continue.")
        return "Please login to continue"
    else:
        """Send feedback or reports to a specified email address."""
        sender_email = "heistchief@gmail.com"
        receiver_email = "heistchief@gmail.com"
        subject = "Feedback from User"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        password = "zyzd qjlb riuu iodi"

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(feedback, "plain"))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Feedback sent successfully.")
        except Exception as e:
            print(f"Failed to send feedback. Error: {e}")
        finally:
            server.quit()

        return "Thank you for your feedback."

# Function to sign up a new user
def signup_user(name: str, email: str, password: str, mobile: str) -> None:
    if users_collection.find_one({"email": email}):
        st.error("Email already exists. Please use a different email.")
    else:
        user_id = users_collection.insert_one({"name": name, "email": email, "password": password, "mobile": mobile}).inserted_id
        st.session_state.user = {"_id": str(user_id), "name": name, "email": email}
        st.session_state.history.append({
            "role": "user",
            "parts": ["The user hase been logged in sucessfully"+str({"_id": str(user["_id"]), "name": user["name"], "email": user["email"]})],
        })
        st.success("Account created successfully!")

# Function to log in a user
def login_user(email: str, password: str) -> dict:
    print(email,password)
    user = users_collection.find_one({"email": email, "password": password})
    if user:
        st.session_state.user = {"_id": str(user["_id"]), "name": user["name"], "email": user["email"]}
        st.session_state.history.append({
            "role": "user",
            "parts": ["The user has been logged in sucessfully"+str({"_id": str(user["_id"]), "name": user["name"], "email": user["email"]})],
        })
        return st.session_state.user
    else:
        st.error("Invalid credentials!")
        return {}
def logout_user():
    # Add logic to log out the user
    if 'user' in st.session_state:
        del st.session_state['user']

def book_ticket(adult: int, child: int, guide: bool, visit_date: str, visit_time: str) -> str:
    """Books a ticket, handles payment, and generates a PDF receipt."""
    if "user" not in st.session_state:
        st.error("Please log in to continue.")
        return "Please login to continue"
    else:
        ticket_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        total_amount = (adult * 50) + (child * 20)
        if guide:
            total_amount += 200

        payment_status = "success"
        payment_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if payment_status == "success":
            st.success("Payment Successful!")
            pdf = generate_ticket_pdf(ticket_id, adult, child, guide, total_amount, visit_date, visit_time, payment_time)
            st.download_button(label="Download Receipt", data=pdf, file_name=f"ticket_{ticket_id}.pdf", mime="application/pdf")
            return f"Ticket ID: {ticket_id}, Payment Status: {payment_status}"
        else:
            st.error("Payment Failed! Please try again.")
            return f"Ticket ID: {ticket_id}, Payment Status: {payment_status}"

def generate_ticket_pdf(ticket_id: str, adult: int, child: int, guide: bool, total_amount: int, visit_date: str, visit_time: str, payment_time: str) -> bytes:
    """Generates a PDF ticket with the provided details."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Ticket Receipt", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Ticket ID: {ticket_id}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Number of Adults: {adult}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Number of Children: {child}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Guide Included: {'Yes' if guide else 'No'}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Total Amount: Rs. {total_amount}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Visit Date: {visit_date}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Visit Time: {visit_time}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Payment Time: {payment_time}", ln=True, align='L')
    return pdf.output(dest='S').encode('latin1')

def initiate_paypal(amount: float) -> str:
    """Embeds the PayPal payment button into the Streamlit app and handles the payment process."""
    payment_status = "failure"
    paypal_html = f"""
    <script src="https://www.paypal.com/sdk/js?client-id=AX0Wku0FLQHVVQKt5fvu4XpmraCQKgxKrYa99L4k-EcxANNwO5YDeYfyzBV4BypFj0uY4kng_pd1Qrlp&currency=USD&enable-funding=card"></script>
    <div id="paypal-button-container"></div>
    <script>
        paypal.Buttons({{
            style: {{
                layout: 'horizontal'
            }},
            createOrder: function(data, actions) {{
                return actions.order.create({{
                    purchase_units: [{{
                        amount: {{
                            value: '{amount:.2f}'
                        }}
                    }}]
                }});
            }},
            onApprove: function(data, actions) {{
                return actions.order.capture().then(function(details) {{
                    alert('Transaction completed by ' + details.payer.name.given_name);
                    document.getElementById('payment-status').value = 'success';
                }});
            }},
            onError: function(err) {{
                alert('Transaction failed');
                document.getElementById('payment-status').value = 'failure';
            }}
        }}).render('#paypal-button-container');
    </script>
    <input type="hidden" id="payment-status" value="failure">
    """
    components.html(paypal_html, height=500)
    payment_status = st.session_state.get("payment_status", "failure")
    return payment_status

function_mapping = {
    "book_ticket": book_ticket,
    "send_feedback": send_feedback,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "Your name is Museum Ai. When the user says hi, greet them and ask if they need any help."
        "If the user says any feedback or report that should be sent to send_feedback function."
        "You're a chatbot that assists people in booking tickets to national museum delhi."
        "The museum will open from 9:00 am to 12:00 pm and from 1:00 pm to 7:00 pm."
        "The ticket fee is Rs 20 for children and Rs 50 for adults."
        "If the user mentions the number of people (adults and children), ticket option, visit date, and time, "
        "you should call the function with them as arguments."
        "If the user enters all the details and wants to book a ticket, the `book_ticket` function should be called with the required parameters."
        "(if the user says to send feedback or report, or gives feed backs or reportm call the `send_feedback` function)All the messages like reports, feedbacks should be sent to `send_feedback` function."
        "By default user is not logged in"
    ),
    tools=[book_ticket, send_feedback]
)

# Initialize session state for history and messages


# Initialize session state for user and page
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'  # Default to login page

# Navigation between pages
def navigate_to(page):
    st.session_state.page = page

# Sidebar Navigation
st.sidebar.title("Museum Ticket Booking")

# if st.session_state.user:
#     st.sidebar.write(f"Logged in as {st.session_state.user}")
#     if st.sidebar.button("Logout"):
#         logout_user()
#         st.sidebar.success("Logged out successfully!")
#         navigate_to('login')
# else:
if st.sidebar.button("Login"):
        navigate_to('login')
if st.sidebar.button("Sign Up"):
        navigate_to('signup')

# Page rendering within the sidebar
if st.session_state.page == 'signup' and not st.session_state.user:
    st.sidebar.subheader("Sign Up")
    name = st.sidebar.text_input("Name")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    mobile = st.sidebar.text_input("Mobile Number")
    
    if st.sidebar.button("Create Account"):
        signup_user(name, email, password, mobile)
        st.sidebar.success("Account created successfully! Please log in.")
        navigate_to('logout')

elif st.session_state.page == 'login' and not st.session_state.user:
    st.sidebar.subheader("Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Log In"):
        user = login_user(email, password)
        if user:
            st.session_state.user = email
            st.sidebar.success("Logged in successfully!")
            navigate_to('logout')
        else:
            st.sidebar.error("Invalid credentials!")

elif st.session_state.page == 'logout' and st.session_state.user:
    st.sidebar.subheader("Logout")
    st.sidebar.write(f"Logged in as {st.session_state.user}")
    
    if st.sidebar.button("Logout"):
        logout_user()
        st.sidebar.success("Logged out successfully!")
        navigate_to('login')
        
# Display chat messages from the session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input for user's message
prompt = st.chat_input("Type your message...")

if prompt:
    chat_session = model.start_chat(history=st.session_state.history)
    # Add user's message to chat
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Update history with the user's input
    st.session_state.history.append({
        "role": "user",
        "parts": [prompt],
    })

    # Display a loading spinner while waiting for the bot's response
    with st.spinner("Waiting for response..."):
        response = chat_session.send_message(prompt)
        
        for part in response.parts:
            if fn := part.function_call:
                # args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
                
                res=function_mapping[fn.name](**fn.args)
                print(fn.name)
                response = chat_session.send_message("Generate response for the user for the result by the sytem:"+res)
        
        # Update history with the model's response
        st.session_state.history.append({
            "role": "model",
            "parts": [response.text],
        })
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
