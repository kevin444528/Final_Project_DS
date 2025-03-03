# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)
launch_sites = spacex_df['Launch Site'].unique()

options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                id='site-dropdown',
                                options=options,  # Set options to the generated list of launch sites
                                value='ALL',  # Default value is 'ALL' meaning all sites are selected
                                placeholder="Select a Launch Site here",  # Placeholder text for the dropdown
                                searchable=True  # Enable searching within the dropdown
                            ),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                    dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,  # Minimum value (0 Kg)
                                    max=10000,  # Maximum value (10,000 Kg)
                                    step=1000,  # Step interval (1000 Kg)
                                    marks={i: str(i) for i in range(0, 10001, 1000)},  # Marks at intervals of 1000 Kg
                                    value=[min_payload, max_payload]  # Default value is from the min_payload to max_payload
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Callback function for the pie chart based on the selected launch site
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    # Filter the dataframe based on the selected launch site
    filtered_df = spacex_df

    # If the selected site is 'ALL', use the whole dataset
    if entered_site == 'ALL':
        success_count = filtered_df['class'].value_counts().to_dict()
        fig = px.pie(
            names=['Failure', 'Success'],
            values=[success_count.get(0, 0), success_count.get(1, 0)],
            title="Overall Success vs Failure Launches"
        )
    else:
        # If a specific site is selected, filter the dataframe
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_count = filtered_df['class'].value_counts().to_dict()
        fig = px.pie(
            names=['Failure', 'Success'],
            values=[success_count.get(0, 0), success_count.get(1, 0)],
            title=f"Launch Success vs Failure for {entered_site}"
        )
    
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, selected_payload_range):
    # Unpack the payload range
    min_payload, max_payload = selected_payload_range
    
    # Filter the dataframe based on the payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) &
                            (spacex_df['Payload Mass (kg)'] <= max_payload)]
    
    # If a specific launch site is selected, further filter by launch site
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['LaunchSite'] == selected_site]
    
    # Create the scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',  # Color by booster version category
        title=f"Payload vs Success for {selected_site if selected_site != 'ALL' else 'All Sites'}",
        labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Success (1) / Failure (0)'},
        hover_data=['Booster Version Category']  # Include booster version in hover data
    )
    
    # Return the figure to be rendered
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
