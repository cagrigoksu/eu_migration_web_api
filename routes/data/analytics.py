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
    
    # Handle missing data
    df = df_eu.dropna(subset=['Country', 'Year', 'Im_Value', 'Em_Value', 'Net_Migration'])

     # Net Migration Trends (line chart) 
    fig_line = px.line(
        df,
        x='Year',
        y='Net_Migration',
        color='Country',
        title='Net Migration Trends by Country'
    )
    line_chart = fig_line.to_html(full_html=False)

    html_template = """
    <html>
    <head>
        <title>EU Migration Dashboard</title>
    </head>
    <body>
        <h1 style='text-align:center;'>EU Migration Data Dashboard</h1>

        <!-- Net Migration Trends Chart -->
        <h2>Net Migration Trends</h2>
        <div>{{ line_chart|safe }}</div>

    </body>
    </html>
    """

    return render_template_string(
        html_template,
        line_chart=line_chart
    )