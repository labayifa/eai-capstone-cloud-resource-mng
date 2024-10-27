import streamlit as st

# Set page config at the very beginning
st.set_page_config(page_title="AWS S3 Deployment Assistant", layout="wide")

from rag_agent import initialize_agent, handle_chat
import traceback

# Initialize the agent
@st.cache_resource
def get_agent():
    return initialize_agent()

agent_executor = get_agent()

# Custom CSS for a cleaner look
st.markdown("""
<style>
.stTextInput > div > div > input {
    background-color: #f0f2f6;
}
.stButton > button {
    width: 100%;
}
.chat-message {
    padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;
}
.chat-message.user {
    background-color: #2b313e;
    color: #ffffff;
}
.chat-message.bot {
    background-color: #475063;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# Main content
st.title("AWS S3 Deployment Assistant")

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar for conversation management
with st.sidebar:
    st.subheader("Conversation Management")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.experimental_rerun()
    
    st.subheader("Need inspiration?")
    st.markdown("Try asking about:")
    suggestions = [
        "Storage classes in AWS S3",
        "Data transfer pricing in S3",
        "S3 Intelligent-Tiering",
        "S3 Standard vs S3 Glacier",
        "Regional pricing differences in S3"
    ]
    for suggestion in suggestions:
        if st.button(suggestion):
            st.session_state.messages.append({"role": "user", "content": suggestion})
            st.experimental_rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about AWS S3 pricing"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            with st.spinner("Thinking..."):
                response = handle_chat(prompt, [m["content"] for m in st.session_state.messages], agent_executor)
                full_response = response.get("output", "I'm sorry, but I couldn't generate a response. Please try again.")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error(f"Traceback: {traceback.format_exc()}")
            full_response = "I'm sorry, but I encountered an error while processing your request. Please try again or rephrase your question."
            message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Add a download button for chat history
if st.session_state.messages:
    chat_history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
    st.download_button(
        label="Download Chat History",
        data=chat_history,
        file_name="chat_history.txt",
        mime="text/plain"
    )