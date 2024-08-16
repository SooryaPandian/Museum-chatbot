import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit.components.v1 as components
from fpdf import FPDF
import random
import string
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

def book_ticket(adult: int, child: int, guide: bool) -> str:
    """Books a ticket, calculates the total cost, handles payment, and generates a PDF receipt.

    This function generates a ticket ID, calculates the total amount based on the number
    of adults, children, and whether a guide is needed. It then calls the `initiate_paypal`
    function to handle payment and, upon successful payment, generates a PDF ticket for download.

    Args:
        adult (int): The number of adults.
        child (int): The number of children.
        guide (bool): Whether a guide is needed.

    Returns:
        str: A string indicating the ticket ID and whether the payment was successful.
    """
    # Generate a random ticket ID
    
    ticket_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    # ticket_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    # Calculate the total amount
    total_amount = (adult * 50) + (child * 20)
    if guide:
        total_amount += 200
    
    # Print ticket details to the terminal
    print(f"Ticket ID: {ticket_id}")
    print(f"Adults: {adult}, Children: {child}, Guide: {'Yes' if guide else 'No'}")
    print(f"Total Amount: Rs. {total_amount}")
    
    # Initiate PayPal payment
    # payment_status = initiate_paypal(total_amount)
    payment_status ="success"
    
    # Check payment status and generate a PDF receipt
    if payment_status == "success":
        st.success("Payment Successful!")
        
        # Generate the PDF ticket
        pdf = generate_ticket_pdf(ticket_id, adult, child, guide, total_amount)
        
        # Display the download button for the PDF
        st.download_button(label="Download Receipt", data=pdf, file_name=f"ticket_{ticket_id}.pdf", mime="application/pdf")
        
        return f"Ticket ID: {ticket_id}, Payment Status: {payment_status}"
    else:
        st.error("Payment Failed! Please try again.")
        return f"Ticket ID: {ticket_id}, Payment Status: {payment_status}"

def generate_ticket_pdf(ticket_id: str, adult: int, child: int, guide: bool, total_amount: int) -> bytes:
    """Generates a PDF ticket with the provided details.

    Args:
        ticket_id (str): The unique ID for the ticket.
        adult (int): The number of adults.
        child (int): The number of children.
        guide (bool): Whether a guide is included.
        total_amount (int): The total amount for the ticket.

    Returns:
        bytes: The PDF file as a byte stream.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add the ticket details to the PDF
    pdf.cell(200, 10, txt="Ticket Receipt", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Ticket ID: {ticket_id}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Number of Adults: {adult}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Number of Children: {child}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Guide Included: {'Yes' if guide else 'No'}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Total Amount: Rs. {total_amount}", ln=True, align='L')
    
    # Output the PDF as a byte stream
    return pdf.output(dest='S').encode('latin1')
def initiate_paypal(amount: float) -> str:
    """Embeds the PayPal payment button into the Streamlit app and handles the payment process.

    This function integrates the PayPal Smart Payment Buttons into the Streamlit app.
    It allows users to make payments by clicking the PayPal button and returns the
    status of the payment (success or failure).

    Args:
        amount (float): The amount to be charged through PayPal.

    Returns:
        str: A string indicating whether the payment was 'success' or 'failure'.
    """
    payment_status = "failure"

    # HTML and JavaScript to embed PayPal buttons
    paypal_html = f"""
    <!-- PayPal Button Integration -->
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
                            value: '{amount:.2f}' // Amount to be charged
                        }}
                    }}]
                }});
            }},
            onApprove: function(data, actions) {{
                return actions.order.capture().then(function(details) {{
                    // Payment was successful
                    alert('Transaction completed by ' + details.payer.name.given_name);
                    document.getElementById('payment-status').value = 'success';
                }});
            }},
            onError: function(err) {{
                // Payment failed
                alert('Transaction failed');
                document.getElementById('payment-status').value = 'failure';
            }}
        }}).render('#paypal-button-container');
    </script>
    <input type="hidden" id="payment-status" value="failure">
    """

    # Render the HTML and JavaScript for PayPal button
    components.html(paypal_html, height=500)

    # Check the payment status
    payment_status = st.session_state.get("payment_status", "failure")

    return payment_status
function_mapping = {
    "book_ticket": book_ticket,
    
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "Your name is Museum Ai.when user said hi greet them nd also ask do they need any help"
        "You're a chatbot that assists people to book tickets in a museum. "
        "you should support multiple languages(default language is english)"
        "whatever language the user input you shoud not change the language of the functions called(only english),you can response to a user in appropiate language"
        "You have to answer the user's doubts about the museum and available ticket options. "
        "If the user mentions the number of people (adults and children) and the ticket option, "
        "you have to call the function with them as arguments."
        "Strictly you should not response any other things like formula for area other than museum "
        "The museum will open from 9:00 am to 12:00pm and from 1:00 pm to 7:00pm"
        "There are two option to book ticket just book the museum ticket or ticket along with guide(Rs 200 for guide)."
        "The ticket fee is 20 for children and 50 for adults"
        "while confirming also show the amount to be paid"
        "If the user enter all the details and want to book ticket, book_ticket function should be called with required parameters"
    ),
    tools=[book_ticket]
)

# Initialize session state for history and messages if not already done
if "history" not in st.session_state:
    st.session_state.history = [
        {
            "role": "user",
            "parts": ["hi"],
        },
        {
            "role": "model",
            "parts": [
                "Hello! 👋  Welcome to the [Museum Name] ticketing service. I'm here to help you book your tickets.  \n\nWhat can I help you with today? Are you interested in learning more about the museum, checking ticket prices, or booking your visit? 😊 \n",
            ],
        },
    ]

if "messages" not in st.session_state:
    st.session_state.messages = []

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
                response = chat_session.send_message("Generate response for the user for the result by the sytem:"+res)
        
        # Update history with the model's response
        st.session_state.history.append({
            "role": "model",
            "parts": [response.text],
        })
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
