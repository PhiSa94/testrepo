# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import logging

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Read the SpaceX data into pandas dataframe
try:
    spacex_df = pd.read_csv("spacex_launch_dash.csv")
    logging.info("CSV file loaded successfully.")
except Exception as e:
    logging.error(f"Error loading CSV: {e}")
    raise

# Handle missing values if needed (for example, if there are any rows with NaN in important columns)
spacex_df.dropna(subset=['Payload Mass (kg)', 'Launch Site', 'class'], inplace=True)
logging.info(f"Data cleaned, remaining rows: {len(spacex_df)}")

# Find min and max payload for the slider
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
logging.info(f"Payload range: {min_payload} to {max_payload}")

# Create a Dash application
app = dash.Dash(__name__)

# Get unique launch sites
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown component for selecting Launch Site
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',  # Default value is 'ALL'
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    
    html.Br(),

    # Pie chart for success/failure launch outcomes
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Payload range slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]  # Default range based on the data
    ),

    html.Br(),

    # Scatter plot for payload vs. success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# TASK 2: Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    logging.debug(f"Generating pie chart for site: {entered_site}")
    if entered_site == 'ALL':
        # Do not filter for success only; show both successes and failures
        fig = px.pie(spacex_df,
                     names='class',
                     title='Total Launch Outcomes for All Sites',
                     color='class',
                     color_discrete_map={0: 'red', 1: 'green'},
                     labels={0: 'Failure', 1: 'Success'})
        return fig
    else:
        # Filter for a specific site
        df_site = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(df_site,
                     names='class',
                     title=f'Total Launch Outcomes for {entered_site}',
                     color='class',
                     color_discrete_map={0: 'red', 1: 'green'},
                     labels={0: 'Failure', 1: 'Success'})
        return fig

# TASK 4: Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_chart(selected_site, payload_range):
    logging.debug(f"Generating scatter chart for site: {selected_site} with payload range {payload_range}")
    
    low, high = payload_range
    # Filter data based on payload range first
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if selected_site == 'ALL':
        # Scatter plot for all sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation Between Payload and Success for All Sites'
        )
    else:
        # Scatter plot for a specific site
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation Between Payload and Success for {selected_site}'
        )
    
    return fig

# Run the app
if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        logging.error(f"Error running app: {e}")
        raise