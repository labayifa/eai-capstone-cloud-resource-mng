from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError
from flasgger import Swagger

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

if __name__ == '__main__':
    app.run(debug=True)
