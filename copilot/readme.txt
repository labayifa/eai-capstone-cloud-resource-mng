1, make sure you have requirement.txt with the following packages listed:

pip install python-dotenv
pip install langchain-openai
pip install langchain
pip install faiss-cpu
pip install langchain-community
pip install langchain-text-splitters
pip install tavily-python
pip install chainlit
pip install requests

2, Create virtual environment / or use the one you have if you're in you pc ... on powershel and inside 'copilot' directory 
use the active script

python -m venv .venv

3, activate it:

.\.venv\Scripts\activate

4, install it by :

pip install -r requirements.txt

5, run the copilot by :

chainlit run chainlit_copilot.py


For the backend script:

1, switch to WSL - linux simply

2, cd copilot

3, python3 s3_API_call_v3.py


for frontend

1, Goto powershell

2, then cd Dash

2, run: python3 app.py