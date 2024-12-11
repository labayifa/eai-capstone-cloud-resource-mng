from dash import register_page
import dash_mantine_components as dmc
from dash import dcc

register_page(__name__, path="/")

__app__ = 'app.py'
__home__ = 'pages/home/home.py'
__analytics__ = 'pages/analytics/analytics.py'
__secret__ = 'pages/secret.py'

with open(__app__, 'r') as file:
    __app__ = file.read()

with open(__home__, 'r') as file:
    __home__ = file.read()

with open(__analytics__, 'r') as file:
    __analytics__ = file.read()

with open(__secret__, 'r') as file:
    __secret__ = file.read()

layout = dmc.Box(
    m=30,
    children=[
        # Main title for services
        dmc.Title(
            "Our Services",
            order=1,
            ta="center",
            mb=30
        ),

        # Grid container for the two cards
        dmc.Grid(
            children=[
                # second card
                dmc.GridCol(
                    span=6,
                    children=[
                        dmc.Card(
                            children=[
                                dmc.CardSection(
                                    dmc.Image(
                                        src="/assets/cloud_pros.png",
                                        h=160,
                                        alt="Effortless Cloud Deployment"
                                    )
                                ),
                                dmc.Group(
                                    align="apart",
                                    mt="md",
                                    mb="xs",
                                    children=[
                                        dmc.Text(
                                            "Cost Effective Cloud Deployment", fw=500, size="lg")
                                    ]
                                ),
                                dmc.Text(
                                    """Our ChatOps service is designed with the startup developer in mind, offering a streamlined 
                                    and budget-friendly approach to deploying cloud storage services. Leveraging the power of 
                                    Language Model (LLM) technology, our chatbot provides tailored recommendations for AWS cloud 
                                    storage solutions that align with your project's financial constraints. By inputting your
                                    project details and budget, you'll receive a comprehensive cost comparison of various AWS 
                                    storage options.""",
                                    size="sm",
                                    c="dimmed"
                                ),
                                dmc.Anchor(
                                    href="#",  # Replace with your target URL
                                    target="_blank",  # Opens the link in a new tab
                                    children=dmc.Button(
                                        "Learn More",
                                        variant="light",
                                        color="blue",
                                        fullWidth=True,
                                        mt="md",
                                        radius="md"
                                    ),
                                    # Prevents the underline on the link
                                    style={"textDecoration": "none"}
                                )

                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"height": "100%"}
                        ),
                    ]
                ),
                # First card
                dmc.GridCol(
                    span=6,
                    children=[
                        dmc.Card(
                            children=[
                                dmc.CardSection(
                                    dmc.Image(
                                        src="/assets/aws_s3.png",
                                        h=160,
                                        alt="S3 Deployment"
                                    )
                                ),
                                dmc.Group(
                                    align="apart",
                                    mt="md",
                                    mb="xs",
                                    children=[
                                        dmc.Text("AWS S3 Deployment",
                                                 fw=500, size="lg")
                                    ]
                                ),
                                dmc.Text(
                                    """- Quick and easy deployment: Deploy your S3 projects in minutes, not hours.
                                    - No technical expertise required: Our app is designed for developers of all skill levels.
                                    - Seamless integration: Our app integrates seamlessly with your existing development workflow.
                                    - Cost-effective: Save time and money by automating your S3 deployment process.Whether you're a solo developer or
                                    part of a startup team, our ChatOps app is the perfect solution for simplifying your AWS S3 deployment. Try it out today
                                     and take the hassle out of deployment!""",
                                    size="sm",
                                    c="dimmed"
                                ),
                                dmc.Anchor(
                                    href="https://docs.aws.amazon.com/s3/",  # Replace with your target URL
                                    target="_blank",  # Opens the link in a new tab
                                    children=dmc.Button(
                                        "Learn More",
                                        variant="light",
                                        color="blue",
                                        fullWidth=True,
                                        mt="md",
                                        radius="md"
                                    ),
                                    # Prevents the underline on the link
                                    style={"textDecoration": "none"}
                                )
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"height": "100%"}
                        ),
                    ]
                ),
                # third card
                dmc.GridCol(
                    span=6,
                    children=[
                        dmc.Card(
                            children=[
                                dmc.CardSection(
                                    dmc.Image(
                                        src="/assets/dynamo.png",
                                        h=160,
                                        alt="DynamodB Deployment"
                                    )
                                ),
                                dmc.Group(
                                    align="apart",
                                    mt="md",
                                    mb="xs",
                                    children=[
                                        dmc.Text("DynamoDB Deployment",
                                                 fw=500, size="lg")
                                    ]
                                ),
                                dmc.Text(
                                    """- Speedy and straightforward deployment: Get your DynamoDB projects up and running swiftly.
                                        - No need for deep technical knowledge: Our app is user-friendly, catering to developers across various expertise levels.
                                        - Smooth integration: Our app seamlessly fits into your existing development workflow, making it a natural extension of your toolkit.
                                        - Cost efficiency: Automate your DynamoDB deployment process to save both time and resources.Our ChatOps app is the ideal solution for 
                                        individual developers and startup teams aiming to simplify their DynamoDB deployment. Give it a try today and experience a stress-free deployment process!""",
                                    size="sm",
                                    c="dimmed"
                                ),
                                dmc.Anchor(
                                    href="https://docs.aws.amazon.com/dynamodb/",  # Replace with your target URL
                                    target="_blank",  # Opens the link in a new tab
                                    children=dmc.Button(
                                        "Learn More",
                                        variant="light",
                                        color="blue",
                                        fullWidth=True,
                                        mt="md",
                                        radius="md"
                                    ),
                                    # Prevents the underline on the link
                                    style={"textDecoration": "none"}
                                )
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"height": "100%"}
                        ),
                    ]
                ),
                # fourth card
                dmc.GridCol(
                    span=6,
                    children=[
                        dmc.Card(
                            children=[
                                dmc.CardSection(
                                    dmc.Image(
                                        src="/assets/easy_deployment.png",
                                        h=160,
                                        alt="Easy Deployment"
                                    )
                                ),
                                dmc.Group(
                                    align="apart",
                                    mt="md",
                                    mb="xs",
                                    children=[
                                        dmc.Text(
                                            "Easy Resource Deployment", fw=500, size="lg")
                                    ]
                                ),
                                dmc.Text(
                                    """Ease of deployment is at the core of our ChatOps service. We understand that navigating the 
                                    complexities of cloud services can be daunting, especially for startup developers with limited 
                                    time and resources. Our LLM-powered chatbot simplifies this process by understanding your project
                                    needs through natural language conversation. It meticulously analyzes your project description 
                                    and utilizes RAG (Retrieval-Augmented Generation) implementation to sift through extensive cloud 
                                    service documentations. As a result, you receive personalized, easy-to-understand guidance and 
                                    actionable steps to deploy the recommended AWS cloud storage services effortlessly.""",
                                    size="sm",
                                    c="dimmed"
                                ),
                                dmc.Anchor(
                                    href="#",  # Replace with your target URL
                                    target="_blank",  # Opens the link in a new tab
                                    children=dmc.Button(
                                        "Learn More",
                                        variant="light",
                                        color="blue",
                                        fullWidth=True,
                                        mt="md",
                                        radius="md"
                                    ),
                                    # Prevents the underline on the link
                                    style={"textDecoration": "none"}
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            style={"height": "100%"}
                        ),
                    ]
                ),
            ],
            gutter="xl",
        ),
    ]
)
