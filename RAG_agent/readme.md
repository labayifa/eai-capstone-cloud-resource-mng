# AWS S3 RAG Agent

This project implements a RAG (Retrieval-Augmented Generation) Agent that helps users find detailed information about AWS S3. The agent is designed to be interacted with through a Streamlit UI.

## Setup Instructions

Before running the application, you need to set up the necessary environment variables.

### Environment Variables

1. Create a `.env` file in the current directory of this project.
2. Add the following variables to the `.env` file, replacing `your_token_here` with your actual keys:

```plaintext
GITHUB_ACCESS_TOKEN=your_github_token_here
OPENAI_API_KEY_Ell=your_openai_key_here
TAVILY_API_KEY=your_tavily_key_here
LANGCHAIN_API_KEY=your_langchain_key_here
```

Make sure the `GITHUB_ACCESS_TOKEN` is set with the token that has access to the repository containing the AWS S3 pricing information by putting the aws_S3_pricing.txt file inside your repo.

## Installation

This project requires Python 3.6 or higher. To install Streamlit, run the following command:

```
pip install streamlit
```

## Running the Application

After setting up the environment variables and installing Streamlit, you can run the RAG Agent with the following command:

```
streamlit run streamlit_ui.py
```

The Streamlit UI will open in your web browser, where you can interact with the AWS S3 Deployment Assistant.

# Deployment Example

![AWS S3 Deployment Assistant
AI Chatbot in Work](images/Screenshot 2024-10-21 213837.png)