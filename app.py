import flask
from flask import request, jsonify
import re
import json
import socket
from dash import Dash, dcc, html, Input, Output, State

def get_data(key, value, current):
    results = []
    pattern_dict = {
        'C': '(C)',
        'C++': '(C\+\+)',
        'Java': '(Java)',
        'C#': '(C\#)',
        'Python': '(Python)',
        'Scala': '(Scala)',
        'Oracle': '(Oracle)',
        'SQL Server': '(SQL Server)',
        'MySQL Server': '(MySQL Server)',
        'PostgreSQL': '(PostgreSQL)',
        'MongoDB': '(MongoDB)',
        'JavaScript': '(JavaScript)',
        'Los Angeles': '(Los Angeles)',
        'New York': '(New York)',
        'San Francisco': '(San Francisco)',
        'Washington DC': '(Washington DC)',
        'Seattle': '(Seattle)',
        'Austin': '(Austin)',
        'Detroit': '(Detroit)',
    }
    for rec in current:
        if re.search(pattern_dict.get(value, value), rec.get(key, '')) is not None:
            results.append(rec)
    return results

app = flask.Flask(__name__)
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')
dash_app.server = app

# Load JSON data
with open('jobs.json', encoding='utf-8') as f:
    data = json.load(f)

dash_app.layout = html.Div(style={'backgroundColor': '#0F8691', 'color': '#FCF0FB', 'padding': '20px'}, children=[
    html.H1("Job Search Terminal",
            style={'textAlign': 'center', 'padding': '10px 0', 'border': '4px solid #9126B6', 'text-align': 'center',
                   'width': '45%', 'color': '#FCF0FB', 'font-size': '24px', 'font-family': 'Verdana',
                   'margin': 'auto'}),
    dcc.Textarea(
        id='command-input',
        style={'width': '100%', 'font-size': '18px', 'height': '200px', 'margin-top': '20px'},
        # Increased font size to 16px
        placeholder="Enter your command here..."
    ),

    html.Button('Execute', id='execute-button', n_clicks=0, style={'margin-top': '10px', 'background-color': '#087BB0', 'border': 'solid', 'font-size': '12px', 'border-color': 'white', 'color': 'white'}),
    html.Div(id='output', style={'margin-top': '20px', 'font-size': '20px'}),

])


@dash_app.callback(
    Output('output', 'children'),
    [Input('execute-button', 'n_clicks')],
    [State('command-input', 'value')]
)
def execute_command(n_clicks, command):
    if n_clicks > 0:
        try:
            lines = command.split('\n')
            topics = []
            values = []
            return_line = ''

            for line in lines:
                if 'topic' in line:
                    topics.append(line.split('=')[1].strip())
                elif 'value' in line:
                    values.append(line.split('=')[1].strip())
                elif 'return' in line:
                    return_line = line.split('=')[1].strip()

            # Debug prints
            print("Topics:", topics)
            print("Values:", values)

            # Process data for multiple criteria
            result_set = data
            for topic, value in zip(topics, values):
                print("Filtering with:", topic, value)  # Debug print
                result_set = get_data(topic, value, result_set)
                print("Intermediate Results Count:", len(result_set))  # Debug print

            if 'count list descending' in return_line:
                if ',' in values[0]:  # Handling multiple values for location count
                    values = [v.strip() for v in values[0].split(',')]
                results = {v: len(get_data(topics[0], v, data)) for v in values}
                sorted_results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
                return html.Pre(f"Count of job postings in locations: {json.dumps(sorted_results, indent=2)}")
            elif 'count' in return_line:
                return html.Pre(f"Count of job postings for {', '.join(values)}: {len(result_set)}")
            else:
                return "Command not recognized"
        except Exception as e:
            return f"Error: {str(e)}"
    return ""


@app.route('/')
def home():
    return '''
        <h1>Welcome to Flask JOB Search API</h1>
        <p><a href="/dash/">Go to Dash App</a></p>
    '''

if __name__ == '__main__':
    app.run(debug=True, port=5002)
