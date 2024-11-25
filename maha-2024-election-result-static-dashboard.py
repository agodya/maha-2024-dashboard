import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load the dataset
file_path = "maha_results_2024.csv"
data = pd.read_csv(file_path)

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout for the dashboard
app.layout = html.Div([
    html.H1("Election Results Dashboard", style={'textAlign': 'center'}),

    # Dropdown for selecting visualization
    dcc.Dropdown(
        id="chart_selector",
        options=[
            {"label": "Top 10 Parties by Total Votes", "value": "top_parties"},
            {"label": "Vote Share Distribution", "value": "vote_share_dist"},
            {"label": "Top 10 Constituencies by Total Votes", "value": "top_constituencies"},
            {"label": "EVM Votes vs Postal Votes", "value": "evm_postal"},
            {"label": "Top 10 Parties by Average Vote Share (%)", "value": "avg_vote_share"},
            {"label": "Top 10 Constituencies by Number of Candidates", "value": "candidates_per_constituency"},
            {"label": "Total Votes Distribution by Party", "value": "votes_dist_by_party"},
            {"label": "Constituencies with Lowest Minimum Vote Share (%)", "value": "lowest_vote_shares"}
        ],
        value="top_parties",
        style={'width': '50%', 'margin': 'auto'}
    ),

    # Graph placeholder
    dcc.Graph(id="chart")
])


# Callback for updating the chart
@app.callback(
    Output("chart", "figure"),
    [Input("chart_selector", "value")]
)
def update_chart(chart_type):
    if chart_type == "top_parties":
        df = data.groupby("Party")["Total Votes"].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(df, x="Party", y="Total Votes", title="Top 10 Parties by Total Votes")
    elif chart_type == "vote_share_dist":
        fig = px.histogram(data, x="Vote Share (%)", nbins=30, title="Vote Share Distribution")
    elif chart_type == "top_constituencies":
        df = data.groupby("AC Name")["Total Votes"].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(df, x="Total Votes", y="AC Name", orientation='h', title="Top 10 Constituencies by Total Votes")
    elif chart_type == "evm_postal":
        evm_vs_postal = data[['EVM Votes', 'Postal Votes']].sum().reset_index()
        evm_vs_postal.columns = ['Vote Type', 'Votes']
        fig = px.pie(evm_vs_postal, values='Votes', names='Vote Type', title="EVM Votes vs Postal Votes")
    elif chart_type == "avg_vote_share":
        df = data.groupby("Party")["Vote Share (%)"].mean().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(df, x="Party", y="Vote Share (%)", title="Top 10 Parties by Average Vote Share (%)")
    elif chart_type == "candidates_per_constituency":
        df = data.groupby("AC Name")["Candidate"].count().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(df, x="Candidate", y="AC Name", orientation='h',
                     title="Top 10 Constituencies by Number of Candidates")
    elif chart_type == "votes_dist_by_party":
        fig = px.box(data, x="Party", y="Total Votes", title="Total Votes Distribution by Party", notched=True)
    elif chart_type == "lowest_vote_shares":
        df = data.groupby("AC Name")["Vote Share (%)"].min().sort_values().head(10).reset_index()
        fig = px.bar(df, x="Vote Share (%)", y="AC Name", orientation='h',
                     title="Constituencies with Lowest Minimum Vote Share (%)")
    else:
        fig = px.scatter(title="Select a chart type to visualize.")

    return fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)