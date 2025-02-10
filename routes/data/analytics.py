from flask import Flask, Blueprint, request, jsonify, render_template_string
from flasgger import swag_from
from routes.auth.user_auth import is_valid_api_key, handle_expired_api_key, require_api_key
from ds import ds_ops
import plotly.express as px
import plotly.graph_objs as go


analytics_bp = Blueprint("analytics", __name__)

# get dataframe
ds_ops.check_file_exist() or ds_ops.prepare_migrations_file()
df_eu = ds_ops.get_dataframe()

@analytics_bp.route("/", methods=["GET"], endpoint="dashboard")
@swag_from({
    'tags': ['Data Visualization - Protected Endpoint']
})
def dashboard():

    df = df_eu

     # Net Migration Trends (line chart) 
    fig_line = px.line(
        df,
        x='Year',
        y='Net_Migration',
        color='Country',
        title='Net Migration Trends by Country'
    )
    line_chart = fig_line.to_html(full_html=False)
    
    # Immigration vs Emigration (bar chart) 
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=df['Year'], y=df['Im_Value'], name='Immigration'))
    fig_bar.add_trace(go.Bar(x=df['Year'], y=df['Em_Value'], name='Emigration'))
    fig_bar.update_layout(barmode='group', title='Immigration vs Emigration')
    bar_chart = fig_bar.to_html(full_html=False)

    html_template = """
    <html>
    <head>
        <title>EU Migration Dashboard</title>
        <style>
            .chart-container {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
            }
            .chart-box {
                width: 48%;
                margin: 1%;
                 min-height: 520px;
            }
        </style>
    </head>
    <body>
        <h1 style='text-align:center;'>EU Migration Data Dashboard</h1>

        <div class="chart-container">
        
            <div class="chart-box">
                <h2>Net Migration Trends</h2>
                <div>{{ line_chart|safe }}</div>
            </div>

            <div class="chart-box">
                <h2>Immigration vs Emigration</h2>
                <div>{{ bar_chart|safe }}</div>
            </div>
        </div>

    </body>
    </html>
    """

    return render_template_string(
        html_template,
        line_chart=line_chart,
        bar_chart=bar_chart,
    )