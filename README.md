# REST API for Calling S3
# *Overview*

This Flask application provides a RESTful API to interact with Amazon S3 for basic bucket management and file storage operations. The API enables users to create S3 buckets, delete them, and upload files to the buckets.

# Features
1. Create S3 Bucket: Create a new S3 bucket in a specified AWS region.
2. Delete S3 Bucket: Delete an S3 bucket along with all its contents.
3. Upload Files to S3: Upload files to a specified S3 bucket.
# Prerequisites
1. AWS Account: You need AWS credentials with access to S3.
2. AWS CLI or IAM Role: Configure AWS credentials on your machine or server.
3. Python: Ensure Python 3.x is installed.
4. Flask: Install Flask using pip install flask.
5. Boto3: Install the boto3 library using pip install boto3.
