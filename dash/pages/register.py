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


# register.py - Form Component
layout = dmc.Center(  
    dmc.Paper(  
        shadow='md',  
        p="40px",  
        mt=60,  
        style={"maxWidth": "500px", "width": "100%"},  
        children=[  
            html.Form(  
                method='POST',
                action='/register',  # Added action attribute
                id="registration-form",  # Added ID for reference
                children=[  
                    dmc.Stack(  
                        gap="lg",  
                        children=[  
                            dmc.Group(  
                                children=[  
                                    dmc.Text("Create Account", size='xl', fw=700),  
                                    iconify(icon="fluent:app-store-24-regular", width=30),  
                                ],  
                                align="apart"  
                            ),  
                            dmc.Text("Join our cloud management platform", c='dimmed', size='sm'),  
                            # Personal Information Section  
                            dmc.Stack(  
                                gap="sm",  
                                children=[  
                                    dmc.Group(  
                                        grow=True,  
                                        children=[  
                                            dmc.TextInput(  
                                                label="First Name",  
                                                name='given_name',  
                                                placeholder="Enter your first name",  
                                                required=True,  
                                            ),  
                                            dmc.TextInput(  
                                                label="Last Name",  
                                                name='last_name',  
                                                placeholder="Enter your last name",  
                                                required=True,  
                                            ),  
                                        ]  
                                    ),  
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
                            

                            # Company Information Section
                            dmc.Stack(
                                gap="sm",
                                children=[
                                    dmc.Text("Company Information", fw=500, size="lg", mt="md"),
                                    dmc.TextInput(
                                        label="Company Name",
                                        name='company_name',
                                        placeholder="Enter your company name",
                                        required=True,
                                        leftSection=iconify(icon="mdi:company", width=20),
                                    ),
                                    dmc.Textarea(
                                        label="Company Address",
                                        name='company_address',
                                        placeholder="Enter your company address",
                                        required=True,
                                        minRows=2,
                                    ),
                                ]
                            ),
                            dmc.Stack(
                                gap="sm",
                                children=[
                                    dmc.Text("Cloud Platform Information", fw=500, size="lg", mt="md"),
                                    dmc.CheckboxGroup(
                                        id="cloud-platforms-group",
                                        label="Which cloud platforms do you use?",
                                        value=[],  # Initial empty selection
                                        children=[
                                            dmc.Checkbox(label="AWS", value="aws"),
                                            dmc.Checkbox(label="Azure", value="azure"),
                                            dmc.Checkbox(label="GCP", value="gcp"),
                                        ],
                                    ),
                                    # Hidden input to store checkbox values
                                    dcc.Input(
                                        id='cloud-platforms-hidden',
                                        type='hidden',
                                        name='cloud_platforms'
                                    ),
                                    dmc.TextInput(
                                        label="Other Cloud Platform",
                                        name='other_cloud',
                                        placeholder="Specify other cloud platform",
                                    ),
                                ]
                            ),
                            # AWS Credentials Section
                            dmc.Stack(
                                gap="sm",
                                children=[
                                    dmc.Text("AWS Credentials", fw=500, size="lg", mt="md"),
                                    dmc.PasswordInput(
                                        label="AWS Access Key",
                                        name='aws_access_key',
                                        placeholder="Enter AWS Access Key",
                                        leftSection=iconify(icon="simple-icons:amazonaws", width=20),
                                    ),
                                    dmc.PasswordInput(
                                        label="AWS Secret Key",
                                        name='aws_secret_key',
                                        placeholder="Enter AWS Secret Key",
                                        leftSection=iconify(icon="simple-icons:amazonaws", width=20),
                                    ),
                                ]
                            ),
                            html.Button(
                                children="Create Account",
                                n_clicks=0, 
                                type="submit",
                                id="register-button",
                                style={
                                    "width": "100%",
                                    "background": "linear-gradient(to right, indigo, cyan)",
                                    "color": "white",
                                    "border": "none",
                                    "padding": "10px 20px",
                                    "border-radius": "5px",
                                    "cursor": "pointer",
                                    "font-size": "16px",
                                }
                            ), 
                            # Sign-in link remains the same
                            dmc.Group(  
                                align="center",  
                                mt="md",  
                                children=[  
                                    dmc.Text("Already have an Account?", c='dimmed', size='sm'),  
                                    dmc.Anchor(  
                                        "Sign in",  
                                        href='/login',  
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
