import dash_mantine_components as dmc
from utils.helpers import iconify

sidebar = dmc.Box(
    children=[
        dmc.NavLink(
            label="Home",
            leftSection=iconify(icon="solar:home-2-line-duotone", width=50),  # Increase icon size
            href='/',
            fz="28px",  # Set font size using 'fz' prop
            style={"padding": "15px 25px"}  # Increase padding for spacing
        ),
        dmc.NavLink(
            label="Feedback and Monitoring",
            leftSection=iconify(icon="hugeicons:analytics-02", width=50),
            href='/analytics',
            fz="28px",
            style={"padding": "15px 25px"}
        ),
        # dmc.NavLink(
        #     label="Secret",
        #     leftSection=iconify(icon="solar:lock-keyhole-minimalistic-unlocked-line-duotone", width=24),
        #     href='/secret',
        #     fz="18px",
        #     style={"padding": "10px 20px"}
        # ),
    ]
)
