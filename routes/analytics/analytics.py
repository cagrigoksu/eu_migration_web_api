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
    
     # Immigration Proportion by Country (pie chart)
    df_immigration = df.groupby('Country')['Im_Value'].sum().reset_index()
    fig_pie = px.pie(
        df_immigration,
        names='Country',
        values='Im_Value',
        title='Proportion of Immigration by Country'
    )
    pie_chart = fig_pie.to_html(full_html=False)

    # Stacked Bar Chart for Immigration & Emigration Trends 
    fig_stacked = go.Figure()
    fig_stacked.add_trace(go.Bar(x=df['Year'], y=df['Im_Value'], name='Immigration'))
    fig_stacked.add_trace(go.Bar(x=df['Year'], y=df['Em_Value'], name='Emigration'))
    fig_stacked.update_layout(barmode='stack', title='Stacked Immigration & Emigration Trends')
    stacked_chart = fig_stacked.to_html(full_html=False)

    # Bubble Chart for Net Migration
    df['Total_Migration'] = df['Im_Value'] + df['Em_Value']
    fig_bubble = px.scatter(
        df,
        x='Year',
        y='Net_Migration',
        size='Total_Migration',
        color='Country',
        title='Net Migration with Bubble Size Based on Total Migration',
        size_max=60
    )
    bubble_chart = fig_bubble.to_html(full_html=False)

    html_template = """
    <html>
    <head>
        <title>EU Migration Dashboard</title>
        <style>
            .chart-container {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                margin-top: 1%;
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
        <div>
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
            
            <div class="chart-container">
            
                <div class="chart-box">
                    <h2>Immigration Proportion by Country</h2>
                    <div>{{ pie_chart|safe }}</div>
                </div>

                <div class="chart-box">
                    <h2>Stacked Bar Chart for Immigration & Emigration Trends</h2>
                    <div>{{ stacked_chart|safe }}</div>
                </div>
            </div>
            
            <div class="chart-container">
            
                <div class="chart-box">
                    <h2>Net Migration with Bubble Size Based on Total Migration</h2>
                    <div>{{ bubble_chart|safe }}</div>
                </div>
                
            </div>
            
        </div>

    </body>
    </html>
    """

    return render_template_string(
        html_template,
        line_chart=line_chart,
        bar_chart=bar_chart,
        pie_chart=pie_chart,
        stacked_chart=stacked_chart,
        bubble_chart=bubble_chart
    )
    
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