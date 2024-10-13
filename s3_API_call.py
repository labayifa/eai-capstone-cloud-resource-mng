from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)


# Create a session and S3 client
sess = boto3.Session(region_name='us-west-2')  # Change to your desired region
s3client = sess.client('s3')

def create_bucket(bucket_name):
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
    """Delete an S3 bucket."""
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
    """Uplaod a file to an S3 bucket """
    try:
        s3client.upload_fileobj(file,bucket_name,object_name)  
        return f"File '{object_name}' uploaded successfully to '{bucket_name}'."
    except ClientError as e:
        return f"Error Uploading File: {e}"
    
@app.route('/create-bucket', methods=['POST'])
def api_create_bucket():
    data = request.json
    bucket_name = data.get('bucket_name')
    
    if not bucket_name:
        return jsonify({"error": "Bucket name is required"}), 400
    
    result = create_bucket(bucket_name)
    return jsonify({"message": result}), 200

@app.route('/delete-bucket', methods=['DELETE'])
def api_delete_bucket():
    data = request.json
    bucket_name = data.get('bucket_name')
    
    if not bucket_name:
        return jsonify({"error": "Bucket name is required"}), 400
    
    result = delete_bucket(bucket_name)
    return jsonify({"message": result}), 200

@app.route('/upload-file',methods=['POST'])
def uploda_file_api():
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