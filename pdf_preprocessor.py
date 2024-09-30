import os
import boto3
from urllib.parse import urlparse
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from nltk.tokenize import sent_tokenize


# ##############################################################################
# # Make sure to install the required packages before running the code:
# # setup the OpenAI API key in your environment variables
# # export OPENAI_API_KEY="your-openai-api-key"    #for linux systems
# # $env:OPENAI_API_KEY="your-openai-api-key"    #for windows (powerShel) systems

# Ensure AWS Credentials Are Set (run the following in your terminal)
# export AWS_ACCESS_KEY_ID="your-access-key-id"
# export AWS_SECRET_ACCESS_KEY="your-secret-access-key"

################################################################################
def download_pdf_from_s3(s3_url, local_path):
    """Download a PDF from an S3 bucket."""
    # Parse the S3 URL
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.netloc
    s3_key = parsed_url.path.lstrip('/')
    
    # Initialize S3 client
    s3 = boto3.client('s3')
    
    # Download the PDF from S3
    s3.download_file(bucket_name, s3_key, local_path)
    print(f"Downloaded {s3_url} to {local_path}")

def load_pdf_with_langchain(pdf_path):
    """Load and parse the PDF using LangChain's PDF loader."""
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return documents

def split_text_by_sentences(documents, max_chunk_size=1000, chunk_overlap=100):
    """Split the document text into chunks based on basic punctuation."""
    text = " ".join([doc.page_content for doc in documents]) 
    sentences = text.split('. ')  # Simple split by periods followed by a space

    chunks = []
    current_chunk = []

    current_length = 0
    for sentence in sentences:
        sentence_length = len(sentence)

        # If adding this sentence exceeds the chunk size, finalize this chunk and start a new one
        if current_length + sentence_length > max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = current_chunk[-chunk_overlap:]  
            current_length = sum(len(sent) for sent in current_chunk) 

        # Add the sentence to the current chunk
        current_chunk.append(sentence)
        current_length += sentence_length

    # Add the last chunk if there's leftover content
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def create_vector_store(chunks):
    """Use OpenAI embeddings to create a vector store using LangChain."""
    # Ensure the API key is set in environment variables
    api_key = os.getenv("OPENAI_API_KEY")  
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store

def save_text_chunks_to_txt(chunks, output_txt_path):
    """Save the preprocessed chunks into a text file."""
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(chunk + "\n---\n")
    print(f"Processed text written to {output_txt_path}.")

def process_pdf(pdf_path, output_txt_path, is_s3=False):
    """Main function to process PDF from local file or S3."""
    # If it's an S3 file, download it first
    if is_s3:
        local_pdf_path = 'downloaded_s3_file.pdf'
        download_pdf_from_s3(pdf_path, local_pdf_path)
    else:
        local_pdf_path = pdf_path

    # Load and extract text from PDF using LangChain
    print(f"Loading and extracting text from {local_pdf_path}...")
    documents = load_pdf_with_langchain(local_pdf_path)
    
    # Split the text by sentences, ensuring no sentences are cut off
    print("Splitting text into chunks based on sentences...")
    chunks = split_text_by_sentences(documents, max_chunk_size=1000, chunk_overlap=2)
    
    # Optionally create a vector store (you can use this later for search)
    print("Creating vector store using OpenAI embeddings...")
    vector_store = create_vector_store(chunks)
    
    # Save the processed chunks to a text file
    print(f"Saving processed text to {output_txt_path}...")
    save_text_chunks_to_txt(chunks, output_txt_path)
    
    print(f"Processing complete for {local_pdf_path}")

if __name__ == "__main__":
    # Choose between a local file or S3 URL for the PDF
    # we have two pdf file paths on the AWS S3 documentation 
    # https://docs.aws.amazon.com/pdfs/AmazonS3/latest/userguide/s3-userguide.pdf
    # https://docs.aws.amazon.com/pdfs/AmazonS3/latest/API/s3-api.pdf

    LOCAL_PDF_PATH = 'https://docs.aws.amazon.com/pdfs/AmazonS3/latest/userguide/s3-userguide.pdf'  # For local or web URL PDF
    S3_PDF_PATH = 's3://your-bucket-name/path/to/s3-file.pdf'  # For S3 PDF
    OUTPUT_TXT_PATH = 'processed_output.txt'
    
    ######### Set to True if you want to load the PDF from S3  ##################

    IS_S3 = False  # Change to False for local files or Web URL
    
    # Ensure the OPENAI_API_KEY is set before running    
    process_pdf(pdf_path=S3_PDF_PATH if IS_S3 else LOCAL_PDF_PATH, output_txt_path=OUTPUT_TXT_PATH, is_s3=IS_S3)
