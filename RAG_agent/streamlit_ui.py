# streamlit_ui.py  
  
import streamlit as st  
from rag_agent import initialize_agent, handle_chat
  
# Initialize the agent  
agent_executor = initialize_agent()  
  
# Streamlit app  
st.title("AWS S3 Pricing RAG Agent")  
  
# Creating a session state for chat_history if it doesn't exist  
if 'chat_history' not in st.session_state:  
    st.session_state['chat_history'] = []  
  
# Text area for user input  
user_input = st.text_area("Ask a question about AWS S3 Pricing:", height=150)  
  
# Button to submit the question  
submit_button = st.button("Submit")  
  
# Handling the chat interaction  
if submit_button and user_input:  
    with st.spinner("AI is at work..."):  
        # Call the handle_chat function and update the session state  
        response = handle_chat(user_input, st.session_state['chat_history'], agent_executor)  
          
        # Update the session state chat history  
        st.session_state['chat_history'].append(user_input)  
        st.session_state['chat_history'].append(response["output"])  
          
        # Display the AI's response  
        st.text_area("Response from the RAG Agent:", response["output"], height=150)  
