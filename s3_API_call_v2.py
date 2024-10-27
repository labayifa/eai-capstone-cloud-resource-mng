from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError
from flasgger import Swagger

app = Flask(__name__)

# swagger = Swagger(app)

swagger = Swagger(app, template={
    "info": {
        "title": "S3 API",
        "description": "An S3 API using Flask and Swagger",
        "version": "1.0.0"
    }
})
# Create a session and S3 client
sess = boto3.Session(region_name='us-west-2')  # Change to your desired region
s3client = sess.client('s3')

def create_bucket(bucket_name):
    """
    Create an S3 bucket.

    This function attempts to create an Amazon S3 bucket with the specified name.
    If the AWS region is 'us-east-1', it creates the bucket without specifying a region.
    For other regions, it includes the region in the bucket creation configuration.

    Args:
        bucket_name (str): The name of the bucket to create.

    Returns:
        str: A message indicating whether the bucket was created successfully or an error occurred.

    Raises:
        ClientError: If there is an error creating the bucket.
    """
    """Create an S3 bucket."""
    try:
        if s3client.meta.region_name == 'us-east-1':
            s3client.create_bucket(Bucket=bucket_name)
        else:
            s3client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': s3client.meta.region_name}
            )
        return f"Bucket '{bucket_name}' created successfully."
    except ClientError as e:
        return f"Error creating bucket: {e}"

def delete_bucket(bucket_name):
    """
    Delete an S3 bucket and all its contents.
    This function deletes all objects within the specified S3 bucket and then deletes the bucket itself.
    If the bucket does not exist or an error occurs during the deletion process, an error message is returned.
    Args:
        bucket_name (str): The name of the S3 bucket to delete.
    Returns:
        str: A message indicating whether the bucket was deleted successfully or an error occurred.
    Raises:
        ClientError: If there is an error deleting the bucket or its contents.
    """
    try:
        objects = s3client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in objects:
            for obj in objects['Contents']:
                s3client.delete_object(Bucket=bucket_name, Key=obj['Key'])
        
        s3client.delete_bucket(Bucket=bucket_name)
        return f"Bucket '{bucket_name}' deleted successfully."
    except ClientError as e:
        return f"Error deleting bucket: {e}"
    
def upload_file_to_s3(file,bucket_name,object_name):
    def upload_file_to_s3(file, bucket_name, object_name):
        """
        Uploads a file to an S3 bucket.
        Parameters:
        file (file-like object): The file to upload.
        bucket_name (str): The name of the S3 bucket.
        object_name (str): The name of the object in the S3 bucket.
        Returns:
        str: A message indicating whether the file was uploaded successfully or an error occurred.
        Raises:
        ClientError: If there is an error uploading the file to S3.
        """
    
    try:
        s3client.upload_fileobj(file,bucket_name,object_name)  
        return f"File '{object_name}' uploaded successfully to '{bucket_name}'."
    except ClientError as e:
        return f"Error Uploading File: {e}"
    
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
        description: JSON payload with bucket_name
        required: true
        schema:
          type: object
          required:
            - bucket_name
          properties:
            bucket_name:
              type: string
              description: The name of the bucket to create
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
    
    if not bucket_name:
        return jsonify({"error": "Bucket name is required"}), 400
    
    result = create_bucket(bucket_name)
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
        description: JSON payload with bucket_name
        required: true
        schema:
          type: object
          required:
            - bucket_name
          properties:
            bucket_name:
              type: string
              description: The name of the bucket to delete
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
    
    if not bucket_name:
        return jsonify({"error": "Bucket name is required"}), 400
    
    result = delete_bucket(bucket_name)
    return jsonify({"message": result}), 200

@app.route('/upload-file',methods=['POST'])
def uploda_file_api():
    """
    Handles the file upload API request.
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
    if 'file' not in request.files:
        return jsonify({"error":"No file part"}),400
    file= request.files['file']
    
    if file.filename =='':
        return jsonify({"error": "No selected file"}),400
    object_name= file.filename
    result = upload_file_to_s3(file,bucket_name,object_name)
    return jsonify({"message": result}),200
    
if __name__ == '__main__':
    app.run(debug=True)