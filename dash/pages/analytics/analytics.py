# # Data structures remain the same
# from io import StringIO
# import pandas as pd
# from dash_iconify import DashIconify
# from utils.helpers import iconify
# import dash_mantine_components as dmc
# from dash import (
#     Output, Input, callback, clientside_callback, ClientsideFunction,
#     register_page, dcc, html
# )
# feedback_data = [{
#     "positive": 120,
#     "negative": 30
# }]

# detailed_feedback_data = [
#     {
#         "id": "FB001",
#         "value": 1,
#         "comment": "The solution provided was perfect! I was able to create my S3 bucket and upload files within minutes.",
#         "query": "Hi, I need to set up a shared file explorer for 2400 users in Asia with a $20 monthly budget. Can you guide me on setting up an S3 bucket for this?"
#     },
#     {
#         "id": "FB002",
#         "value": 0,
#         "comment": "The service was slow, and I couldn't complete the bucket creation in time.",
#         "query": "I want an S3 bucket named 'my-test-bucket' in the US East region. Can you help me create this?"
#     },
#     {
#         "id": "FB003",
#         "value": 1,
#         "comment": "The response was quick and helped me delete the unnecessary resources efficiently.",
#         "query": "I have changed my mind and no longer need the S3 bucket in Europe. Can you delete it?"
#     },
#     {
#         "id": "FB004",
#         "value": 1,
#         "comment": "The explanation about DynamoDB pricing was clear and helped me plan my budget.",
#         "query": "Can you explain the pricing structure for DynamoDB with a usage pattern of 500 writes per second?"
#     },
#     {
#         "id": "FB005",
#         "value": 0,
#         "comment": "The provided details were not sufficient to resolve my issue with API integration.",
#         "query": "I need to upload a file to my S3 bucket but keep getting a '403 Forbidden' error. Can you assist?"
#     }
# ]


# register_page(__name__, path="/analytics")

# layout = dmc.Box(
#     children=[
#         dcc.Store(id='FeedbackData', data=feedback_data),
#         dcc.Store(id='DetailedFeedbackData', data=detailed_feedback_data),
#         dcc.Download(id="download-feedback-csv"),
#         dmc.Paper(
#             className='ChartAreaDiv',
#             shadow="sm",
#             children=[
#                 dmc.Box(id='feedbackChart'),
#                 dmc.Space(h=20),
#                 dmc.Group(
#                     justify="space-between",
#                     align="center",
#                     children=[
#                         dmc.Text("Customer Feedback Data", size="xl", fw=700),
#                         dmc.ActionIcon(
#                             DashIconify(
#                                 icon="clarity:download-line", width=24),
#                             id="download-button",
#                             variant="subtle",
#                             size="lg",
#                             color="blue",
#                         ),
#                     ],
#                 ),
#                 dmc.Table(
#                     id="feedback-table",
#                     striped=True,
#                     highlightOnHover=True,
#                     withTableBorder=True,
#                     horizontalSpacing="xs",
#                     verticalSpacing="xs",
#                     fz="sm",  # Use 'fz' for font size
#                     children=[
#                         html.Thead(
#                             html.Tr([
#                                 html.Th("ID", style={'width': '10%'}),
#                                 html.Th("Value", style={'width': '10%'}),
#                                 html.Th("Comment", style={'width': '30%'}),
#                                 html.Th("User Query", style={'width': '50%'}),
#                             ])
#                         ),
#                         html.Tbody(id="feedback-table-body")
#                     ],
#                     style={'marginTop': '10px'}
#                 )
#             ]
#         )
#     ]
# )

# # Callbacks remain the same


# @callback(
#     Output("feedbackChart", "children"),
#     Input("FeedbackData", "data"),
# )
# def update_feedback_chart(feedback_data):
#     feedback_dict = feedback_data[0]
#     return dcc.Graph(
#         id='feedback-graph',
#         figure={
#             'data': [
#                 {
#                     'x': ['Positive Feedback', 'Negative Feedback'],
#                     'y': [feedback_dict['positive'], feedback_dict['negative']],
#                     'type': 'bar',
#                     'name': 'Feedback',
#                     'marker': {
#                         'color': ['#34A853', '#EA4335'],
#                         'line': {
#                             'color': '#FFFFFF',
#                             'width': 2
#                         }
#                     }
#                 },
#             ],
#             'layout': {
#                 'title': {
#                     'text': 'Customer Feedback Evaluation',
#                     'font': {
#                         'size': 24,
#                         'color': '#FFFFFF'
#                     }
#                 },
#                 'xaxis': {
#                     'title': 'Feedback Type',
#                     'tickangle': -45,
#                     'title_font': {'size': 18, 'color': '#FFFFFF'},
#                     'tickfont': {'size': 14, 'color': '#FFFFFF'},
#                     'automargin': True,
#                 },
#                 'yaxis': {
#                     'title': 'Number of Feedbacks',
#                     'title_font': {'size': 18, 'color': '#FFFFFF'},
#                     'tickfont': {'size': 14, 'color': '#FFFFFF'},
#                     'gridcolor': '#4F4F4F'
#                 },
#                 'paper_bgcolor': '#1E1E1E',
#                 'plot_bgcolor': '#1E1E1E',
#                 'margin': {'l': 60, 'r': 30, 't': 60, 'b': 75},
#                 'bargap': 0.15,
#             }
#         },
#         config={
#             'displayModeBar': False
#         }
#     )


# @callback(
#     Output("feedback-table-body", "children"),
#     Input("DetailedFeedbackData", "data"),
# )
# def update_feedback_table(detailed_feedback_data):
#     rows = []
#     for feedback in detailed_feedback_data:
#         rows.append(html.Tr([
#             html.Td(feedback['id']),
#             html.Td(
#                 dmc.Badge(
#                     "Positive" if feedback['value'] == 1 else "Negative",
#                     color="green" if feedback['value'] == 1 else "red",
#                     size="sm"
#                 )
#             ),
#             html.Td(feedback['comment'], style={
#                     'maxWidth': '300px', 'whiteSpace': 'normal', 'wordBreak': 'break-word'}),
#             html.Td(feedback['query'], style={
#                     'maxWidth': '500px', 'whiteSpace': 'normal', 'wordBreak': 'break-word'}),
#         ]))
#     return rows


# @callback(
#     Output("download-feedback-csv", "data"),
#     Input("download-button", "n_clicks"),
#     Input("DetailedFeedbackData", "data"),
#     prevent_initial_call=True
# )
# def download_csv(n_clicks, detailed_feedback_data):
#     if n_clicks is None:
#         return None

#     df = pd.DataFrame(detailed_feedback_data)
#     return dcc.send_data_frame(
#         df.to_csv,
#         "feedback_data.csv",
#         index=False
#     )


# import os
# import json
# import pandas as pd
# import boto3
# from io import StringIO
# from dash_iconify import DashIconify
# from utils.helpers import iconify
# import dash_mantine_components as dmc
# from dash import (
#     Output, Input, callback, clientside_callback, ClientsideFunction,
#     register_page, dcc, html
# )

# # DynamoDB Configuration
# dynamodb = boto3.resource('dynamodb',
#                           region_name=os.getenv('AWS_REGION', 'us-west-2'),
#                           aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#                           aws_secret_access_key=os.getenv(
#                               'AWS_SECRET_ACCESS_KEY')
#                           )

# # Replace with your actual DynamoDB table name
# FEEDBACK_TABLE_NAME = 'Feedback'
# feedback_table = dynamodb.Table(FEEDBACK_TABLE_NAME)


# def fetch_dynamodb_feedback():
#     """
#     Fetch feedback items from DynamoDB
#     Returns a list of dictionaries with processed feedback data
#     """
#     try:
#         response = feedback_table.scan()
#         items = response.get('Items', [])

#         # Process DynamoDB AttributeValue format
#         processed_items = [
#             {
#                 'email': item.get('email', {}).get('S', ''),
#                 'id': item.get('id', {}).get('S', ''),
#                 'message': item.get('message', {}).get('S', ''),
#                 'status': int(item.get('status', {}).get('N', 0)),
#                 'timestamp': item.get('timestamp', {}).get('S', '')
#             }
#             for item in items
#         ]

#         return processed_items
#     except Exception as e:
#         print(f"Error fetching DynamoDB items: {e}")
#         return []


# def aggregate_feedback_stats(feedback_data):
#     """
#     Compute overall feedback statistics
#     """
#     positive_count = sum(1 for item in feedback_data if item['status'] == 1)
#     negative_count = len(feedback_data) - positive_count

#     return [{'positive': positive_count, 'negative': negative_count}]


# register_page(__name__, path="/analytics")

# layout = dmc.Box(
#     children=[
#         dcc.Store(id='FeedbackData'),
#         dcc.Store(id='DetailedFeedbackData'),
#         dcc.Download(id="download-feedback-csv"),
#         dmc.Paper(
#             className='ChartAreaDiv',
#             shadow="sm",
#             children=[
#                 dmc.Box(id='feedbackChart'),
#                 dmc.Space(h=20),
#                 dmc.Group(
#                     justify="space-between",
#                     align="center",
#                     children=[
#                         dmc.Text("Customer Feedback Data", size="xl", fw=700),
#                         dmc.ActionIcon(
#                             DashIconify(
#                                 icon="clarity:download-line", width=24),
#                             id="download-button",
#                             variant="subtle",
#                             size="lg",
#                             color="blue",
#                         ),
#                     ],
#                 ),
#                 dmc.Table(
#                     id="feedback-table",
#                     striped=True,
#                     highlightOnHover=True,
#                     withTableBorder=True,
#                     horizontalSpacing="xs",
#                     verticalSpacing="xs",
#                     fz="sm",
#                     children=[
#                         html.Thead(
#                             html.Tr([
#                                 html.Th("ID", style={'width': '10%'}),
#                                 html.Th("Status", style={'width': '10%'}),
#                                 html.Th("Email", style={'width': '30%'}),
#                                 html.Th("Message", style={'width': '50%'}),
#                             ])
#                         ),
#                         html.Tbody(id="feedback-table-body")
#                     ],
#                     style={'marginTop': '10px'}
#                 )
#             ]
#         )
#     ]
# )

# # Interval component to periodically refresh data
# layout.children.insert(0, dcc.Interval(
#     id='interval-component',
#     interval=60*1000,  # 1 minute
#     n_intervals=0
# ))

# # Callback to fetch and store feedback data


# @callback(
#     [Output('FeedbackData', 'data'),
#      Output('DetailedFeedbackData', 'data')],
#     [Input('interval-component', 'n_intervals')]
# )
# def update_feedback_data(n):
#     feedback_data = fetch_dynamodb_feedback()

#     # Compute overall statistics for chart
#     chart_data = aggregate_feedback_stats(feedback_data)

#     return chart_data, feedback_data


# @callback(
#     Output("feedbackChart", "children"),
#     Input("FeedbackData", "data"),
# )
# def update_feedback_chart(feedback_data):
#     if not feedback_data:
#         return dcc.Graph(
#             id='feedback-graph',
#             figure={'layout': {'title': 'No Feedback Data Available'}}
#         )

#     feedback_dict = feedback_data[0]
#     return dcc.Graph(
#         id='feedback-graph',
#         figure={
#             'data': [
#                 {
#                     'x': ['Positive Feedback', 'Negative Feedback'],
#                     'y': [feedback_dict['positive'], feedback_dict['negative']],
#                     'type': 'bar',
#                     'name': 'Feedback',
#                     'marker': {
#                         'color': ['#34A853', '#EA4335'],
#                         'line': {
#                             'color': '#FFFFFF',
#                             'width': 2
#                         }
#                     }
#                 },
#             ],
#             'layout': {
#                 'title': {
#                     'text': 'Customer Feedback Evaluation',
#                     'font': {
#                         'size': 24,
#                         'color': '#FFFFFF'
#                     }
#                 },
#                 'xaxis': {
#                     'title': 'Feedback Type',
#                     'tickangle': -45,
#                     'title_font': {'size': 18, 'color': '#FFFFFF'},
#                     'tickfont': {'size': 14, 'color': '#FFFFFF'},
#                     'automargin': True,
#                 },
#                 'yaxis': {
#                     'title': 'Number of Feedbacks',
#                     'title_font': {'size': 18, 'color': '#FFFFFF'},
#                     'tickfont': {'size': 14, 'color': '#FFFFFF'},
#                     'gridcolor': '#4F4F4F'
#                 },
#                 'paper_bgcolor': '#1E1E1E',
#                 'plot_bgcolor': '#1E1E1E',
#                 'margin': {'l': 60, 'r': 30, 't': 60, 'b': 75},
#                 'bargap': 0.15,
#             }
#         },
#         config={
#             'displayModeBar': False
#         }
#     )


# @callback(
#     Output("feedback-table-body", "children"),
#     Input("DetailedFeedbackData", "data"),
# )
# def update_feedback_table(detailed_feedback_data):
#     if not detailed_feedback_data:
#         return [html.Tr([html.Td("No feedback data available", colSpan=4)])]

#     rows = []
#     for feedback in detailed_feedback_data:
#         rows.append(html.Tr([
#             html.Td(feedback['id']),
#             html.Td(
#                 dmc.Badge(
#                     "Positive" if feedback['status'] == 1 else "Negative",
#                     color="green" if feedback['status'] == 1 else "red",
#                     size="sm"
#                 )
#             ),
#             html.Td(feedback['email'], style={
#                 'maxWidth': '300px', 'whiteSpace': 'normal', 'wordBreak': 'break-word'}),
#             html.Td(feedback['message'], style={
#                 'maxWidth': '500px', 'whiteSpace': 'normal', 'wordBreak': 'break-word'}),
#         ]))
#     return rows


# @callback(
#     Output("download-feedback-csv", "data"),
#     Input("download-button", "n_clicks"),
#     Input("DetailedFeedbackData", "data"),
#     prevent_initial_call=True
# )
# def download_csv(n_clicks, detailed_feedback_data):
#     if n_clicks is None or not detailed_feedback_data:
#         return None

#     df = pd.DataFrame(detailed_feedback_data)
#     return dcc.send_data_frame(
#         df.to_csv,
#         "dynamodb_feedback_data.csv",
#         index=False
#     )


import os
import json
import pandas as pd
import boto3
from io import StringIO
from dash_iconify import DashIconify
from utils.helpers import iconify
import dash_mantine_components as dmc
from dash import (
    Output, Input, callback, clientside_callback, ClientsideFunction,
    register_page, dcc, html
)

# DynamoDB Configuration
# Make sure to set these environment variables or replace with actual credentials
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region = os.getenv('AWS_REGION', 'us-west-2')
table_name = os.getenv('DYNAMODB_TABLE_NAME', 'Feedback')

dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=region
)


def fetch_dynamodb_feedback():
    """
    Fetch feedback items from DynamoDB using client scan method
    Returns a list of dictionaries with processed feedback data
    """
    try:
        # Perform a scan to retrieve all items
        response = dynamodb.scan(TableName=table_name)

        # Get the list of items from the response
        items = response.get('Items', [])

        # Process DynamoDB AttributeValue format
        processed_items = []
        for item in items:
            processed_item = {
                'email': item.get('email', {}).get('S', ''),
                'id': item.get('id', {}).get('S', ''),
                'message': item.get('message', {}).get('S', ''),
                'status': int(item.get('status', {}).get('N', 0)),
                'timestamp': item.get('timestamp', {}).get('S', '')
            }
            processed_items.append(processed_item)

        return processed_items
    except Exception as e:
        print(f"Error fetching DynamoDB items: {e}")
        return []


def aggregate_feedback_stats(feedback_data):
    """
    Compute overall feedback statistics
    """
    positive_count = sum(1 for item in feedback_data if item['status'] == 1)
    negative_count = len(feedback_data) - positive_count

    return [{'positive': positive_count, 'negative': negative_count}]


register_page(__name__, path="/analytics")

layout = dmc.Box(
    children=[
        dcc.Store(id='FeedbackData'),
        dcc.Store(id='DetailedFeedbackData'),
        dcc.Download(id="download-feedback-csv"),
        # Interval component to periodically refresh data
        dcc.Interval(
            id='interval-component',
            interval=60*1000,  # 1 minute
            n_intervals=0
        ),
        dmc.Paper(
            className='ChartAreaDiv',
            shadow="sm",
            children=[
                dmc.Box(id='feedbackChart'),
                dmc.Space(h=20),
                dmc.Group(
                    justify="space-between",
                    align="center",
                    children=[
                        dmc.Text("Customer Feedback Data", size="xl", fw=700),
                        dmc.ActionIcon(
                            DashIconify(
                                icon="clarity:download-line", width=24),
                            id="download-button",
                            variant="subtle",
                            size="lg",
                            color="blue",
                        ),
                    ],
                ),
                dmc.Table(
                    id="feedback-table",
                    striped=True,
                    highlightOnHover=True,
                    withTableBorder=True,
                    horizontalSpacing="xs",
                    verticalSpacing="xs",
                    fz="sm",
                    children=[
                        html.Thead(
                            html.Tr([
                                html.Th("ID", style={'width': '10%'}),
                                html.Th("Status", style={'width': '10%'}),
                                html.Th("Email", style={'width': '30%'}),
                                html.Th("Message", style={'width': '50%'}),
                            ])
                        ),
                        html.Tbody(id="feedback-table-body")
                    ],
                    style={'marginTop': '10px'}
                )
            ]
        )
    ]
)

# Callback to fetch and store feedback data


@callback(
    [Output('FeedbackData', 'data'),
     Output('DetailedFeedbackData', 'data')],
    [Input('interval-component', 'n_intervals')]
)
def update_feedback_data(n):
    feedback_data = fetch_dynamodb_feedback()

    # Compute overall statistics for chart
    chart_data = aggregate_feedback_stats(feedback_data)

    return chart_data, feedback_data


@callback(
    Output("feedbackChart", "children"),
    Input("FeedbackData", "data"),
)
def update_feedback_chart(feedback_data):
    if not feedback_data:
        return dcc.Graph(
            id='feedback-graph',
            figure={'layout': {'title': 'No Feedback Data Available'}}
        )

    feedback_dict = feedback_data[0]
    return dcc.Graph(
        id='feedback-graph',
        figure={
            'data': [
                {
                    'x': ['Positive Feedback', 'Negative Feedback'],
                    'y': [feedback_dict['positive'], feedback_dict['negative']],
                    'type': 'bar',
                    'name': 'Feedback',
                    'marker': {
                        'color': ['#34A853', '#EA4335'],
                        'line': {
                            'color': '#FFFFFF',
                            'width': 2
                        }
                    }
                },
            ],
            'layout': {
                'title': {
                    'text': 'Customer Feedback Evaluation',
                    'font': {
                        'size': 24,
                        'color': '#FFFFFF'
                    }
                },
                'xaxis': {
                    'title': 'Feedback Type',
                    'tickangle': -45,
                    'title_font': {'size': 18, 'color': '#FFFFFF'},
                    'tickfont': {'size': 14, 'color': '#FFFFFF'},
                    'automargin': True,
                },
                'yaxis': {
                    'title': 'Number of Feedbacks',
                    'title_font': {'size': 18, 'color': '#FFFFFF'},
                    'tickfont': {'size': 14, 'color': '#FFFFFF'},
                    'gridcolor': '#4F4F4F'
                },
                'paper_bgcolor': '#1E1E1E',
                'plot_bgcolor': '#1E1E1E',
                'margin': {'l': 60, 'r': 30, 't': 60, 'b': 75},
                'bargap': 0.15,
            }
        },
        config={
            'displayModeBar': False
        }
    )


@callback(
    Output("feedback-table-body", "children"),
    Input("DetailedFeedbackData", "data"),
)
def update_feedback_table(detailed_feedback_data):
    if not detailed_feedback_data:
        return [html.Tr([html.Td("No feedback data available", colSpan=4)])]

    rows = []
    for feedback in detailed_feedback_data:
        rows.append(html.Tr([
            html.Td(feedback['id']),
            html.Td(
                dmc.Badge(
                    "Positive" if feedback['status'] == 1 else "Negative",
                    color="green" if feedback['status'] == 1 else "red",
                    size="sm"
                )
            ),
            html.Td(feedback['email'], style={
                'maxWidth': '300px', 'whiteSpace': 'normal', 'wordBreak': 'break-word'}),
            html.Td(feedback['message'], style={
                'maxWidth': '500px', 'whiteSpace': 'normal', 'wordBreak': 'break-word'}),
        ]))
    return rows


@callback(
    Output("download-feedback-csv", "data"),
    Input("download-button", "n_clicks"),
    Input("DetailedFeedbackData", "data"),
    prevent_initial_call=True
)
def download_csv(n_clicks, detailed_feedback_data):
    if n_clicks is None or not detailed_feedback_data:
        return None

    df = pd.DataFrame(detailed_feedback_data)
    return dcc.send_data_frame(
        df.to_csv,
        "dynamodb_feedback_data.csv",
        index=False
    )
