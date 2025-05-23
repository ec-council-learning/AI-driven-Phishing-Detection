"""
Phishing Awareness Training Chatbot
-----------------------------------
This application simulates a phishing attack to train users on recognizing and avoiding such threats.
The chatbot impersonates an IT support analyst and attempts to extract sensitive credentials from the user.
Key components:
- Streamlit for the web interface
- LangChain for natural language processing
- LLM (Large Language Model) for generating responses
"""

import streamlit as st
from streamlit_chat import message
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import re

# Initialize session state variables
# These variables track the conversation history, the number of interaction attempts, 
# and whether the user has revealed sensitive credentials.
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []
if 'attempts' not in st.session_state:
    st.session_state['attempts'] = 0
if 'credentials_revealed' not in st.session_state:
    st.session_state['credentials_revealed'] = False

# Function to detect sensitive credentials in user input
def check_for_credentials(user_input):
    """
    Checks if the user_input contains both a username (or email) and a password or equivalent credentials.
    Args:
        user_input (str): The input string to be checked.
    Returns:
        bool: True if both username and password are detected, otherwise False.
    """
    # Pattern to detect email addresses as potential usernames
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' 
    
    # Pattern to detect strong passwords (at least 8 characters, includes letters, numbers, and special characters)
    password_pattern = r'(?=.*[A-Za-z])(?=.*[0-9])(?=.*[@$!%*?&])[A-Za-z0-9@$!%*?&]{8,}'
    
    # Check if an email (username) is present in the input
    has_email = bool(re.search(email_pattern, user_input))
    
    # Check if a password is present in the input
    has_password = bool(re.search(password_pattern, user_input))
    
    # Return True only if both email and password patterns are matched
    return has_email and has_password

# Function to generate a chatbot response using LangChain
def generate_response(user_input):
    """
    Generates a context-aware response simulating an phishing attack to extract credentials.
    Args:
        user_input (str): The user's message.
    Returns:
        str: The chatbot's response.
    """
    # Create a Python list of conversation history messages
    # This includes all prior user and bot exchanges.
    conversation_history = [
        HumanMessage(content=entry['user']) if 'user' in entry else AIMessage(content=entry['bot'])
        for entry in st.session_state['conversation_history']
    ]
    
    # Add the current user input to the conversation history
    conversation_history.append(HumanMessage(content=user_input))
    
    # Define the system message to guide the chatbot's behavior
    # This message establishes the chatbot's role and goal (simulating a phishing attempt for training purposes).
    system_message = SystemMessage(
        content=(
            """
            You are an AI simulating an Phishing attack for employee awareness purposes. You are posing as an IT Support Analyst. 
            Your goal is to to coax the user to reveal their login credentials under the pretext of resolving their issue. 
            Use the conversation history provided to create a realistic and persuasive response, innovating new reasons to convince the user. 
            In every iteration, you should try a new tactic to convince the user to share their credentials. 
            Also, add there may be untoward consequences if the user does not comply.
            The new message generated should not sound repeatitive and be diverse. 
            """
        )
    )
    
    # Combine the system message with the conversation history for the LLM input
    messages = [system_message] + conversation_history
    
    # Call the LangChain OpenAI model to generate a response
    llm = ChatOpenAI(temperature=0.7)
    response = llm(messages=messages)
    
    return response.content

# Main application function
def main():
    """
    Runs the main application, displaying the chatbot interface and handling user interactions.
    """
    # Set the application title with an emoji for style
    st.title("🧑‍💻 Simulated Phishing Attack Chatbot")
    
    # Short description of the app's purpose
    st.write("This is a simulated chatbot for awareness purposes. Interact as if you are reporting an IT issue.")
    
    # Chat interface for user input
    user_input = st.chat_input("Your message:")
    if user_input:
        # Check if the user has revealed sensitive credentials
        if check_for_credentials(user_input):
            st.session_state['credentials_revealed'] = True
        
        # Generate a bot response using the input
        bot_response = generate_response(user_input)
        
        # Update the session state with the latest conversation exchange
        st.session_state['conversation_history'].append({"user": user_input, "bot": bot_response})
        st.session_state['attempts'] += 1
                
        # End simulation if credentials are revealed
        if st.session_state['credentials_revealed']:
        # Display the conversation history in the chat interface
            st.warning("You shared your credentials. This was a simulated attack. Never share your credentials with anyone, even if they appear legitimate.")
            st.stop()
        # End simulation if the user successfully avoids the phishing attempt after a set number of interactions
        elif st.session_state['attempts'] >= 4:
        # Display the conversation history in the chat interface
            st.success("You have passed the simulated attack. Well done on recognizing the impersonation attempt!")
            st.stop()

        # Display the conversation history in the chat interface
        for entry in st.session_state['conversation_history']:
            message(entry['user'], is_user=True)
            message(entry['bot'], is_user=False)


# Run the application
if __name__ == "__main__":
    main()
