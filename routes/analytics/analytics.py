from flask import Flask, Blueprint, request, jsonify, render_template_string
from flasgger import swag_from
from routes.auth.user_auth import is_valid_api_key, handle_expired_api_key, require_api_key
from ds import ds_ops
import plotly.express as px
import plotly.graph_objs as go
import dash
from dash import dcc, html, Input, Output

analytics_bp = Blueprint("analytics", __name__)

# get dataframe
ds_ops.check_file_exist() or ds_ops.prepare_migrations_file()
df_eu = ds_ops.get_dataframe()

@analytics_bp.route("/", methods=["GET"], endpoint="dashboard")
@swag_from({
    'tags': ['Data Visualization z']
})

def create_dash_app(flask_app):
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        routes_pathname_prefix="/analytics/dashboard/",
        suppress_callback_exceptions=True
    )

    def create_country_filter_controls(prefix):
        return html.Div([
            html.Label("Select Country:"),
            dcc.Dropdown(
                id= prefix+"-country-dropdown",
                options=[{"label": c, "value": c} for c in df_eu["Country"].unique()],
                value=None,
                placeholder="All Countries"
            )
        ])
    
    def create_start_year_filter_controls(prefix):
        return html.Div([
            html.Label("Select Start Year:"),
            dcc.Input(id=prefix+"-start-year", type="number", placeholder="Start Year")
        ])
        
    def create_end_year_filter_controls(prefix):
        return html.Div([
            html.Label("Select End Year:"),
            dcc.Input(id=prefix+"-end-year", type="number", placeholder="End Year")
        ])
        
    dash_app.layout = html.Div([
        html.H1("EU Migration Data Dashboard", style={'textAlign': 'center'}),

        html.Div([
            
            # Line chart
            html.Div([
                html.H2("Net Migration Trends"),
                create_country_filter_controls("line"),
                create_start_year_filter_controls("line"),
                create_end_year_filter_controls("line"),                
                dcc.Graph(id="line-chart")
              ], className="chart-box")            
            ]),
        
            # Bar chart
            html.Div([
                html.H2("Immigration vs Emigration"),
                create_country_filter_controls("bar"),
                create_start_year_filter_controls("bar"),
                create_end_year_filter_controls("bar"),           
                dcc.Graph(id="bar-chart")
            ], className="chart-box"),
            
            # Pie chart
            html.Div([
                html.H2("Immigration Proportion by Country"),
                create_start_year_filter_controls("pie"),
                create_end_year_filter_controls("pie"),   
                dcc.Graph(id="pie-chart")
            ], className="chart-box"),
            
            # Stacked bar chart
            html.Div([
                html.H2("Stacked Immigration & Emigration Trends"),
                create_country_filter_controls("stacked-bar"),
                create_start_year_filter_controls("stacked-bar"),
                create_end_year_filter_controls("stacked-bar"),
                dcc.Graph(id="stacked-bar-chart")
            ], className="chart-box"),
            
            # Bubble chart
            html.Div([
                html.H2("Net Migration with Bubble Size Based on Total Migration"),
                create_country_filter_controls("bubble"),
                create_start_year_filter_controls("bubble"),
                create_end_year_filter_controls("bubble"),
                dcc.Graph(id="bubble-chart")
            ], className="chart-box")
    ])

   
    @dash_app.callback(
        Output("line-chart", "figure"),
        Input("line-country-dropdown", "value"),
        Input("line-start-year", "value"),
        Input("line-end-year", "value"))
    def update_line_charts(selected_country, start_year, end_year):
        df = df_eu.copy()

        # Apply filters
        if selected_country:
            df = df[df["Country"] == selected_country]
        if start_year and end_year:
            df = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        # Line Chart
        fig_line = px.line(df, x="Year", y="Net_Migration", color="Country", title="Net Migration Trends by Country")
        return fig_line
    
    @dash_app.callback(
    Output("bar-chart", "figure"),
    Input("bar-country-dropdown", "value"),
    Input("bar-start-year", "value"),
    Input("bar-end-year", "value"))
    def update_bar_charts(selected_country, start_year, end_year):
        df = df_eu.copy()
        
        if selected_country:
            df = df[df["Country"] == selected_country]
        if start_year and end_year:
            df = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=df["Year"], y=df["Im_Value"], name="Immigration"))
        fig_bar.add_trace(go.Bar(x=df["Year"], y=df["Em_Value"], name="Emigration"))
        fig_bar.update_layout(barmode="group", title="Immigration vs Emigration")
        
        return fig_bar
    
    @dash_app.callback(
    Output("pie-chart", "figure"),
    Input("pie-start-year", "value"),
    Input("pie-end-year", "value"))
    def update_pie_charts(start_year, end_year):
        df = df_eu.copy()
        
        if start_year and end_year:
            df = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        df_immigration = df.groupby("Country")["Im_Value"].sum().reset_index()
        fig_pie = px.pie(df_immigration, names="Country", values="Im_Value", title="Proportion of Immigration by Country")
        
        return fig_pie
    
    @dash_app.callback(
    Output("stacked-bar-chart", "figure"),
    Input("stacked-bar-country-dropdown", "value"),
    Input("stacked-bar-start-year", "value"),
    Input("stacked-bar-end-year", "value"))
    def update_stacked_bar_charts(selected_country, start_year, end_year):
        df = df_eu.copy()
        
        if selected_country:
            df = df[df["Country"] == selected_country]
        
        if start_year and end_year:
            df = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        fig_stacked = go.Figure()
        fig_stacked.add_trace(go.Bar(x=df["Year"], y=df["Im_Value"], name="Immigration"))
        fig_stacked.add_trace(go.Bar(x=df["Year"], y=df["Em_Value"], name="Emigration"))
        fig_stacked.update_layout(barmode="stack", title="Stacked Immigration & Emigration Trends")
        
        return fig_stacked
    
    @dash_app.callback(
    Output("bubble-chart", "figure"),
    Input("bubble-country-dropdown", "value"),
    Input("bubble-start-year", "value"),
    Input("bubble-end-year", "value"))
    def update_bubble_charts(selected_country, start_year, end_year):
        df = df_eu.copy()
        
        if selected_country:
            df = df[df["Country"] == selected_country]
        
        if start_year and end_year:
            df = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

        df["Total_Migration"] = df["Im_Value"] + df["Em_Value"]
        fig_bubble = px.scatter(df, x="Year", y="Net_Migration", size="Total_Migration", color="Country",
                                title="Net Migration with Bubble Size Based on Total Migration", size_max=60)
        
        return fig_bubble
    
    return dash_app

    
@analytics_bp.route("/map", methods=["GET"], endpoint="map")
@swag_from({
    'tags': ['Data Visualization']
})
def map():

    df = df_eu

    fig_map = px.choropleth(
        df,
        locations='Country',
        locationmode='ISO-3',
        color='Net_Migration',
        hover_name='Country',
        animation_frame='Year',
        title='Choropleth Map of Net Migration by Country'
    )
    map_chart = fig_map.to_html(full_html=False)

    html_template = """
<html>
    <head>
        <title>EU Migration Dashboard</title>
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                width: 100%;
            }
            .chart-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                width: 100%;
            }
            .map-box {
                height: 100%;
                width: 100%;
            }
        </style>
    </head>
    <body>
        <div class="chart-container">
            <div class="map-box">{{ map_chart|safe }}</div>
        </div>
    </body>
</html>
    """

    return render_template_string(
        html_template,
        map_chart = map_chart
    )