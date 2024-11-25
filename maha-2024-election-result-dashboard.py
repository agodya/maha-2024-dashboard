from idlelib.autocomplete import TRY_A

from click import prompt
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from dash import Dash, html, dcc, callback, Output, Input, State
import dash_ag_grid as dag
import pandas as pd
import re

from dotenv import find_dotenv, load_dotenv
import os

from sqlalchemy import True_

# load the api key
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
GROQ_API_KEY = os.getenv("GROQ_API_KEY") # Create a .env file and add the API key there

#load the dataset, grab the first 5 rows, and convert to string so that the LLM can read the data
df = pd.read_csv('maha_results_2024.csv')
df_5_rows = df.head(20)
csv_string = df_5_rows.to_string(index=False)

#choose the model
model = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama3-70b-8192"
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You're a data visualization expert and use your favorite graphing library Plotly only. Suppose, that "
            "the data is provided as a maha_results_2024.csv file. Here are the first 5 rows of the data set: {data} "
            "Follow the user's indications when creating the graph"
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

chain = prompt | model

#extract the Plotly fig object from the code generated in the callback
def get_fig_from_code(code):
    local_variables = {}
    exec(code, {}, local_variables)
    return local_variables['fig']

app = Dash()
app.layout = [
    html.H1("Maharashtra Assembly Election Results 2024"),
    dag.AgGrid(
        rowData=df.to_dict("records"),
        columnDefs=[{"field": i} for i in df.columns ],
        defaultColDef={"filter": True, "sortable": True, "floatingFilter": True}
    ),
    dcc.Textarea(id='user-request', style={'width': '50%', 'height': 50, 'margin-top': 20}),
    html.Br(),
    html.Button('Submit', id='my-button'),
    dcc.Loading(
        [
            html.Div(id='my-figure', children=''),
            dcc.Markdown(id='content', children='')
        ],
        type='cube'
    )
]

@callback(
    Output('my-figure', 'children'),
    Output('content', 'children'),
    Input('my-button', 'n_clicks'),
    State('user-request', 'value'),
    prevent_initial_call=True
)
def create_graph(_, user_input):
    response = chain.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "data": csv_string
        },
    )
    result_output = response.content
    print(result_output)

    # Check if the answer includes code. This regular expression will match code blocks
    # with or without the language specifier (like 'python')
    code_block_match = re.search(r'```(?:[Pp]ython)?(.*?)```', result_output, re.DOTALL)
    print(code_block_match)
    # if code is included, extract the figure created
    if code_block_match:
        code_block = code_block_match.group(1).strip()
        cleaned_code = re.sub(r'(?m)^\s*fig\.show\(\)\s*$', '', code_block)
        fig = get_fig_from_code(cleaned_code)
        return dcc.Graph(figure=fig), result_output
    else:
        return "", result_output

if __name__ == "__main__":
    app.run_server(debug=False, port=8807)






print(df_5_rows)