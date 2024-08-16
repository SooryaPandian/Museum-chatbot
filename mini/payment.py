import streamlit as st

def display_payment_button():
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
