from dash import html, dcc, Output, Input, callback, register_page
from flask import session
import json
import dash_mantine_components as dmc
from utils.helpers import iconify

register_page(__name__)

def create_info_section(title, content, icon=None):
    """Helper function to create consistent info sections"""
    return dmc.Paper(
        p="md",
        radius="sm",
        withBorder=True,
        children=[
            dmc.Group(
                ta="apart",
                children=[
                    dmc.Group(
                        children=[
                            iconify(icon=icon, width=20) if icon else None,
                            dmc.Text(title, fw=500),
                        ]
                    ),
                ]
            ),
            dmc.Stack(
                mt="xs",
                children=[
                    dmc.Text(f"{key}: {value}", size="sm", c="dimmed")
                    for key, value in content.items()
                ]
            )
        ]
    )

# def layout(**kwargs):
#     if 'email' in session:
#         account = session.get('email', {})

#         # Assuming `account` is a dictionary-like object
#         personal_info = {
#             "First Name": account.get("given_name", "N/A"),
#             "Last Name": account.get("last_name", "N/A"),
#             "Email": account.get("email", "N/A")
#         }

#         company_info = {
#             "Company Name": account.get("company_info.name", "N/A"),
#             "Company Address": account.get("company_address", "N/A")
#         }

#         cloud_info = {
#             "Cloud Platforms": ", ".join(account.get("cloud_platforms", [])),
#             "Other Platform": account.get("other_cloud", "N/A")
#         }

#         # Mask AWS credentials for security
#         aws_info = {
#             "AWS Access Key": f"****{account.get('aws_access_key', '')[-4:]}",
#             "AWS Secret Key": f"****{account.get('aws_secret_key', '')[-4:]}"
#         }

def layout(**kwargs):
    if 'email' in session:
        account = session.get('email', {})

        # Personal information
        personal_info = {
            "First Name": account.get("given_name", "N/A"),
            "Last Name": account.get("last_name", "N/A"),
            "Email": account.get("email", "N/A")
        }

        # Company information - updated to match nested structure
        company_info = {
            "Company Name": account.get("company_info", {}).get("name", "N/A"),
            "Company Address": account.get("company_info", {}).get("address", "N/A")
        }

        # Cloud platforms information - updated to match nested structure
        cloud_info = {
            "Cloud Platforms": ", ".join(account.get("cloud_platforms", {}).get("selected_platforms", [])),
            "Other Platform": account.get("cloud_platforms", {}).get("other_platform", "N/A")
        }

        # AWS credentials - updated to match nested structure
        aws_info = {
            "AWS Access Key": f"****{account.get('aws_credentials', {}).get('access_key', '')[-4:]}",
            "AWS Secret Key": f"****{account.get('aws_credentials', {}).get('secret_key', '')[-4:]}"
        }

        return dmc.Center(
            mt=50,
            children=[
                dmc.Paper(
                    shadow="md",
                    p="xl",
                    style={"maxWidth": "800px", "width": "100%"},
                    children=[
                        dmc.Stack(
                            gap="lg",
                            children=[
                                # Header
                                dmc.Group(
                                    ta="apart",
                                    children=[
                                        dmc.Title("Account Details", order=2),
                                        dmc.Button(
                                            "Edit Profile",
                                            leftSection=iconify(icon="feather:edit", width=16),
                                            variant="light",
                                        )

                                    ]
                                ),
                                dmc.Grid(
                                    gutter="lg",  # Spacing between grid items
                                    children=[
                                        dmc.Group(
                                            create_info_section(
                                                "Personal Information",
                                                personal_info,
                                                "mdi:account"
                                            ),
                                            style={"flex": "1 1 45%"},  # Ensures two items per row on wider screens
                                        ),
                                        dmc.Group(
                                            create_info_section(
                                                "Company Information",
                                                company_info,
                                                "mdi:company"
                                            ),
                                            style={"flex": "1 1 45%"},
                                        ),
                                        dmc.Group(
                                            create_info_section(
                                                "Cloud Platform Information",
                                                cloud_info,
                                                "mdi:cloud"
                                            ),
                                            style={"flex": "1 1 45%"},
                                        ),
                                        dmc.Group(
                                            create_info_section(
                                                "AWS Credentials",
                                                aws_info,
                                                "simple-icons:amazonaws"
                                            ),
                                            style={"flex": "1 1 45%"},
                                        ),
                                    ],
                                    style={"display": "flex", "flexWrap": "wrap"},  # Enables responsive behavior
                                ),
                                dmc.Accordion(
                                    chevronPosition="left",
                                    children=[
                                        dmc.AccordionItem(
                                            value="raw_account_data",  # Unique value for identification
                                            children=[
                                                dmc.Text("Raw Account Data", fw=500, mb="md"),  # Replaces `label`
                                                dmc.CodeHighlight(
                                                    language="json",
                                                    code=json.dumps(account, indent=2),
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )

    else:
        return dmc.Center(
            style={"height": "100vh"},
            children=[
                dmc.Paper(
                    p="xl",
                    shadow="md",
                    radius="md",
                    style={"maxWidth": "400px", "width": "100%"},
                    children=[
                        dmc.Stack(
                            ta="center",
                            gap="md",
                            children=[
                                iconify(icon="mdi:lock-alert", width=48),
                                dmc.Text(
                                    "This page requires authentication",
                                    ta="center",
                                    size="lg",
                                    fw=500
                                ),
                                dmc.Group(
                                    gap="xs",
                                    children=[
                                        dmc.Text("Please"),
                                        dmc.Anchor(
                                            "login",
                                            href="/login",
                                            size="sm",
                                            fw=500,
                                        ),
                                        dmc.Text("to continue"),
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )

