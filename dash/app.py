from dash import (
    Dash, html, ALL, dcc, callback, Input, Output, State, 
    clientside_callback, ClientsideFunction,
    _dash_renderer, page_registry, page_container, no_update, set_props
)
from flask import Flask, request, redirect, session, url_for
import json, os
import dash_mantine_components as dmc
from datetime import datetime
# from flask import request, redirect

from authlib.integrations.flask_client import OAuth

# Internal Imports
from components.header import header
from components.sidebar import sidebar
from utils.helpers import iconify
from appconfig import stylesheets

_dash_renderer._set_react_version("18.2.0")

# with open('db.json', 'r') as openfile:
with open('../db.json', 'r') as openfile:
    db = json.load(openfile)
 

server = Flask(__name__)
server.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))


# chainlit running port, that bring a copilot to the dash app
external_scripts = [
    'http://localhost:8000/copilot/index.js'
]

app = Dash(
    __name__, 
    server=server, 
    use_pages=True,
    external_stylesheets=stylesheets,
    external_scripts=external_scripts
)


server = app.server

oauth = OAuth(server)

google = oauth.register(
    name='google',
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    api_base_url='https://www.googleapis.com/oauth2/v3/',
    client_kwargs={'scope': 'openid profile email'}
)

app.layout = dmc.MantineProvider(
    id="mantine-provider",
    children = [
        dmc.AppShell(
            id="app-shell",
            navbar={ "breakpoint": "md", "collapsed": {"mobile": True}},
            children = [
                dcc.Location(id="url"),
                dmc.AppShellHeader(header()),
                dmc.AppShellNavbar(sidebar, withBorder=True),
                dmc.AppShellMain(page_container),
            ]
        )
    ]   
)

# @server.route('/login', methods=['POST'])
# def login_button_click():
#     if request.form:
#         email = request.form['email']
#         password = request.form['password']
#         user = db.get(email)
#         if user and user['password'] == password:
#             session['email'] = user
#             return redirect('/secret')
#         else:
#             return """invalid username and/or password <a href='/login'>login here</a> or register here <a href='/register'>register here</a> """


# @server.route('/login', methods=['POST'])
# def login_button_click():
#     if request.form:
#         email = request.form['email']
#         password = request.form['password']
#         user = db.get(email)
        
#         if user and user['password'] == password:
#             # Store user in session
#             session['email'] = user
            
#             # Extract AWS credentials
#             aws_credentials = user.get('aws_credentials', {})
#             access_key = aws_credentials.get('access_key', '')
#             secret_key = aws_credentials.get('secret_key', '')
            
#             # Get path to root directory (one level up from dash directory)
#             root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#             secrets_path = os.path.join(root_dir, 'secrets.json')
            
#             # Create or update secrets.json
#             secrets_data = {
#                 'aws_credentials': {
#                     'access_key': access_key,
#                     'secret_key': secret_key
#                 },
#                 'user_email': email
#             }
            
#             try:
#                 # Write credentials to secrets.json with proper formatting
#                 with open(secrets_path, 'w') as f:
#                     json.dump(secrets_data, f, indent=4)
                    
#                 return redirect('/secret')
                
#             except Exception as e:
#                 print(f"Error writing secrets file: {str(e)}")
#                 return """An error occurred while processing your login. Please try again. 
#                          <a href='/login'>login here</a>"""
        
#         else:
#             return """invalid username and/or password <a href='/login'>login here</a> 
#                      or register here <a href='/register'>register here</a> """

def clear_secrets_file(secrets_path):
    """Clear the contents of secrets.json"""
    empty_secrets = {
        "aws_credentials": {
            "access_key": "",
            "secret_key": ""
        },
        "user_email": "",
        "user_first_name": "",
        "user_last_name": ""
    }
    
    try:
        with open(secrets_path, 'w') as f:
            json.dump(empty_secrets, f, indent=4)
    except Exception as e:
        print(f"Error clearing secrets file: {str(e)}")

@server.route('/login', methods=['POST'])
def login_button_click():
    if request.form:
        email = request.form['email']
        password = request.form['password']
        user = db.get(email)
        
        if user and user['password'] == password:
            # Store user in session
            session['email'] = user
            
            # Extract AWS credentials and user details
            aws_credentials = user.get('aws_credentials', {})
            access_key = aws_credentials.get('access_key', '')
            secret_key = aws_credentials.get('secret_key', '')
            first_name = user.get('given_name', '')
            last_name = user.get('last_name', '')
            
            # Get path to root directory (one level up from dash directory)
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            secrets_path = os.path.join(root_dir, 'secrets.json')
            
            try:
                # First clear any existing data
                clear_secrets_file(secrets_path)
                
                # Then write new credentials and user details
                secrets_data = {
                    'aws_credentials': {
                        'access_key': access_key,
                        'secret_key': secret_key
                    },
                    'user_email': email,
                    'user_first_name': first_name,
                    'user_last_name': last_name
                }
                
                with open(secrets_path, 'w') as f:
                    json.dump(secrets_data, f, indent=4)
                    
                return redirect('/secret')
                
            except Exception as e:
                print(f"Error handling secrets file: {str(e)}")
                return """An error occurred while processing your login. Please try again. 
                         <a href='/login'>login here</a>"""
        
        else:
            return """invalid username and/or password <a href='/login'>login here</a> 
                     or register here <a href='/register'>register here</a> """

# @server.route('/register', methods=['POST'])
# def register_button_click():
#     try:
#         if request.method == 'POST':
#             # Print form data for debugging
#             print("Form Data:", request.form)
            
#             # Basic user information
#             given_name = request.form.get('given_name')
#             last_name = request.form.get('last_name')
#             email = request.form.get('email')
#             password = request.form.get('password')

#             # Validate required fields
#             if not all([given_name, last_name, email, password]):
#                 return """Missing required fields. Please <a href='/register'>go back</a> and fill all required fields."""

#             # Check if user already exists
#             user = db.get(email, None)
#             if user:
#                 return f"""User with email {email} already exists. Please <a href='/register'>try again</a> with a different email."""
            
#             # Get company information
#             company_name = request.form.get('company_name', '')
#             company_address = request.form.get('company_address', '')
            
#             # Get cloud platform preferences
#             cloud_platforms = request.form.getlist('cloud_platforms') or []
#             other_cloud = request.form.get('other_cloud', '')
            
#             # Get AWS credentials
#             aws_access_key = request.form.get('aws_access_key', '')
#             aws_secret_key = request.form.get('aws_secret_key', '')
            
#             # Create user data dictionary
#             user_data = {
#                 "given_name": given_name,
#                 "last_name": last_name,
#                 "email": email,
#                 "password": password,
#                 "company_info": {
#                     "name": company_name,
#                     "address": company_address
#                 },
#                 "cloud_platforms": {
#                     "selected_platforms": cloud_platforms,
#                     "other_platform": other_cloud
#                 },
#                 "aws_credentials": {
#                     "access_key": aws_access_key,
#                     "secret_key": aws_secret_key
#                 },
#                 "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             }
            
#             # Save to database
#             db[email] = user_data
#             # with open("db.json", "w") as outfile:
#             with open("../db.json", "w") as outfile:
#                 json.dump(db, outfile, indent=4)
#             return redirect('/login')
            
#     except Exception as e:
#         print("Registration Error:", str(e))  # Add logging for debugging
#         return f"""An error occurred during registration. Please <a href='/register'>try again</a>. Error: {str(e)}"""
    
#     return redirect('/register')


# Add this callback to your app.py
@callback(
    Output('cloud-platforms-hidden', 'value'),
    Input('cloud-platforms-group', 'value')
)
def update_hidden_input(selected_platforms):
    if selected_platforms is None:
        return '[]'
    return json.dumps(selected_platforms)

# Modified registration callback
@server.route('/register', methods=['POST'])
def register_button_click():
    try:
        if request.method == 'POST':
            # Print form data for debugging
            print("Form Data:", request.form)
            
            # Basic user information
            given_name = request.form.get('given_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')

            # Validate required fields
            if not all([given_name, last_name, email, password]):
                return """Missing required fields. Please <a href='/register'>go back</a> and fill all required fields."""

            # Check if user already exists
            user = db.get(email, None)
            if user:
                return f"""User with email {email} already exists. Please <a href='/register'>try again</a> with a different email."""
            
            # Get company information
            company_name = request.form.get('company_name', '')
            company_address = request.form.get('company_address', '')
            
            # Get cloud platform preferences - Parse the JSON string from hidden input
            cloud_platforms_str = request.form.get('cloud_platforms', '[]')
            try:
                cloud_platforms = json.loads(cloud_platforms_str)
            except json.JSONDecodeError:
                cloud_platforms = []
                
            other_cloud = request.form.get('other_cloud', '')
            
            # Print debug information
            print("Selected Cloud Platforms:", cloud_platforms)
            
            # Get AWS credentials
            aws_access_key = request.form.get('aws_access_key', '')
            aws_secret_key = request.form.get('aws_secret_key', '')
            
            # Create user data dictionary
            user_data = {
                "given_name": given_name,
                "last_name": last_name,
                "email": email,
                "password": password,
                "company_info": {
                    "name": company_name,
                    "address": company_address
                },
                "cloud_platforms": {
                    "selected_platforms": cloud_platforms,
                    "other_platform": other_cloud
                },
                "aws_credentials": {
                    "access_key": aws_access_key,
                    "secret_key": aws_secret_key
                },
                "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save to database
            db[email] = user_data
            with open("../db.json", "w") as outfile:
                json.dump(db, outfile, indent=4)
            return redirect('/login')
            
    except Exception as e:
        print("Registration Error:", str(e))
        return f"""An error occurred during registration. Please <a href='/register'>try again</a>. Error: {str(e)}"""
    
    return redirect('/register')
        
# Flask routes for OAuth
@server.route('/signingoogle')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@server.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    resp.raise_for_status()
    user_info = resp.json()
    session['email'] = user_info
    return redirect('/')

@callback(
    Output('avatar-indicator', 'children'),
    Input("url", "pathname"),
)


def update_user_initials(url):
    user = ''
    image = ''
    size = 0
    
    if url == '/logout':
        # Clear the secrets file when logging out
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        secrets_path = os.path.join(root_dir, 'secrets.json')
        clear_secrets_file(secrets_path)
        user = ""
        size = 0
    elif 'email' in session:
        acount = session['email']
        user = f"{acount.get('given_name', '')[:1]}{acount.get('last_name', '')[:1]}"
        image = acount.get('picture', '')
        size = 8
        
    status = dmc.Indicator(
        dmc.Avatar(
            style={"cursor": "pointer"},
            size="md",
            radius="xl",
            src=image,
        ),
        offset=3,
        position="bottom-end",
        styles={
            "indicator": {"height": '20px', "padding": '2px', 'paddingInline': '0px'},
        },
        c='dark',
        size=size,
        label=user,
        withBorder=True,
        id='indicator'
    )
    return status



clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='theme_switcher_callback'
    ),
    Output("mantine-provider", "theme"),
    Output("mantine-provider", "forceColorScheme"),
    Output("color-scheme-toggle", "rightSection"),
    Output("color-scheme-toggle", "label"),
    Input("color-scheme-toggle", "n_clicks")

)
clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='side_bar_toggle'
    ),
    Output("app-shell", "navbar"),
    Input("burger-button", "opened"),
    State("app-shell", "navbar"),

)

if __name__ == "__main__":
    # app.run_server(debug=True, port= 8050)
    app.run_server(debug=False, port= 8050)
