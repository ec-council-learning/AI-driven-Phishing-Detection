"""
Phishing Message Detector: This Streamlit app uses OpenAI's GPT-4 model via LangChain 
to analyze messages and identify potential phishing attempts. Users can input a message, 
and the app provides a detailed analysis, conclusion, and recommendations based on 
common phishing characteristics. Secure API key handling is implemented for user safety.
"""
import streamlit as st
from langchain.chat_models import ChatOpenAI  
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("API key not found. Please set it in the .env file.")

# Set page configuration
st.set_page_config(
    page_title="Phishing Message Detector",
    page_icon="🔍",
    layout="centered"
)

# App title and description
st.title("📧 Phishing Message Detector")
st.markdown("""
This application analyzes text to determine if it's a potential phishing message.
Enter your API key and the message you want to analyze below.
""")

# Create a sidebar for API key input
with st.sidebar:
    
    # Information about the app
    st.markdown("### About")
    st.markdown("""
    This app uses OpenAI's GPT model through LangChain to analyze messages 
    and identify potential phishing attempts based on common characteristics.
    """)
    
    # Add some example phishing messages that users can try
    st.markdown("### Example Messages to Try")
    examples = [
        '''Subject: URGENT: Unusual Activity Detected on Your Account
        Dear Valued Customer,
        We have detected suspicious login attempts on your online banking account from an unrecognized device in Kyiv, Ukraine at 3:47 AM today. Your account has been temporarily restricted for security purposes.
        To verify your identity and restore full access to your account, please click the link below within 24 hours to confirm your personal information:
        http://secure-bankingverify.com/account-verify
        Failure to verify your account will result in permanent suspension of your online banking services. For your protection, please do not share this email with anyone.
        If you believe you received this message in error, contact our fraud department immediately at +1-888-555-0123.
        Regards,
        Security Department
        National Banking Services''',
        '''Subject: [IMPORTANT] Your Package Delivery Status Update Required
        Hello Customer,
        We've attempted to deliver your package (Tracking #: PKG78941235) to your address twice without success. Unfortunately, we cannot complete the delivery due to incomplete delivery information.
        Your package will be returned to the sender within 48 hours unless you update your delivery preferences. To receive your package, please complete the delivery verification process:

        Click here: http://tracking-delivery-update.net/verify?id=7812
        Confirm your delivery address and contact details
        Pay the re-delivery fee of $2.99 using your preferred payment method

        This is your final notification. If you have questions about your delivery, contact our customer service department.
        Delivery Management Team
        Global Shipping Services''',
        '''Subject: Upcoming Mandatory Security Training Session
        Dear Team Members,
        As part of our ongoing commitment to data security and privacy, our IT department has scheduled the quarterly security awareness training for all employees. This 45-minute session will cover recent security threats, password management best practices, and how to identify potential phishing attempts.
        Session Details:

        Date: Thursday, April 3, 2025
        Time: 10:00 AM - 10:45 AM (your local time)
        Location: Virtual - Microsoft Teams meeting
        Presenter: Sarah Chen, Chief Information Security Officer

        This training is mandatory for all employees. If you're unable to attend the live session, a recording will be available on the company intranet for one week following the presentation.
        Please add this to your calendar, and feel free to prepare any security-related questions you'd like addressed during the Q&A portion.
        Best regards,
        Michael Rodriguez
        HR Director'''
    ]
    
    for i, example in enumerate(examples):
        if st.button(f"Example {i+1}", key=f"example_{i}"):
            st.session_state.message_input = example

# Initialize session state for the message input
if 'message_input' not in st.session_state:
    st.session_state.message_input = ""

# Text area for user input
message = st.text_area(
    "Enter the message to analyze:",
    value=st.session_state.message_input,
    height=150
)

# Function to analyze the message
def analyze_phishing_message(message, api_key):
    # Set the OpenAI API key
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Create a prompt template
    template = """
    You are a cybersecurity expert specializing in identifying phishing attempts.
    
    Analyze the following message and determine if it's likely a phishing attempt.
    Consider these characteristics of phishing messages:
    
    1. Creates a sense of urgency or fear
    2. Contains suspicious links or attachments
    3. Requests personal information, credentials, or financial details
    4. Has spelling or grammatical err–ors
    5. Uses an unusual sender address
    6. Contains threats or extreme consequences
    7. Offers deals that are too good to be true
    8. Lacks specific personalization
    
    Message to analyze:
    {message}
    
    First, provide a detailed analysis of the message based on the characteristics above.
    Then, provide your conclusion with a confidence level (High, Medium, Low) on whether this is a phishing attempt or legitimate message.
    
    Your response should be in this format:
    
    Analysis:
    [Your detailed analysis here]
    
    Conclusion:
    [Your conclusion with confidence level]
    
    Recommendation:
    [What the user should do with this message]
    """
    
    # Create the prompt
    prompt = PromptTemplate(
        input_variables=["message"],
        template=template,
    )
    
    # Initialize the LLM using ChatOpenAI
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Create and run the chain
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(message)
    
    return response

# Analyze button
if st.button("Analyze Message"):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    elif not message:
        st.error("Please enter a message to analyze.")
    else:
        with st.spinner("Analyzing message..."):
            try:
                # Call the analysis function
                result = analyze_phishing_message(message, api_key)
                
                # Display the result
                st.markdown("## Analysis Result")
                
                # Split the result into sections
                sections = result.split("\n\n")
                
                # Display each section with appropriate formatting
                for section in sections:
                    if section.startswith("Analysis:"):
                        st.subheader("Analysis")
                        st.write(section[9:].strip())
                    elif section.startswith("Conclusion:"):
                        st.subheader("Conclusion")
                        conclusion_text = section[11:].strip()
                        
                        # Highlight the conclusion based on whether it's likely phishing
                        if "phishing" in conclusion_text.lower() and not "not a phishing" in conclusion_text.lower():
                            st.error(conclusion_text)
                        else:
                            st.success(conclusion_text)
                    elif section.startswith("Recommendation:"):
                        st.subheader("Recommendation")
                        st.info(section[14:].strip())
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if "API key" in str(e).lower():
                    st.error("There might be an issue with your API key. Please check if it's valid.")
                else:
                    st.error("Please make sure you have the required packages installed and try again.")

# Add CSS for better styling
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextArea>div>div>textarea {
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)
