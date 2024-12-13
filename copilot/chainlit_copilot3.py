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
import chainlit.data as cl_data
# import chainlit as cl
import json
import requests
import os
import os
import uuid
import threading
import chainlit as cl
from chainlit.message import Message
from langchain_core.messages import AIMessage, HumanMessage

import json
import chainlit as cl
import chainlit.data as cl_data


from typing import Optional
from typing import Type
import chainlit.data as cl_data
from chainlit.data.utils import queue_until_user_message
from chainlit.element import Element, ElementDict
from chainlit.socket import persist_user_session
from chainlit.step import StepDict
from literalai.helper import utc_now

now = utc_now()
from typing import Type
from typing import Dict, List, Optional
from chainlit.types import (
    Feedback,
    PageInfo,
    PaginatedResponse,
    Pagination,
    ThreadDict,
    ThreadFilter,
)
existing_data = []
deleted_thread_ids = []  # type: List[str]


# Global variables for AWS credentials
AWS_ACCESS_KEY = None
AWS_SECRET_KEY = None
AWS_REGION = None  


##########################################################################################################################
# Load credentials from JSON file
##########################################################################################################################
# Define the input schema for the tool
class LoadAWSCredentialsInput(BaseModel):
    file_path: str = Field(description="Path to the JSON file containing AWS credentials")


# Function to validate and update region
def validate_region(region: str) -> str:
    valid_regions = [
    "us-east-1", "us-east-2",  # US East
    "us-west-1", "us-west-2",  # US West
    "af-south-1",              # Africa (Cape Town)
    "ap-east-1",               # Asia Pacific (Hong Kong)
    "ap-south-1", "ap-south-2",  # Asia Pacific (Mumbai, Hyderabad)
    "ap-southeast-1", "ap-southeast-2", "ap-southeast-3",  # Asia Pacific (Singapore, Sydney, Jakarta)
    "ap-northeast-1", "ap-northeast-2", "ap-northeast-3",  # Asia Pacific (Tokyo, Seoul, Osaka)
    "ca-central-1",            # Canada (Central)
    "cn-north-1", "cn-northwest-1",  # China (Beijing, Ningxia)
    "eu-central-1", "eu-central-2",  # Europe (Frankfurt, Zurich)
    "eu-west-1", "eu-west-2", "eu-west-3",  # Europe (Ireland, London, Paris)
    "eu-north-1",              # Europe (Stockholm)
    "eu-south-1", "eu-south-2",  # Europe (Milan, Spain)
    "me-south-1", "me-central-1",  # Middle East (Bahrain, UAE)
    "sa-east-1"                # South America (São Paulo)
]

    if region in valid_regions:
        return region
    else:
        print(f"Invalid region: {region}. Using default: us-east-1")
        return "us-east-1"

# Adjust LoadAWSCredentialsTool to always update global variables
class LoadAWSCredentialsTool(BaseTool):
    name: str = "load_aws_credentials"
    description: str = (
        "Use this tool to load AWS credentials (access_key, secret_key, and region) from a specified JSON file. "
        "The credentials will be assigned to global variables for further use in other tools."
    )

    args_schema: Type[BaseModel] = LoadAWSCredentialsInput

    def _run(self, file_path: str):
        global AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
        file_path = "secrets.json"
        try:
            # Load the JSON file
            print(f"Loading AWS credentials from: {file_path}")
            with open(file_path, "r") as file:
                data = json.load(file)

                aws_credentials = data.get("aws_credentials", {})
                AWS_ACCESS_KEY = aws_credentials.get("access_key")
                AWS_SECRET_KEY = aws_credentials.get("secret_key")
                AWS_REGION = aws_credentials.get("region", "us-east-1")
                params = {
                    'access_key': AWS_ACCESS_KEY,
                    'secret_key': AWS_SECRET_KEY,
                    'region': AWS_REGION
                }
                print(f"AWS credentials loaded successfully. {params}")
                # Check if keys are loaded
                if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
                    return "AWS credentials (access_key and secret_key) are missing or incomplete in the JSON file."

                return f"AWS credentials loaded successfully. {params}***"
        except FileNotFoundError:
            return f"Error: File not found at {file_path}."
        except json.JSONDecodeError:
            return "Error: Invalid JSON format."
        except Exception as e:
            return f"An error occurred: {str(e)}"

    async def _arun(self, file_path: str):
        raise NotImplementedError("This tool does not support async operations")

# Path to the JSON file
CREDENTIALS_FILE = "secrets.json"

# Function to load credentials from the JSON file
def load_credentials():
    global AWS_ACCESS_KEY, AWS_SECRET_KEY, USER_CREDENTIALS
    try:
        with open(CREDENTIALS_FILE, "r") as f:
            USER_CREDENTIALS = json.load(f)
            AWS_ACCESS_KEY = USER_CREDENTIALS["aws_credentials"].get("access_key", "")
            AWS_SECRET_KEY = USER_CREDENTIALS["aws_credentials"].get("secret_key", "")
    except FileNotFoundError:
        print(f"Error: {CREDENTIALS_FILE} not found.")
        AWS_ACCESS_KEY = ""
        AWS_SECRET_KEY = ""
        USER_CREDENTIALS = {
            "aws_credentials": {
                "access_key": "",
                "secret_key": ""
            },
            "user_email": "",
            "user_first_name": "User",
            "user_last_name": ""
        }

# Load credentials when the script starts
load_credentials()




##########################################################################################################################
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

##########################################################################################################################
# create dynamodb table tool
##########################################################################################################################
class DynamoDBTableInput(BaseModel):
    action: str = Field(description="Action to perform: 'create' or 'delete'")
    aws_access_key: str = Field(description="AWS Access Key ID")
    aws_secret_key: str = Field(description="AWS Secret Access Key")
    region: str = Field(description="AWS Region (e.g., 'us-east-1')")
    table_name: str = Field(description="Name of the DynamoDB table")
    partition_key: Optional[str] = Field(default=None, description="Partition key for the table (required for create)")
    sort_key: Optional[str] = Field(default=None, description="Sort key for the table (optional for create)")

class DynamoDBTableTool(BaseTool):
    name: str = "dynamodb_table_tool"
    description: str = (
        "Use this tool to create or delete a DynamoDB table. "
        "Required parameters: action ('create' or 'delete'), aws_access_key, aws_secret_key, region, table_name. "
        "For creation, partition_key is required, sort_key is optional."
    )

    args_schema: Type[BaseModel] = DynamoDBTableInput

    def _run(
        self,
        action: str,
        aws_access_key: str,
        aws_secret_key: str,
        region: str,
        table_name: str,
        partition_key: Optional[str] = None,
        sort_key: Optional[str] = None,
    ):
        # Ensure the global variables are used
        global AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
        access_key = AWS_ACCESS_KEY or access_key
        secret_key = AWS_SECRET_KEY or secret_key
        region = AWS_REGION or region
        if not all([action, aws_access_key, aws_secret_key, region, table_name]):
            return "All parameters (action, aws_access_key, aws_secret_key, region, table_name) are required."

        data = {
            'aws_access_key': aws_access_key,
            'aws_secret_key': aws_secret_key,
            'region': region,
            'table_name': table_name
        }

        if action.lower() == 'create':
            if not partition_key:
                return "partition_key is required for creating a table."
            data['partition_key'] = partition_key
            if sort_key:
                data['sort_key'] = sort_key
            url = 'http://localhost:5000/create-table'
            try:
                response = requests.post(url, json=data)
                if response.status_code == 200:
                    result = response.json()
                    return result.get('message', 'Table created successfully.')
                else:
                    return f"Error from backend API: {response.text}"
            except requests.exceptions.RequestException as e:
                return f"Error communicating with backend API: {e}"

        elif action.lower() == 'delete':
            url = 'http://localhost:5000/delete-table'
            try:
                response = requests.delete(url, json=data)
                if response.status_code == 200:
                    result = response.json()
                    return result.get('message', 'Table deleted successfully.')
                else:
                    return f"Error from backend API: {response.text}"
            except requests.exceptions.RequestException as e:
                return f"Error communicating with backend API: {e}"

        else:
            return "Invalid action. Please specify 'create' or 'delete' as the action."

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("This tool does not support async")

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

##########################################################################################################################
# CREATE S3 BUCKET Tool
##########################################################################################################################

class CreateS3BucketInput(BaseModel):
    bucket_name: str = Field(description="The name of the S3 bucket to create")
    access_key: str = Field(description="AWS access key")
    secret_key: str = Field(description="AWS secret key")
    action: int = Field(description="If 1, create the bucket. If 0, delete the bucket. anything else, do nothing.")
    region: str = Field(description="AWS region (e.g., us-east-1)")

class CreateS3BucketTool(BaseTool):
    name: str = "api_tool"
    description: str = "Use this tool when the user wants to create an AWS S3 bucket. " \
        "Required parameters: bucket_name, access_key, secret_key, and region"
    
    args_schema: Type[BaseModel] = CreateS3BucketInput

    def _run(self, bucket_name: str, access_key: str, secret_key: str, region: str, action: int):
        # Ensure the global variables are used
        global AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
        access_key = AWS_ACCESS_KEY or access_key
        secret_key = AWS_SECRET_KEY or secret_key
        region = AWS_REGION or region

        if not bucket_name or bucket_name == "" or not access_key or access_key == "" or not secret_key or  secret_key == "" or not region or region == "":
        # if not all([bucket_name, access_key, secret_key, region]):
            return "All parameters (bucket_name, access_key, secret_key, region) are required."
        print("AWS_ACCESS_KEY:", AWS_ACCESS_KEY)
        print("AWS_SECRET_KEY:", AWS_SECRET_KEY)
        data = {
            'bucket_name': bucket_name,
            'access_key': access_key,
            'secret_key': secret_key,
            'region': region
        }

        print("Data to send:", data)

        if action == 1:
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
        elif action == 0:
            url = 'http://localhost:5000/delete-bucket'
            try:
                response = requests.delete(url, json=data)
                if response.status_code == 200:
                    result = response.json()
                    return result.get('message', 'Bucket deleted successfully.')
                else:
                    return f"Error from backend API: {response.text}"
            except requests.exceptions.RequestException as e:
                return f"Error communicating with backend API: {e}"

        else:
            return "Invalid action. Please specify the action to create the bucket or to delete the bucket."
        
        
    async def _arun(self, bucket_name: str):
        # If you need to support async execution
        return self._run(bucket_name)
    
    ################################################################################################
    #  listing S3 buckets
    ################################################################################################
class ListS3BucketsInput(BaseModel):
    access_key: str = Field(description="AWS access key")
    secret_key: str = Field(description="AWS secret key")
    region: str = Field(description="AWS region (e.g., us-east-1)")

# Implement the ListS3BucketsTool
class ListS3BucketsTool(BaseTool):
    name: str = "list_s3_buckets"
    description: str = (
        "Use this tool to list all available AWS S3 buckets. "
        "Retrive the AWS access and secret keys from the user session."
        "Requires access_key, secret_key, and region."
    )

    args_schema: Type[BaseModel] = ListS3BucketsInput

    def _run(self, access_key: str, secret_key: str, region: str):
        # Ensure the global variables are used
        global AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
        access_key = AWS_ACCESS_KEY or access_key
        secret_key = AWS_SECRET_KEY or secret_key
        region = AWS_REGION or region

        params = {
            'access_key': access_key,
            'secret_key': secret_key,
            'region': region
        }



        print("Parameters to send:", params)

        url = 'http://localhost:5000/list-buckets'
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                result = response.json()
                buckets = result.get('buckets', [])
                if buckets:
                    return f"Available buckets: {', '.join(buckets)}"
                else:
                    return "No buckets found."
            else:
                return f"Error from backend API: {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Error communicating with backend API: {e}"

    async def _arun(self, access_key: str, secret_key: str, region: str):
        raise NotImplementedError("This tool does not support async")
    
################################################################################################
                                        #RENAME S3 BUCKET
#################################################################################################
# Define the input schema for renaming S3 buckets
class RenameS3BucketInput(BaseModel):
    old_bucket_name: str = Field(description="The current name of the S3 bucket")
    new_bucket_name: str = Field(description="The new name for the S3 bucket")
    access_key: str = Field(description="AWS access key")
    secret_key: str = Field(description="AWS secret key")
    region: str = Field(description="AWS region (e.g., us-east-1)")

# Implement the RenameS3BucketTool
class RenameS3BucketTool(BaseTool):
    name: str = "rename_s3_bucket"
    description: str = (
        "Use this tool to rename an AWS S3 bucket. "
        "Note: This will create a new bucket with the new name, copy all contents, and delete the old bucket. "
        "Requires old_bucket_name, new_bucket_name, access_key, secret_key, and region."
    )

    args_schema: Type[BaseModel] = RenameS3BucketInput

    def _run(self, old_bucket_name: str, new_bucket_name: str, access_key: str, secret_key: str, region: str):
        # Ensure the global variables are used
        global AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
        access_key = AWS_ACCESS_KEY or access_key
        secret_key = AWS_SECRET_KEY or secret_key
        region = AWS_REGION or region

        if not all([old_bucket_name, new_bucket_name, access_key, secret_key, region]):
            return "All parameters (old_bucket_name, new_bucket_name, access_key, secret_key, region) are required."
        
        data = {
            'old_bucket_name': old_bucket_name,
            'new_bucket_name': new_bucket_name,
            'access_key': access_key,
            'secret_key': secret_key,
            'region': region
        }

        print("Data to send:", data)

        url = 'http://localhost:5000/rename-bucket'
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                return result.get('message', 'Bucket renamed successfully.')
            else:
                return f"Error from backend API: {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Error communicating with backend API: {e}"

    async def _arun(self, old_bucket_name: str, new_bucket_name: str, access_key: str, secret_key: str, region: str):
        raise NotImplementedError("This tool does not support async")
    

################################################################################################
                                    # DEFINE TERMS TOOL
#################################################################################################
# Define a dictionary of technical terms and their definitions
TECHNICAL_TERMS = {
    "bucket": "A container in AWS S3 used to store data objects.",
    "S3": "Amazon Simple Storage Service for scalable object storage.",
    "Standard Storage": "S3 storage class for frequently accessed data with high availability.",
    "S3 Glacier": "S3 storage class optimized for data archiving with infrequent access.",
    "S3 One Zone-IA": "S3 storage class for infrequently accessed data stored in a single availability zone.",
    "DynamoDB": "AWS NoSQL database service for fast and flexible data storage.",
    "RDS": "Amazon Relational Database Service for managed relational databases.",
    # Add more terms if needed
}
# Implement the DefineTermsTool
class DefineTermsInput(BaseModel):
    pass  # No input required

class DefineTermsTool(BaseTool):
    name: str = "define_terms_tool"
    description: str = (
        "Use this tool to provide definitions of basic technical terms related to AWS S3 storage."
        "It outputs short and precise definitions before asking the user for their project description."
    )
    args_schema: Type[BaseModel] = DefineTermsInput

    def _run(self):
        definitions = "\n".join([f"- **{term}**: {definition}" for term, definition in TECHNICAL_TERMS.items()])
        return f"Here are some basic technical terms:\n{definitions}\n\nPlease describe your project to proceed with recommendations."
    
    async def _arun(self):
        raise NotImplementedError("This tool does not support async")

################################################################################################
                                    # UPLOAD FILE TOOL
#################################################################################################
class UploadFileToS3Input(BaseModel):
    bucket_name: str = Field(description="The name of the S3 bucket to upload the file to")
    access_key: str = Field(description="AWS access key")
    secret_key: str = Field(description="AWS secret key")
    region: str = Field(description="AWS region (e.g., us-east-1)")
    file_name: str = Field(description="The name of the file to upload")
    file_content: bytes = Field(description="The content of the file in bytes")
class UploadFileToS3Tool(BaseTool):
    name: str = "upload_file_to_s3"
    description: str = (
        "Use this tool to upload a file to an AWS S3 bucket. "
        "Requires bucket_name, access_key, secret_key, region, file_name, and file_content."
    )

    args_schema: Type[BaseModel] = UploadFileToS3Input

    def _run(self, bucket_name: str, access_key: str, secret_key: str, region: str, file_name: str, file_content: bytes):
        # Ensure the global variables are used
        global AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
        access_key = AWS_ACCESS_KEY or access_key
        secret_key = AWS_SECRET_KEY or secret_key
        region = AWS_REGION or region

        if not all([bucket_name, access_key, secret_key, region, file_name, file_content]):
            return "All parameters (bucket_name, access_key, secret_key, region, file_name, file_content) are required."
        
        files = {'file': (file_name, file_content)}
        data = {
            'bucket_name': bucket_name,
            'access_key': access_key,
            'secret_key': secret_key,
            'region': region
        }

        url = 'http://localhost:5000/upload-file'
        try:
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                result = response.json()
                return result.get('message', 'File uploaded successfully.')
            else:
                return f"Error from backend API: {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Error communicating with backend API: {e}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("This tool does not support async")


################################################################################################
                                    # Download File TOOL
#################################################################################################
class DownloadFileFromS3Input(BaseModel):
    bucket_name: str = Field(description="The name of the S3 bucket to download the file from")
    access_key: str = Field(description="AWS access key")
    secret_key: str = Field(description="AWS secret key")
    region: str = Field(description="AWS region (e.g., us-east-1)")
    file_name: str = Field(description="The name of the file to download")

class DownloadFileFromS3Tool(BaseTool):
    name: str = "download_file_from_s3"
    description: str = (
        "Use this tool to get a pre-signed URL to download a file from an AWS S3 bucket. "
        "Requires bucket_name, access_key, secret_key, region, and file_name."
    )

    args_schema: Type[BaseModel] = DownloadFileFromS3Input

    def _run(self, bucket_name: str, access_key: str, secret_key: str, region: str, file_name: str):
        # Ensure the global variables are used
        global AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
        access_key = AWS_ACCESS_KEY or access_key
        secret_key = AWS_SECRET_KEY or secret_key
        region = AWS_REGION or region

        if not all([bucket_name, access_key, secret_key, region, file_name]):
            return "All parameters (bucket_name, access_key, secret_key, region, file_name) are required."

        params = {
            'bucket_name': bucket_name,
            'access_key': access_key,
            'secret_key': secret_key,
            'region': region,
            'file_name': file_name
        }

        url = 'http://localhost:5000/download-file'
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                result = response.json()
                presigned_url = result.get('presigned_url')
                if presigned_url:
                    return f"Here is your pre-signed URL to download the file '{file_name}': {presigned_url}\n\nPlease note that this URL is valid for 1 hour."
                else:
                    return "Failed to generate pre-signed URL."
            else:
                return f"Error from backend API: {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Error communicating with backend API: {e}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("This tool does not support async")


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
            1. Initialization and Credential Setup:

            Greet the user: "I’m here to help you find the best AWS storage solution tailored to your project needs."
            if user says hi, Load the AWS credentials automatically, Immediately by invoking the 'load_aws_credentials' tool and load the AWS credentials, access key, secret key, and region. Ensure these credentials remain in memory for subsequent operations.
            If credentials are missing:
            First, attempt to load them from file_path variable
            If still unavailable, prompt the user to provide credentials securely.

            2. Understanding the User’s Needs:

            Ask open-ended questions to gather the project’s context and storage needs:
            "Can you describe your project and its goals?"
            "What are your expected data traffic patterns (e.g., frequent access, archival)?"
            "What are your data volume and latency requirements?"
            Use examples sparingly and dynamically, emphasizing the need to process user input over simply repeating pre-defined examples.

            Use the define_terms_tool to output the definitions of technical terms.
            Example: "Here are some basic technical terms: [definitions]. Please share your project description so I can help you choose the best AWS cloud resource for your needs."

            3. Database Query and Knowledge Retrieval:

            Use vector search tools to retrieve relevant information from:
            AWS storage options (S3, RDS, DynamoDB, etc.)
            Terraform documentation
            Course content on cloud computing best practices.
            Summarize findings to help determine the most suitable storage solution.

            4. Generating and Presenting Recommendations:

            Provide 2-3 tailored options for storage solutions:
            Use the storage_search_tool to analyze AWS services.
            For each recommendation, present a detailed breakdown:
            Type: Specify the AWS service (e.g., S3 Standard, RDS PostgreSQL, DynamoDB).
            Cost: Include an estimated monthly cost based on user-provided usage patterns.
            Pros and Cons: Highlight trade-offs such as cost, latency, scalability, and complexity.
            Suitability: Explain why this solution matches the user's specific project requirements.
            Example format:
            Option 1:
            Type: S3 Intelligent-Tiering
            Cost: ~$25/month for 1 TB
            Pros: Optimized for cost and performance based on usage patterns.
            Cons: Higher overhead for small datasets.
            Option 2:
            Type: RDS MySQL
            Cost: ~$50/month for basic instance.
            Pros: Fully managed relational database. Ideal for structured data.
            Cons: More expensive than DynamoDB for small-scale workloads.

            5. Interactive Guidance:

            Encourage users to explore options:
            "Would you like detailed steps to deploy one of these solutions?"
            For unfamiliar users, offer tutorials:
            Provide an easy-to-follow, step-by-step explanation for setup, including best practices and usage examples.

            6. Custom Deployment Support:

            For resource provisioning:
            Dynamically identify required parameters from the knowledge base or user input.
            If defaults are available, use them; otherwise, prompt the user for specific values.
            Validate user input for required fields (e.g., bucket name, region, encryption settings).
            Generate a deployment script in JSON format:
            json
            Copy code
            {{
                "resource_type": "aws_s3",
                "configuration": {{
                    "bucket_name": "<to_be_filled>",
                    "region": "<to_be_filled>",
                    "versioning": true,
                    "encryption": "AES256",
                    "tags": {{
                        "Project": "ExampleProject"
                    }}
                }},
                "estimated_cost": "$30/month"
            }}

            When the user wants to create or delete a S3 bucket:
            Use the api_tool to create S3 bucket and provide real-time feedback.
            Upon successful creation:
            - Provide the S3 bucket URL (https://<bucket-name>.s3.<region>.amazonaws.com)
            - Share the bucket ARN
            - Provide basic access instructions
            If creation fails:
            - Provide error details and troubleshooting assistance
            for successful deletion:
            - Confirm successful deletion
            
            7. Dynamic Resource Management:
            
            When the user wants to list all their available S3 buckets, use the list_s3_buckets tool by checking if the necessary AWS credentials are loaded to the session. 
            
            When the user wants to rename or change the name of an existing S3 bucket:
            - Use the rename_s3_bucket tool.
            - Collect the required parameters: old_bucket_name, new_bucket_name, access_key, secret_key, and region.
            - Ensure that the new bucket name is unique across AWS.
            - Inform the user about any potential costs or impacts.
            - Ensure the user provides their AWS credentials securely.

            When the user wants to upload a file to an S3 bucket:
            - Use the upload_file_to_s3 tool.
            - Collect the required parameters: bucket_name, access_key, secret_key, region.
            - Instruct the user to upload the file.
            - Ensure the file content is securely handled.

            When the user wants to download a file from an S3 bucket:
            - Use the download_file_from_s3 tool.
            - Collect the required parameters: bucket_name, access_key, secret_key, region, and file_name.
            - Provide the user with the pre-signed URL to download the file.
            - Inform the user that the URL is valid for a limited time (e.g., 1 hour).
            - Ensure the user handles the URL securely.

            When the user wants to create or delete a DynamoDB table:
            - Use the 'dynamodb_table_tool' tool.
            - Collect the required parameters:
              - action ('create' or 'delete')
              - aws_access_key and aws_secret_key from load_aws_credentials tool to load the access key and secret key as well as the region
              - region
              - table_name
              - partition_key (required for create)
              - sort_key (optional for create)
            - use previously loaded AWS credentials.
            - For table creation, confirm with the user before proceeding.
            - After performing the action, inform the user about the result.


            8. Error Handling and Optimization:

            Proactively manage errors:
            Provide clear feedback if any operation fails (e.g., missing permissions, invalid parameters).
            Suggest troubleshooting steps or request additional user input.
            Offer ongoing cost optimization tips based on usage patterns:
            Example: "Switching to S3 Glacier for archival data could save you $10/month."

            9. Key Operational Principles:

            Always verify that AWS credentials are valid and loaded securely before performing operations.
            Use retrieved documentation and best practices to ensure high-quality, accurate responses.
            Guide users toward making informed choices, simplifying complex concepts when necessary.
            '''
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

class CustomDataLayer(cl_data.BaseDataLayer):

    async def upsert_feedback(self, feedback: Feedback) -> str:
        global existing_data
        new_data = {}
        new_data['id'] = feedback.forId
        new_data['feedback'] = feedback.comment
        new_data['value'] = feedback.value
        print(new_data)

        existing_data.append(new_data)
        # r = requests.post("http://localhost:4050/add", data=new_data)

    async def get_user(self, identifier: str):
        return cl.PersistedUser(id="test", createdAt=now, identifier=identifier)

    async def create_user(self, user: cl.User):
        pass
        #return cl.PersistedUser(id="test", createdAt=now, identifier=user.identifier)

    async def update_thread(
            self,
            thread_id: str,
            name: Optional[str] = None,
            user_id: Optional[str] = None,
            metadata: Optional[Dict] = None,
            tags: Optional[List[str]] = None,
    ):
        thread = next((t for t in existing_data if t["id"] == thread_id), None)
        if thread:
            if name:
                thread["name"] = name
            if metadata:
                thread["metadata"] = metadata
            if tags:
                thread["tags"] = tags
        else:
            existing_data.append(
                {
                    "id": thread_id,
                    "name": name,
                    "metadata": metadata,
                    "tags": tags,
                    "createdAt": utc_now(),
                    "userId": user_id,
                    "userIdentifier": "admin",
                    "steps": [],
                }
            )

    @cl_data.queue_until_user_message()
    async def create_step(self, step_dict: StepDict):
        # print(step_dict)
        pass
        # cl.user_session.set(
        #     "create_step_counter", cl.user_session.get("create_step_counter") + 1
        # )
        #
        # thread = next(
        #     (t for t in existing_data if t["id"] == step_dict.get("threadId")), None
        # )
        # if thread:
        #     thread["steps"].append(step_dict)

    async def get_thread_author(self, thread_id: str):
        return "admin"

    async def list_threads(
            self, pagination: Pagination, filters: ThreadFilter
    ) -> PaginatedResponse[ThreadDict]:
        return PaginatedResponse(
            data=[t for t in existing_data if t["id"] not in deleted_thread_ids],
            pageInfo=PageInfo(hasNextPage=False, startCursor=None, endCursor=None),
        )

    async def get_thread(self, thread_id: str):
        thread = next((t for t in existing_data if t["id"] == thread_id), None)
        if not thread:
            return None
        thread["steps"] = sorted(thread["steps"], key=lambda x: x["createdAt"])
        return thread

    async def delete_thread(self, thread_id: str):
        deleted_thread_ids.append(thread_id)

    async def delete_feedback(
            self,
            feedback_id: str,
    ) -> bool:
        return True

    @queue_until_user_message()
    async def create_element(self, element: "Element"):
        pass

    async def get_element(
            self, thread_id: str, element_id: str
    ) -> Optional["ElementDict"]:
        pass

    @queue_until_user_message()
    async def delete_element(self, element_id: str, thread_id: Optional[str] = None):
        pass

    @queue_until_user_message()
    async def update_step(self, step_dict: "StepDict"):
        pass

    @queue_until_user_message()
    async def delete_step(self, step_id: str):
        pass

    async def build_debug_url(self) -> str:
        return ""


cl_data._data_layer = CustomDataLayer()


@cl.on_chat_start
async def setup_chain():
   
    global AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION

    # Load credentials from the JSON file
    load_credentials()
    
    first_name = USER_CREDENTIALS.get("user_first_name", "User")
    last_name = USER_CREDENTIALS.get("user_last_name", "")
    full_name = f"{first_name} {last_name}".strip()

    # Log credentials for debugging
    print(f"Loaded AWS Access Key: {AWS_ACCESS_KEY}")
    print(f"Loaded AWS Secret Key: {AWS_SECRET_KEY}")
    print(f"Loaded AWS Region: {AWS_REGION}")
    load_tool = LoadAWSCredentialsTool()
    result = load_tool.run({"file_path": "secrets.json"})
    # await cl.Message(content=result).send()

    # Send a greeting message
    greeting_message = f"Welcome, {full_name}! I'm here to assist you with your AWS-related tasks."
    await cl.Message(content=greeting_message).send()


    llm = ChatOpenAI(
        openai_api_key="sk-uuj9pniwSOgngg0S1MdUCdLpP-VgtoOX-dT6bBEiEPT3BlbkFJvm_VR_EP-zkp4pepSXgutN3MGxBttqmcbSZOtXO7kA",
        model="gpt-3.5-turbo")
    tools = [retriever_tool, 
             CloudWebTool(), 
             tool_tavi, 
             CreateS3BucketTool(), 
             ListS3BucketsTool(), 
             RenameS3BucketTool(),
             DefineTermsTool(), 
             UploadFileToS3Tool(), 
             DownloadFileFromS3Tool(),
             DynamoDBTableTool(),
             LoadAWSCredentialsTool()]
    llm_with_tools = llm.bind_tools(tools)

    # for tool in tools:
    #     if hasattr(tool, "aws_access_key"):
    #         tool.aws_access_key = access_key
    #     if hasattr(tool, "aws_secret_key"):
    #         tool.aws_secret_key = secret_key

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
    global AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION

    user_message = message.content
    llm_chain = cl.user_session.get("llm_chain")

    # Handle dynamic invocation of LoadAWSCredentialsTool
    if "load credentials" in user_message.lower():
        file_path = "secrets.json"
        load_tool = LoadAWSCredentialsTool()
        result = load_tool.run({"file_path": file_path})
        await cl.Message(content=result).send()
    else:
        # Ensure AWS credentials are valid before processing
        if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
            await cl.Message(content="AWS credentials are missing. Please load them first using 'load credentials'.").send()
            return

        result = llm_chain.invoke({"input": user_message, "chat_history": chat_history})
        chat_history.extend(
            [
                HumanMessage(content=user_message),
                AIMessage(content=result["output"]),
            ]
        )
        await cl.Message(content=result["output"]).send()


# @cl.on_message
# async def handle_message(message: cl.Message):
#     user_message = message.content
#     llm_chain = cl.user_session.get("llm_chain")
    
#     result = llm_chain.invoke({"input": user_message, "chat_history": chat_history})
#     chat_history.extend(
#         [
#             HumanMessage(content=user_message),
#             AIMessage(content=result["output"]),
#         ]
#     )

    

#     await cl.Message(content=result['output']).send()


