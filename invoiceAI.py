from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
import streamlit as st
import os
from streamlit_lottie import st_lottie
import requests
from PIL import Image
import google.generativeai as genai


os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content([input, image[0], prompt])
        return response.text
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type, 
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# New function to load Lottie animation
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Set page config
st.set_page_config(page_title="InVoiceAI", layout="wide")

# Custom CSS
st.markdown("""
<style>
.big-font {
    font-size:50px !important;
    font-weight: bold;
    color: #1E90FF;
}
.stButton>button {
    background-color: #4CAF50;
    color: white;
    font-size: 20px;
    padding: 15px 32px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="big-font">Invoice Info Extractor</p>', unsafe_allow_html=True)

# Load Lottie animation
lottie_url = "https://assets9.lottiefiles.com/packages/lf20_qmfs6c3i.json"
lottie_json = load_lottieurl(lottie_url)

# Two-column layout
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader("Choose an invoice image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Invoice", use_column_width=True)

    input = st.text_input("What would you like to know about this invoice?", key="input")
    submit = st.button("Ask InvoiceAI")

with col2:
    st_lottie(lottie_json, height=300, key="lottie")

input_prompt = """
               You are an expert in understanding invoices.
               You will receive input images as invoices &
               you will have to answer questions based on the input image
               """

if submit:
    if uploaded_file is None:
        st.error("Please upload an invoice image before asking a question.")
    else:
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt, image_data, input)
        if response:
            st.success("The InvoiceAI says:")
            st.write(response)
            
            # Check if the response indicates the question is out of scope
            if "I'm sorry, but I can't answer that question based on the invoice" in response or "The information you're asking for is not typically found on an invoice" in response:
                st.warning("It seems your question might be beyond the scope of the invoice. Please try asking about information typically found on invoices, such as dates, amounts, item descriptions, or vendor details.")
        else:
            st.error("Failed to get a response. Please try again with a different question or check your internet connection.")
