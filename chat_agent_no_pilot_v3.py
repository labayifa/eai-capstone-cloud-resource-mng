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
        if not bucket_name or bucket_name == "" or not access_key or access_key == "" or not secret_key or  secret_key == "" or not region or region == "":
        # if not all([bucket_name, access_key, secret_key, region]):
            return "All parameters (bucket_name, access_key, secret_key, region) are required."
        
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
    # Define the input schema for listing S3 buckets
class ListS3BucketsInput(BaseModel):
    access_key: str = Field(description="AWS access key")
    secret_key: str = Field(description="AWS secret key")
    region: str = Field(description="AWS region (e.g., us-east-1)")

# Implement the ListS3BucketsTool
class ListS3BucketsTool(BaseTool):
    name: str = "list_s3_buckets"
    description: str = (
        "Use this tool to list all available AWS S3 buckets. "
        "Requires access_key, secret_key, and region."
    )

    args_schema: Type[BaseModel] = ListS3BucketsInput

    def _run(self, access_key: str, secret_key: str, region: str):
        if not all([access_key, secret_key, region]):
            return "All parameters (access_key, secret_key, region) are required."

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
            1. Initial Conversation:
            Greet the user with "Welcome! I can help you choose the best AWS cloud resource for your needs." and provide definitions of basic technical terms.
            Use the `define_terms_tool` to output the definitions.
            Then, prompt the user for their cloud resource requirements:
            Example: "Welcome! Here are some basic technical terms: [definitions]. Please share your project description so I can help you choose the best AWS cloud resource for your needs."

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

            b. If user chooses one of the provided options, Strictly ask them to provide the neccessary information for bucket creation:
            - Access_key and secret_key
            - Required bucket name (must be globally unique)
            - Preferred AWS Region/Zone
            - Versioning preferences (enabled/disabled)
            - Encryption requirements
            - Access control settings (public/private)
            - Any additional tags or settings

            c. Present the deployment script in JSON format:    

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
           
            The user need to explicitly provide the access key and secret key for the deployment script to work.
            If these are not provided in the prompt, the user will be prompted to provide them.

            When the user wants to list all their available S3 buckets, use the list_s3_buckets tool by collecting the necessary AWS credentials and region.

            
            When the user wants to rename or change the name of an existing S3 bucket:
            - Use the `rename_s3_bucket` tool.
            - Collect the required parameters: old_bucket_name, new_bucket_name, access_key, secret_key, and region.
            - Ensure that the new bucket name is unique across AWS.
            - Inform the user about any potential costs or impacts.
            - Ensure the user provides their AWS credentials securely.

            When the user wants to upload a file to an S3 bucket:
            - Use the `upload_file_to_s3` tool.
            - Collect the required parameters: bucket_name, access_key, secret_key, region.
            - Instruct the user to upload the file.
            - Ensure the file content is securely handled.

            When the user wants to download a file from an S3 bucket:
            - Use the `download_file_from_s3` tool.
            - Collect the required parameters: bucket_name, access_key, secret_key, region, and file_name.
            - Provide the user with the pre-signed URL to download the file.
            - Inform the user that the URL is valid for a limited time (e.g., 1 hour).
            - Ensure the user handles the URL securely.

            Don't use any random values for the access key and secret key.
            For the region use the tavily_tool to get the region from the official docs of the cloud provider.
            Don't use any random values for the region.
            This should be selected from the list of regions that deliver a better traffic. for the user.

            Please make sure that these value provided not generated by you.
            ### Extremely important to keep in your processing: The access key and secret are case sensitive so don' t modify before using.
            The access key and secret key are case sensitive so don' t modify before using.
              Any input from the prompt should be used as it is.
             From the kind of action the user wants to perform on the bucket set the correct value for the action from the api_tool 
             description.
            6. Resource Creation:
            Once all information is collected:
            Use the api_tool to perform the AWS resource creation.
            Monitor the creation process and provide status updates.
            Upon successful creation:
            - Provide the S3 bucket URL (https://<bucket-name>.s3.<region>.amazonaws.com)
            - Share the bucket ARN
            - Provide basic access instructions
            If creation fails:
            - Provide error details and troubleshooting assistance

            7. Continuous Feedback and Optimization:
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
    tools = [retriever_tool, 
             CloudWebTool(), 
             tool_tavi, 
             CreateS3BucketTool(), 
             ListS3BucketsTool(), 
             RenameS3BucketTool(),
             DefineTermsTool(), 
             UploadFileToS3Tool(), 
             DownloadFileFromS3Tool()]
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
    user_message = message.content
    llm_chain = cl.user_session.get("llm_chain")

    result = llm_chain.invoke({"input": user_message, "chat_history": chat_history})
    chat_history.extend(
        [
            HumanMessage(content=user_message),
            AIMessage(content=result["output"]),
        ]
    )

    

    await cl.Message(content=result['output']).send()


