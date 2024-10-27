# rag_agent.py  
  
# Import necessary libraries  
import os  
from dotenv import load_dotenv  
from langchain_community.document_loaders import GithubFileLoader  
from langchain_openai import ChatOpenAI, OpenAIEmbeddings  
from langchain_community.vectorstores import FAISS  
from langchain_text_splitters import RecursiveCharacterTextSplitter  
from langchain.tools.retriever import create_retriever_tool  
from langchain.agents import Tool, AgentExecutor  
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser  
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages  
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  
from langchain_core.messages import AIMessage, HumanMessage  
from langchain_community.document_loaders import TextLoader  
# Load environment variables  
load_dotenv()  
  
github_access_token = os.getenv('GITHUB_ACCESS_TOKEN')  
openai_api_key = os.getenv('OPENAI_API_KEY_Ell')  
tavily_api_key = os.getenv('TAVILY_API_KEY')  
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')  
  
# Function to initialize and return the agent executor  
def initialize_agent():  
    # Load documents from GitHub securely  
    try:  
        # loader = GithubFileLoader(  
        #     # specify your git handle and repo name
        #     repo="ellonsolomon/S3_RAG_LMM",  
        #     access_token=github_access_token,  
        #     github_api_url="https://api.github.com",  
        #     file_filter=lambda file_path: file_path.endswith("txt"),  
        txt_file_path = '/home/br/Downloads/Fall_2024/Capstone/eai-capstone-cloud-resource-mng-rag_agent/RAG_agent/aws_S3_pricing.txt'
        loader = TextLoader(file_path=txt_file_path, encoding="utf-8")
        # )  
        documents = loader.load()  
    except Exception as e:  
        print(f"Error loading documents from GitHub: {e}")  
        documents = []  
  
    # Split documents into manageable chunks  
    text_splitter = RecursiveCharacterTextSplitter()  
    try:  
        documents = text_splitter.split_documents(documents)  
    except Exception as e:  
        print(f"Error splitting documents: {e}")  
  
    # Initialize FAISS vector store  
    try:  
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)  
        vector = FAISS.from_documents(documents, embeddings)  
    except Exception as e:  
        print(f"Error initializing FAISS vector store: {e}")  
  
    # Create retriever tool  
    retriever = vector.as_retriever()  
    retriever_tool = create_retriever_tool(  
        retriever,  
        "AWS_S3_Pricing_Information",  
        "Search for information about AWS S3 Pricing in detail. For data transfer and storage pricing options, use this tool!",  
    )  
  
    # Bind tools to the LLM  
    llm = ChatOpenAI(openai_api_key=openai_api_key)  
    tools = [retriever_tool]  
    try:  
        llm_with_tools = llm.bind_tools(tools)  
    except Exception as e:  
        print(f"Error binding tools to LLM: {e}")  
  
    # Refine prompt template for better interaction  
    prompt = ChatPromptTemplate.from_messages(  
        [  
            (  
                "system",  
                '''You are an AI assistant that provides detailed AWS S3 Pricing information to users. For inquiries about data transfer and storage pricing options, utilize the AWS_S3_Pricing_Information tool to deliver precise and updated pricing details.'''  
            ),  
            MessagesPlaceholder(variable_name="chat_history"),  
            ("user", "{input}"),  
            MessagesPlaceholder(variable_name="agent_scratchpad"),  
        ]  
    )  
  
    # Initialize agent with custom output parser if needed  
    agent = (  
        {  
            "input": lambda x: x["input"],  
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),  
            "chat_history": lambda x: x["chat_history"]  
        }  
        | prompt  
        | llm_with_tools  
        | OpenAIToolsAgentOutputParser()  
    )  
  
    # Return the agent executor  
    return AgentExecutor(agent=agent, tools=tools, verbose=False)  
  
# Function to handle the chat interaction  
def handle_chat(input_message, chat_history, agent_executor):  
    try:  
        result = agent_executor.invoke({"input": input_message, "chat_history": chat_history})  
        chat_history.extend([  
            HumanMessage(content=input_message),  
            AIMessage(content=result["output"]),  
        ])  
        return result  
    except Exception as e:  
        print(f"Error during chat interaction: {e}")  
        return None  