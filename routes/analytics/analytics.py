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
    'tags': ['Data Visualization - Protected Endpoint']
})

def create_dash_app(flask_app):
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        routes_pathname_prefix="/analytics/dashboard/",
        suppress_callback_exceptions=True
    )

    dash_app.layout = html.Div([
        html.H1("EU Migration Data Dashboard", style={'textAlign': 'center'}),

        html.Div([
            html.Label("Select Country:"),
            dcc.Dropdown(
                id="country-dropdown",
                options=[{"label": c, "value": c} for c in df_eu["Country"].unique()],
                value=None,
                placeholder="All Countries"
            ),
            html.Label("Select Start Year:"),
            dcc.Input(id="start-year", type="number", placeholder="Start Year"),
            html.Label("Select End Year:"),
            dcc.Input(id="end-year", type="number", placeholder="End Year")
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        # Line chart
        html.Div([
            html.H2("Net Migration Trends"),
            dcc.Graph(id="line-chart")
        ], className="chart-box"),

        # Bar chart
        html.Div([
            html.H2("Immigration vs Emigration"),
            dcc.Graph(id="bar-chart")
        ], className="chart-box"),

        # Pie chart
        html.Div([
            html.Label("Select Year:"),
            dcc.Input(id="pie-year", type="number", placeholder="Year"),
            html.H2("Immigration Proportion by Country"),
            dcc.Graph(id="pie-chart")
        ], className="chart-box"),

        # Stacked bar chart
        html.Div([
            html.H2("Stacked Immigration & Emigration Trends"),
            dcc.Graph(id="stacked-chart")
        ], className="chart-box"),

        # Bubble chart
        html.Div([
            html.H2("Net Migration with Bubble Size Based on Total Migration"),
            dcc.Graph(id="bubble-chart")
        ], className="chart-box")
    ])

   
    @dash_app.callback(
        Output("line-chart", "figure"),
        Output("bar-chart", "figure"),
        Output("pie-chart", "figure"),
        Output("stacked-chart", "figure"),
        Output("bubble-chart", "figure"),
        Input("country-dropdown", "value"),
        Input("start-year", "value"),
        Input("end-year", "value"),
        Input("pie-year", "value")
    )
    def update_charts(selected_country, start_year, end_year, pie_year):
        df = df_eu.copy()

        # Apply filters
        if selected_country:
            df = df[df["Country"] == selected_country]
        if start_year and end_year:
            df = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]
        if pie_year:
            df = df[df["Year"] == pie_year]

        # Line Chart
        fig_line = px.line(df, x="Year", y="Net_Migration", color="Country", title="Net Migration Trends by Country")

        # Bar Chart
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=df["Year"], y=df["Im_Value"], name="Immigration"))
        fig_bar.add_trace(go.Bar(x=df["Year"], y=df["Em_Value"], name="Emigration"))
        fig_bar.update_layout(barmode="group", title="Immigration vs Emigration")

        # Pie Chart
        df_immigration = df.groupby("Country")["Im_Value"].sum().reset_index()
        fig_pie = px.pie(df_immigration, names="Country", values="Im_Value", title="Proportion of Immigration by Country")

        # Stacked Bar Chart
        fig_stacked = go.Figure()
        fig_stacked.add_trace(go.Bar(x=df["Year"], y=df["Im_Value"], name="Immigration"))
        fig_stacked.add_trace(go.Bar(x=df["Year"], y=df["Em_Value"], name="Emigration"))
        fig_stacked.update_layout(barmode="stack", title="Stacked Immigration & Emigration Trends")

        # Bubble Chart
        df["Total_Migration"] = df["Im_Value"] + df["Em_Value"]
        fig_bubble = px.scatter(df, x="Year", y="Net_Migration", size="Total_Migration", color="Country",
                                title="Net Migration with Bubble Size Based on Total Migration", size_max=60)

        return fig_line, fig_bar, fig_pie, fig_stacked, fig_bubble

    return dash_app
    
@analytics_bp.route("/map", methods=["GET"], endpoint="map")
@swag_from({
    'tags': ['Data Visualization - Protected Endpoint']
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