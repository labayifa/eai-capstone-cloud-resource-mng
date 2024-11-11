# Project Setup and Running Instructions

## Prerequisites

### AWS Credentials Configuration
Set up your AWS credentials by exporting the following environment variables:
```bash
export AWS_ACCESS_KEY_ID='AKIAU6GDZD3MNLTT7TON'
export AWS_SECRET_ACCESS_KEY='rYKBlDlORgEZfNi0H99D8SdlIYXZhtpVWR5TYtRo'
```

## Running the Application

### Backend Server
To start the backend server:
```bash
python3 s3_API_call_v3.py
```

### Chainlit Interface
To launch the Chainlit application:
```bash
chainlit run chat_agent_no_pilot_v2.py
```

## Project Structure
- `s3_API_call_v3.py`: Backend server implementation
- `chat_agent_no_pilot_v2.py`: Chainlit chat interface

## Additional Information
- Ensure all required dependencies are installed before running the application
- Make sure both backend and Chainlit interface are running for full functionality
