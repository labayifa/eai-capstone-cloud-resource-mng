from flask import Flask, request, jsonify,send_file
import boto3
from botocore.exceptions import ClientError
from flasgger import Swagger
import os


app = Flask(__name__)

swagger = Swagger(app, template={
    "info": {
        "title": "S3 API",
        "description": "An S3 API using Flask and Swagger",
        "version": "1.0.0"
    }
})

def create_s3_client(access_key, secret_key, region):
    """
    Create an S3 client using provided AWS credentials.
    Args:
        access_key (str): The AWS access key.
        secret_key (str): The AWS secret key.
        region (str): The AWS region.
    Returns:
        S3 Client
    """
    return boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)

def create_bucket(bucket_name, access_key, secret_key, region):
    """
    Create an S3 bucket.
    """
    s3client = create_s3_client(access_key, secret_key, region)
    try:
        if region == 'us-east-1':
            s3client.create_bucket(Bucket=bucket_name)
        else:
            s3client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        return f"Bucket '{bucket_name}' created successfully."
    except ClientError as e:
        return f"Error creating bucket: {e}"

def delete_bucket(bucket_name, access_key, secret_key, region):
    """
    Delete an S3 bucket and all its contents.
    """
    s3client = create_s3_client(access_key, secret_key, region)
    try:
        objects = s3client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in objects:
            for obj in objects['Contents']:
                s3client.delete_object(Bucket=bucket_name, Key=obj['Key'])
        
        s3client.delete_bucket(Bucket=bucket_name)
        return f"Bucket '{bucket_name}' deleted successfully."
    except ClientError as e:
        return f"Error deleting bucket: {e}"
    
def upload_file_to_s3(file, bucket_name, access_key, secret_key, region, object_name):
    """
    Uploads a file to an S3 bucket.
    """
    s3client = create_s3_client(access_key, secret_key, region)
    try:
        s3client.upload_fileobj(file, bucket_name, object_name)
        return f"File '{object_name}' uploaded successfully to '{bucket_name}'."
    except ClientError as e:
        return f"Error uploading file: {e}"

@app.route('/create-bucket', methods=['POST'])
def api_create_bucket():
    """
    API endpoint to create an S3 bucket.
    ---
    tags:
      - S3 Bucket Management
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: JSON payload with bucket_name, access_key, secret_key, and region
        required: true
        schema:
          type: object
          required:
            - bucket_name
            - access_key
            - secret_key
            - region
          properties:
            bucket_name:
              type: string
              description: The name of the bucket to create
            access_key:
              type: string
              description: AWS access key
            secret_key:
              type: string
              description: AWS secret key
            region:
              type: string
              description: AWS region
    responses:
      200:
        description: Bucket created successfully
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Error occurred
        schema:
          type: object
          properties:
            error:
              type: string
    """
    data = request.json
    bucket_name = data.get('bucket_name')
    access_key = data.get('access_key')
    secret_key = data.get('secret_key')
    region = data.get('region')

    if not all([bucket_name, access_key, secret_key, region]):
        return jsonify({"error": "Bucket name, access key, secret key, and region are required."}), 400

    result = create_bucket(bucket_name, access_key, secret_key, region)
    return jsonify({"message": result}), 200

@app.route('/delete-bucket', methods=['DELETE'])
def api_delete_bucket():
    """
    Deletes an S3 bucket based on the provided bucket name.
    ---
    tags:
      - S3 Bucket Management
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: JSON payload with bucket_name, access_key, secret_key, and region
        required: true
        schema:
          type: object
          required:
            - bucket_name
            - access_key
            - secret_key
            - region
          properties:
            bucket_name:
              type: string
              description: The name of the bucket to delete
            access_key:
              type: string
              description: AWS access key
            secret_key:
              type: string
              description: AWS secret key
            region:
              type: string
              description: AWS region
    responses:
      200:
        description: Bucket deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Error occurred
        schema:
          type: object
          properties:
            error:
              type: string
    """
    data = request.json
    bucket_name = data.get('bucket_name')
    access_key = data.get('access_key')
    secret_key = data.get('secret_key')
    region = data.get('region')

    if not all([bucket_name, access_key, secret_key, region]):
        return jsonify({"error": "Bucket name, access key, secret key, and region are required."}), 400

    result = delete_bucket(bucket_name, access_key, secret_key, region)
    return jsonify({"message": result}), 200

@app.route('/upload-file', methods=['POST'])
def upload_file_api():
    """
    Uploads a file to an S3 bucket.
    ---
    tags:
      - S3 Bucket Management
    consumes:
      - multipart/form-data
    produces:
      - application/json
    parameters:
      - in: formData
        name: bucket_name
        type: string
        required: true
        description: The name of the bucket to upload the file to
      - in: formData
        name: access_key
        type: string
        required: true
        description: AWS access key
      - in: formData
        name: secret_key
        type: string
        required: true
        description: AWS secret key
      - in: formData
        name: region
        type: string
        required: true
        description: AWS region
      - in: formData
        name: file
        type: file
        required: true
        description: The file to upload
    responses:
      200:
        description: File uploaded successfully
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Error occurred
        schema:
          type: object
          properties:
            error:
              type: string
    """
    data = request.form
    bucket_name = data.get('bucket_name')
    access_key = data.get('access_key')
    secret_key = data.get('secret_key')
    region = data.get('region')
    file = request.files.get('file')

    if not all([bucket_name, access_key, secret_key, region, file]):
        return jsonify({"error": "Bucket name, access key, secret key, region, and file are required."}), 400

    object_name = file.filename
    result = upload_file_to_s3(file, bucket_name, access_key, secret_key, region, object_name)
    return jsonify({"message": result}), 200
def list_s3_buckets(access_key, secret_key, region):
    """
    Retrieve a list of all S3 buckets in the specified AWS account.
    
    Args:
        access_key (str): The AWS access key.
        secret_key (str): The AWS secret key.
        region (str): The AWS region.
    
    Returns:
        list: A list of bucket names, or an error message if an exception occurs.
    """
    s3client = create_s3_client(access_key, secret_key, region)
    
    try:
        # List all buckets in the account
        response = s3client.list_buckets()
        
        # Extract and return the bucket names from the response
        bucket_names = [bucket['Name'] for bucket in response['Buckets']]
        return bucket_names
    
    except ClientError as e:
        # Return an error message if an exception occurs
        return f"Error retrieving bucket list: {e}"

@app.route('/list-buckets', methods=['GET'])
def api_list_buckets():
    """
    API endpoint to retrieve the list of available S3 buckets.
    ---
    tags:
      - S3 Bucket Management
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: query
        name: access_key
        type: string
        required: true
        description: AWS access key
      - in: query
        name: secret_key
        type: string
        required: true
        description: AWS secret key
      - in: query
        name: region
        type: string
        required: true
        description: AWS region
    responses:
      200:
        description: List of S3 buckets
        schema:
          type: object
          properties:
            buckets:
              type: array
              items:
                type: string
      400:
        description: Error occurred
        schema:
          type: object
          properties:
            error:
              type: string
    """
    # Retrieve query parameters
    access_key = request.args.get('access_key')
    secret_key = request.args.get('secret_key')
    region = request.args.get('region')

    if not all([access_key, secret_key, region]):
        return jsonify({"error": "Access key, secret key, and region are required."}), 400

    # Call the function to list buckets
    buckets = list_s3_buckets(access_key, secret_key, region)
    
    if isinstance(buckets, list):
        return jsonify({"buckets": buckets}), 200
    else:
        return jsonify({"error": buckets}), 400
      
@app.route('/rename-bucket', methods=['POST'])
def rename_bucket_api():
    """
    Rename an existing S3 bucket by copying its contents to a new bucket and deleting the old one.
    ---
    tags:
      - S3 Bucket Management
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: JSON payload with old_bucket_name, new_bucket_name, access_key, secret_key, and region
        required: true
        schema:
          type: object
          required:
            - old_bucket_name
            - new_bucket_name
            - access_key
            - secret_key
            - region
          properties:
            old_bucket_name:
              type: string
              description: The name of the existing bucket
            new_bucket_name:
              type: string
              description: The name of the new bucket
            access_key:
              type: string
              description: AWS access key
            secret_key:
              type: string
              description: AWS secret key
            region:
              type: string
              description: AWS region
    responses:
      200:
        description: Bucket renamed successfully
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Error occurred
        schema:
          type: object
          properties:
            error:
              type: string
    """
    data = request.json
    old_bucket_name = data.get('old_bucket_name')
    new_bucket_name = data.get('new_bucket_name')
    access_key = data.get('access_key')
    secret_key = data.get('secret_key')
    region = data.get('region')

    if not all([old_bucket_name, new_bucket_name, access_key, secret_key, region]):
        return jsonify({"error": "Old bucket name, new bucket name, access key, secret key, and region are required."}), 400

    s3client = create_s3_client(access_key, secret_key, region)

    # Step 1: Create the new bucket
    try:
        create_bucket(new_bucket_name, access_key, secret_key, region)
    except Exception as e:
        return jsonify({"error": f"Error creating new bucket: {e}"}), 400

    # Step 2: Copy all objects from the old bucket to the new one
    try:
        objects = s3client.list_objects_v2(Bucket=old_bucket_name)
        if 'Contents' in objects:
            for obj in objects['Contents']:
                copy_source = {'Bucket': old_bucket_name, 'Key': obj['Key']}
                s3client.copy_object(CopySource=copy_source, Bucket=new_bucket_name, Key=obj['Key'])
    except ClientError as e:
        return jsonify({"error": f"Error copying objects: {e}"}), 400

    # Step 3: Delete objects from the old bucket
    try:
        if 'Contents' in objects:
            for obj in objects['Contents']:
                s3client.delete_object(Bucket=old_bucket_name, Key=obj['Key'])
    except ClientError as e:
        return jsonify({"error": f"Error deleting objects from old bucket: {e}"}), 400

    # Step 4: Delete the old bucket
    try:
        s3client.delete_bucket(Bucket=old_bucket_name)
    except ClientError as e:
        return jsonify({"error": f"Error deleting old bucket: {e}"}), 400

    return jsonify({"message": f"Bucket renamed successfully from '{old_bucket_name}' to '{new_bucket_name}'."}), 200

def download_file_from_s3(bucket_name, access_key, secret_key, region, file_name, download_path):
    """
    Download a file from an S3 bucket.
    """
    s3client = create_s3_client(access_key, secret_key, region)
    try:
        s3client.download_file(bucket_name, file_name, download_path)
        return f"File '{file_name}' downloaded successfully from '{bucket_name}'."
    except ClientError as e:
        error_message = f"Error downloading file: {e.response['Error']['Message']}"
        return error_message

@app.route('/download-file', methods=['GET'])
def download_file_api():
    """
    Download a file from an S3 bucket.
    """
    # Get parameters from query string
    bucket_name = request.args.get('bucket_name')
    access_key = request.args.get('access_key')
    secret_key = request.args.get('secret_key')
    region = request.args.get('region')
    file_name = request.args.get('file_name')

    # Check if all required parameters are provided
    if not all([bucket_name, access_key, secret_key, region, file_name]):
        return jsonify({"error": "Bucket name, access key, secret key, region, and file name are required."}), 400

    # Define the path where the file will be saved (current working directory)
    download_path = os.path.join(os.getcwd(), file_name)

    # Attempt to download the file
    result = download_file_from_s3(bucket_name, access_key, secret_key, region, file_name, download_path)

    # Check if there was an error in downloading
    if "Error" in result:
        return jsonify({"error": result}), 400

    # Send the file for download as an attachment
    return send_file(download_path, as_attachment=True)
  
if __name__ == '__main__':
    app.run(debug=True)
