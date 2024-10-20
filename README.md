README for REST API for Calling S3
Overview
This Flask application provides a RESTful API to interact with Amazon S3 for basic bucket management and file storage operations. The API enables users to create S3 buckets, delete them, and upload files to the buckets.

Features
Create S3 Bucket: Create a new S3 bucket in a specified AWS region.
Delete S3 Bucket: Delete an S3 bucket along with all its contents.
Upload Files to S3: Upload files to a specified S3 bucket.
Prerequisites
AWS Account: You need AWS credentials with access to S3.
AWS CLI or IAM Role: Configure AWS credentials on your machine or server.
Python: Ensure Python 3.x is installed.
Flask: Install Flask using pip install flask.
Boto3: Install the boto3 library using pip install boto3.
