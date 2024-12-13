import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
import time


app = Flask(__name__)
swagger = Swagger(app)

def create_dynamodb_table(aws_access_key, aws_secret_key, region, table_name, partition_key, sort_key=None, read_capacity=5, write_capacity=5):
    """
    Creates a DynamoDB table.

    Parameters:
    - aws_access_key: AWS Access Key ID
    - aws_secret_key: AWS Secret Access Key
    - region: AWS Region
    - table_name: Name of the DynamoDB table
    - partition_key: Partition key for the table
    - sort_key: (optional) Sort key for the table
    - read_capacity: (optional) Read capacity units for the table (default is 5)
    - write_capacity: (optional) Write capacity units for the table (default is 5)

    Returns:
    - Table creation status
    """
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        
        key_schema = [{'AttributeName': partition_key, 'KeyType': 'HASH'}]
        attribute_definitions = [{'AttributeName': partition_key, 'AttributeType': 'S'}]

        if sort_key:
            key_schema.append({'AttributeName': sort_key, 'KeyType': 'RANGE'})
            attribute_definitions.append({'AttributeName': sort_key, 'AttributeType': 'S'})

        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput={
                'ReadCapacityUnits': read_capacity,
                'WriteCapacityUnits': write_capacity
            }
        )

        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        return f"Table {table_name} created successfully."

    except ClientError as e:
        return f"An error occurred: {e.response['Error']['Message']}"

@app.route('/create-table', methods=['POST'])
@swag_from({
    'tags': ['DynamoDB'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'aws_access_key': {'type': 'string'},
                    'aws_secret_key': {'type': 'string'},
                    'region': {'type': 'string'},
                    'table_name': {'type': 'string'},
                    'partition_key': {'type': 'string'},
                    'sort_key': {'type': 'string'}
                },
                'required': ['aws_access_key', 'aws_secret_key', 'region', 'table_name', 'partition_key']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Table created successfully',
            'examples': {
                'application/json': {
                    'message': 'Table TestTable created successfully.'
                }
            }
        },
        '400': {
            'description': 'Error creating table',
            'examples': {
                'application/json': {
                    'message': 'An error occurred: [error message]'
                }
            }
        }
    }
})
def create_table():
    """
    Create DynamoDB Table
    This endpoint allows you to create a new DynamoDB table with specified attributes.
    ---
    """
    data = request.get_json()
    aws_access_key = data['aws_access_key']
    aws_secret_key = data['aws_secret_key']
    region = data['region']
    table_name = data['table_name']
    partition_key = data['partition_key']
    sort_key = data.get('sort_key')

    result = create_dynamodb_table(aws_access_key, aws_secret_key, region, table_name, partition_key, sort_key)
    return jsonify({'message': result})

@app.route('/delete-table', methods=['DELETE'])
@swag_from({
    'tags': ['DynamoDB'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'aws_access_key': {'type': 'string'},
                    'aws_secret_key': {'type': 'string'},
                    'region': {'type': 'string'},
                    'table_name': {'type': 'string'}
                },
                'required': ['aws_access_key', 'aws_secret_key', 'region', 'table_name']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Table deleted successfully',
            'examples': {
                'application/json': {
                    'message': 'Table TestTable deleted successfully.'
                }
            }
        },
        '400': {
            'description': 'Error deleting table',
            'examples': {
                'application/json': {
                    'message': 'An error occurred: [error message]'
                }
            }
        }
    }
})
def delete_table():
    """
    Delete DynamoDB Table
    This endpoint allows you to delete an existing DynamoDB table.
    ---
    """
    data = request.get_json()
    aws_access_key = data['aws_access_key']
    aws_secret_key = data['aws_secret_key']
    region = data['region']
    table_name = data['table_name']

    try:
        # Connect to DynamoDB
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

        # Get the table and delete it
        table = dynamodb.Table(table_name)
        table.delete()

        return jsonify({'message': f'Table {table_name} deleted successfully.'})
    except ClientError as e:
        return jsonify({'message': f'An error occurred: {e.response["Error"]["Message"]}'}), 400

# Function to insert data into DynamoDB
def insert_data_into_dynamodb(aws_access_key, aws_secret_key, region, table_name, partition_key, sort_key, data):
    """
    Inserts data into a DynamoDB table with partition key and sort key.

    Parameters:
    - aws_access_key: AWS Access Key ID
    - aws_secret_key: AWS Secret Access Key
    - region: AWS Region
    - table_name: Name of the DynamoDB table
    - partition_key: Name of the partition key (e.g., 'id')
    - sort_key: Name of the sort key (e.g., 'timestamp')
    - data: The data to insert, should be a dictionary containing 'id', 'status', 'message', 'query'

    Returns:
    - Insertion status
    """
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

        table = dynamodb.Table(table_name)

        # Add timestamp to data (current time)
        data[sort_key] = str(int(time.time()))  # Using UNIX timestamp for the sort key

        # Insert the data into the table
        table.put_item(Item=data)

        return f"Data with id {data[partition_key]} inserted successfully."

    except ClientError as e:
        return f"An error occurred: {e.response['Error']['Message']}"

# New endpoint to insert data into DynamoDB
@app.route('/insert-data', methods=['POST'])
@swag_from({
    'tags': ['DynamoDB'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'aws_access_key': {'type': 'string'},
                    'aws_secret_key': {'type': 'string'},
                    'region': {'type': 'string'},
                    'table_name': {'type': 'string'},
                    'partition_key': {'type': 'string'},
                    'sort_key': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string'},
                            'status': {'type': 'integer'},
                            'message': {'type': 'string'},
                            'query': {'type': 'string'}
                        },
                        'required': ['id', 'status', 'message', 'query']
                    }
                },
                'required': ['aws_access_key', 'aws_secret_key', 'region', 'table_name', 'partition_key', 'sort_key', 'data']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Data inserted successfully',
            'examples': {
                'application/json': {
                    'message': 'Data with id FB005 inserted successfully.'
                }
            }
        },
        '400': {
            'description': 'Error inserting data',
            'examples': {
                'application/json': {
                    'message': 'An error occurred: [error message]'
                }
            }
        }
    }
})
def insert_data():
    """
    Insert data into DynamoDB Table
    This endpoint allows you to insert data into the specified DynamoDB table.
    --- 
    """
    data = request.get_json()
    aws_access_key = data['aws_access_key']
    aws_secret_key = data['aws_secret_key']
    region = data['region']
    table_name = data['table_name']
    partition_key = data['partition_key']
    sort_key = data['sort_key']
    item_data = data['data']

    # Call the function to insert the data
    result = insert_data_into_dynamodb(aws_access_key, aws_secret_key, region, table_name, partition_key, sort_key, item_data)
    return jsonify({'message': result})

def read_all_items_from_dynamodb(aws_access_key, aws_secret_key, region, table_name):
    """
    Reads all items from the specified DynamoDB table.

    Parameters:
    - aws_access_key: AWS Access Key ID
    - aws_secret_key: AWS Secret Access Key
    - region: AWS Region
    - table_name: Name of the DynamoDB table

    Returns:
    - List of items in the table or error message
    """
    try:
        # Create a DynamoDB client
        dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

        # Perform a scan to retrieve all items
        response = dynamodb.scan(TableName=table_name)

        # Get the list of items from the response
        items = response.get('Items', [])
        
        return items

    except ClientError as e:
        return f"An error occurred: {e.response['Error']['Message']}"

@app.route('/read-items', methods=['GET'])
def read_items():
    """
    Endpoint to read all items from DynamoDB table.
    ---
    """
    # Get the parameters from the request
    aws_access_key = request.args.get('aws_access_key')
    aws_secret_key = request.args.get('aws_secret_key')
    region = request.args.get('region')
    table_name = request.args.get('table_name')

    # Call the function to read all items
    result = read_all_items_from_dynamodb(aws_access_key, aws_secret_key, region, table_name)

    # Return the result
    if isinstance(result, list):
        return jsonify({'items': result})
    else:
        return jsonify({'message': result}), 400
if __name__ == '__main__':
    app.run(debug=True)

