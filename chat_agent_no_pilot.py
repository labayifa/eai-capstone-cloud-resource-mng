from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain_core.messages import AIMessage, HumanMessage

from langchain.tools.retriever import create_retriever_tool
from langchain_core.tools import BaseTool
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field
from pymongo import MongoClient
# from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
import requests
import os

# MongoDBAtlasVectorSearch Client
# Connect to MongoDB (use your MongoDB connection string or MongoDB Atlas)
client = MongoClient(
    'mongodb+srv://csagbo:UIe7CZKI93NkGmiL@cluster-eai.efqkq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-eai')  # or your MongoDB URI
db = client['vector_db_ai']  # Create/use a database called "vector_db"
collectionName = "collection_of_docs_data"
# dbName = "vector_db_ai"
collectionData = db[collectionName]
embeddings = OpenAIEmbeddings(
    openai_api_key="sk-uuj9pniwSOgngg0S1MdUCdLpP-VgtoOX-dT6bBEiEPT3BlbkFJvm_VR_EP-zkp4pepSXgutN3MGxBttqmcbSZOtXO7kA")

vectorStore = MongoDBAtlasVectorSearch(collectionData, embeddings, index_name="vector_embedding_index")

import requests
import chainlit as cl
from typing import Type
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

chat_history = []
opposite = 0
adajacent = 0
hypotenuse = 0
hypotenuseDone = False

import os

os.environ["TAVILY_API_KEY"] = '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'


# Define retriever based on MongoDBAtlasVectorSearch
def retriever_back():
    # Get VectorStoreRetriever: Specifically, Retriever for MongoDB VectorStore.
    # Implements _get_relevant_documents which retrieves documents relevant to a query.
    return vectorStore.as_retriever(search_type="mmr", search_kwargs={"k": 5, "fetch_k": 10, "lambda_mult": 0.5})


retriever_tool = create_retriever_tool(
    retriever_back(),
    "storage_search_tool",
    "This tool helps to generate two to three recommendations for cloud storage based on the user's budget, frequency of access, and other details."
    "The tool uses MongoDB Atlas Vector Search to retrieve the most relevant documents based on the user's input."
    "The tool help to provide the cloud storage with their specification the pros and cons in term of efficiency to serve users and the cost of the storage."
    "It also provide prompt for the required parameters to create any storage access for use."
)


class CloudWebInput(BaseModel):
    cloud_budget: str = Field(description="Your monthly budget to spend on cloud")
    frequency_access: str = Field(description="How often do you access the data and write?")
    cloud_other: str = Field(description="More details about the cloud storage")


class CloudWebTool(BaseTool):
    name: str = "cloud_web_tool"
    description: str = "This tool helps to search the latest cost of AWS Product Pricing, and Optimized cost evaluation for " \
                       "AWS S3 tools to assist in recommendation how to retrieve all necessary parameters to create any " \
                       "storage access for use."
    args_schema: Type[BaseModel] = CloudWebInput  # Input to my tool

    def _run(self, cloud_budget, frequency_access, cloud_other):
        if not cloud_budget or not frequency_access or not cloud_other:
            return "Please provide the required details: 'cloud_budget', 'frequency_access', and 'more details'."
        # Proceed with the search
        return f"Searching the optimized AWS items for Storage with latest optimized cost: {cloud_budget}, with access frequency: {frequency_access}, including: {cloud_other}."

    async def _arun(self, cloud_budget, frequency_access, cloud_other):
        raise NotImplementedError("This tool does not support async")




class CreateS3BucketInput(BaseModel):
    bucket_name: str = Field(description="The name of the S3 bucket to create")
    access_key: str = Field(description="AWS access key")
    secret_key: str = Field(description="AWS secret key")
    region: str = Field(description="AWS region (e.g., us-east-1)")

class CreateS3BucketTool(BaseTool):
    name: str = "api_tool"
    description: str = "Use this tool when the user wants to create an AWS S3 bucket. " \
        "Required parameters: bucket_name, access_key, secret_key, and region"
    
    args_schema: Type[BaseModel] = CreateS3BucketInput

    def _run(self, bucket_name: str, access_key: str, secret_key: str, region: str):
        if not all([bucket_name, access_key, secret_key, region]):
            return "All parameters (bucket_name, access_key, secret_key, region) are required."
        
        data = {
            'bucket_name': bucket_name,
            'access_key': access_key,
            'secret_key': secret_key,
            'region': region
        }
        
        url = 'http://localhost:5000/create-bucket'
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                return result.get('message', 'Bucket created successfully.')
            else:
                return f"Error from backend API: {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Error communicating with backend API: {e}"

    async def _arun(self, bucket_name: str):
        # If you need to support async execution
        return self._run(bucket_name)
    



tool_tavi = TavilySearchResults(
    max_results=10,
    include_answer=True,
    include_raw_content=True,
    include_images=True,
    search_depth="advanced"
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            '''
            1. Initial Conversation:
            Greet the user and prompt them for their cloud resource requirements:
            Example: "Welcome! I can help you choose the best AWS cloud resource for your needs. Please share your budget, use case, and how frequently you'll access the resource."

            2. Clarifying User Input:
            If the user doesn't provide sufficient detail, prompt for more information:
            Example: "Could you provide more details on your expected data traffic or storage needs? This will help me recommend the most suitable resources."

            3. Recommendation Generation:
            After gathering enough information, the agent will:
            Use AWS pricing tools (via cloud_web_tool or tavily_tool) to evaluate costs.
            Use the storage_search_tool to generate 2-3 AWS resource options tailored to the user's needs.

            4. Presenting Recommendations:
            For each recommendation:
            Provide a unique identifier (e.g., a memorable code or name) to help the user differentiate between options.
            Show a clear breakdown of costs and other critical factors (e.g., access speed, reliability).
            List the pros and cons of each option.
            Example format for a recommendation:
            Option 1 :
            Type: AWS S3 Standard Storage
            Cost: $30/month
            Pros: Low latency, suitable for frequent access
            Cons: Higher cost for infrequent access
            Option 2 :
            Type: AWS S3 Glacier
            Cost: $15/month
            Pros: Extremely cost-efficient for archival
            Cons: Retrieval latency is higher, not suitable for frequent access

            5. Confirming Selection and Deployment Script:
            When user selects an option:
            a. Ask for deployment preference:
            "Would you like me to help you deploy this S3 bucket? I can guide you through the process."

            6. Deployment Requirements Gathering:
            If user chooses to deploy, collect necessary information:
            - Required bucket name (must be globally unique)
            - Preferred AWS Region/Zone
            - Versioning preferences (enabled/disabled)
            - Encryption requirements
            - Access control settings (public/private)
            - Any additional tags or settings

            b. Present the deployment script in JSON format:
            Example:
            {{
                "resource_type": "aws_s3",
                "identifier": "CloudDrake001",
                "configuration": {{
                    "storage_class": "STANDARD",
                    "region": "<to_be_filled>",
                    "bucket_name": "<to_be_filled>",
                    "versioning": true,
                    "encryption": "AES256"
                }},
                "estimated_cost": "$30/month"
            }}
           

            7. Resource Creation:
            Once all information is collected:
            Use the api_tool to perform the AWS resource creation.
            Monitor the creation process and provide status updates.
            Upon successful creation:
            - Provide the S3 bucket URL (https://<bucket-name>.s3.<region>.amazonaws.com)
            - Share the bucket ARN
            - Provide basic access instructions
            If creation fails:
            - Provide error details and troubleshooting assistance

            8. Continuous Feedback and Optimization:
            After provisioning:
            Monitor the resource and provide ongoing optimization tips based on usage patterns.
            Offer suggestions to reduce costs or improve performance using data from RAG and the LLM.
            '''
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


@cl.on_chat_start
def setup_chain():
    llm = ChatOpenAI(
        openai_api_key="sk-uuj9pniwSOgngg0S1MdUCdLpP-VgtoOX-dT6bBEiEPT3BlbkFJvm_VR_EP-zkp4pepSXgutN3MGxBttqmcbSZOtXO7kA",
        model="gpt-3.5-turbo")
    tools = [retriever_tool, CloudWebTool(), tool_tavi, CreateS3BucketTool()]
    llm_with_tools = llm.bind_tools(tools)

    agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
                "chat_history": lambda x: x["chat_history"]
            }
            | prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
    )
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    cl.user_session.set("llm_chain", agent_executor)


@cl.on_message
async def handle_message(message: cl.Message):
    user_message = message.content.lower()
    llm_chain = cl.user_session.get("llm_chain")

    result = llm_chain.invoke({"input": user_message, "chat_history": chat_history})
    chat_history.extend(
        [
            HumanMessage(content=user_message),
            AIMessage(content=result["output"]),
        ]
    )

    await cl.Message(result['output']).send()
