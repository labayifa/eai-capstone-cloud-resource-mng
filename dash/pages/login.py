# import dash
# from dash import html, dcc
# from utils.helpers import iconify
# import dash_mantine_components as dmc 

# dash.register_page(__name__)
# from dash_iconify import DashIconify


# dash.register_page(__name__)
# loginButtonStyle =   {
#     "background": "#E418C2ff",
#     "padding": "5px 20px" ,
#     "border": "none",
#     "borderRadius": "20px",
#     "color": "white",
#     "fontSize":"16px",
#     "width":"100%"
    
#   }

# loginWithGoogleStyle =   {
#     "textDecoration": "white",
#     "borderRadius": "50px",
#   }

# layout = dmc.Center(
#     dmc.Paper(
#         shadow='sm',
#         p = "30px",
#         mt = 60,
#         children = [
#             html.Form(
#                 style = {"width":'300px'},
#                 method='POST',
#                 children = [
#                     dmc.Text("Sign in ",  size='xl', fw=700),
#                     dmc.Text("Please log in to continue", c='gray', size='xs', mb = 10),
#                     dmc.TextInput(
#                         label="Email",
#                         name='email',
#                         placeholder="Enter your Email",
#                         required = True,

#                         leftSection=iconify(icon="ic:round-alternate-email", width=20),
#                     ),
#                     dmc.PasswordInput(
#                         mb=20,
#                         label="Password",
#                         placeholder="Enter your password",
#                         leftSection=iconify(icon="bi:shield-lock", width=20),
#                         name='password',
#                         required = True
#                     ),
#                     html.Button(
#                         children="Sign in", 
#                         n_clicks=0, 
#                         type="submit", 
#                         id="login-button", 
#                         style =loginButtonStyle
#                     ),
#                 ]
#             )
#         ]
#     )
# )


import dash
from dash import html, dcc
from utils.helpers import iconify
import dash_mantine_components as dmc

dash.register_page(__name__)

buttonStyle = {  
    "background": "linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)",  
    "padding": "10px 24px",  
    "border": "none",  
    "borderRadius": "8px",  
    "color": "white",  
    "fontSize": "16px",  
    "width": "100%",  
    "cursor": "pointer",  
    "transition": "transform 0.2s",  
    "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)"  
}

layout = dmc.Center(
    dmc.Paper(
        shadow='md',
        p="40px",
        mt=60,
        style={"maxWidth": "500px", "width": "100%"},
        children=[
            html.Form(
                method='POST',
                id="login-form",  # Added ID for reference
                children=[
                    dmc.Stack(
                        gap="lg",
                        children=[
                            dmc.Group(
                                children=[
                                    dmc.Text("Sign in", size='xl', fw=700),
                                    iconify(icon="fluent:signin-24-regular", width=30),
                                ],
                                align="apart"
                            ),
                            dmc.Text(
                                "Welcome back! Please log in to access your account",
                                c='dimmed',
                                size='sm'
                            ),
                            # Input fields for login
                            dmc.Stack(
                                gap="sm",
                                children=[
                                    dmc.TextInput(
                                        label="Email",
                                        name='email',
                                        placeholder="Enter your Email",
                                        required=True,
                                        leftSection=iconify(icon="ic:round-alternate-email", width=20),
                                    ),
                                    dmc.PasswordInput(
                                        label="Password",
                                        placeholder="Enter your password",
                                        leftSection=iconify(icon="bi:shield-lock", width=20),
                                        name='password',
                                        required=True
                                    ),
                                ]
                            ),
                            # Submit button
                            html.Button(
                                children="Sign in",
                                n_clicks=0,
                                type="submit",
                                id="login-button",
                                style=buttonStyle
                            ),
                            # Registration link
                            dmc.Group(
                                align="center",
                                mt="md",
                                children=[
                                    dmc.Text("Don't have an account yet?", c='dimmed', size='sm'),
                                    dmc.Anchor(
                                        "Create an account",
                                        href='/register',
                                        size='sm',
                                        underline=False,
                                        c="indigo"
                                    )
                                ]
                            ),
                        ]
                    )
                ]
            )
        ]
    )
)
