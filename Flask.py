from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
#from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from functools import wraps
import plotly
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import json
import base64
import datetime
import io
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import flask
import pandas



#Kullanıcı Login Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
       if "logged_in" in session:
           return f(*args, **kwargs)
       else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın.","danger")
            return redirect(url_for("login"))
    return decorated_function


class loginform(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")




#Flask Server Coonnection
server = Flask(__name__)
server.secret_key="ybblog"


#İndex Html process
@server.route('/')
def index():
    return render_template('index.html')



#login process
@server.route("/login",methods = ["GET","POST"])
def login():
    form=loginform(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data
        
        if username == "kadir":
            if password_entered == "1234":
                flash("Başarıyla Giriş Yaptınız...","success")
                
                session["logged_in"]=True
                session["username"]=username

                return redirect(url_for("index"))
            else:
                flash("Parolanızı Yanlış Girdiniz...","danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle bir kullanıcı bulunmuyor...","danger")
            return redirect(url_for("login"))




    return render_template("login.html",form = form)





# Logout Process
@server.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


#DashBoards Process
@server.route('/DashBoards')
def Dashboards():
    feature = 'Bar'
    bar = create_plot(feature)
    return render_template('Dashboards.html', plot=bar)

def create_plot(feature):
    if feature == 'Scatter':
        N = 40
        x = np.linspace(0, 1, N)
        y = np.random.randn(N)
        df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe
        data = [
            go.Bar(
                x=df['x'], # assign x as the dataframe column 'x'
                y=df['y']
            )
        ]
    else:
        N = 1000
        random_x = np.random.randn(N)
        random_y = np.random.randn(N)

        # Create a trace
        data = [go.Scatter(
            x = random_x,
            y = random_y,
            mode = 'markers'
        )]


    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON












"""DASH PAGE PART"""

#Flask server connection to dash server
app = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/Upload/',
)


#For multi callback
app.config.suppress_callback_exceptions = True

df=''

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content'),
    html.Div(id='datatable-interactivity-container')
])





#Dash İndex page
index_page = html.Div([
    dcc.Upload(
        id='upload-data',
    children=html.Div([
            'Drag and Drop or ',
         html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Br(),
   html.A([html.Button(["Goto Home Page"],style={"width" : "5%","height":"20%",'margin': '10px'})], href='/'),
    html.Div(id='page-1-content')   
])



#Return Documents and Graph Function
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
         
        ])
    sayfa= html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        dash_table.DataTable(
            id='datatable-interactivity',
            columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
        ),

        html.Hr(),  # horizontal line
        html.Div(id='datatable-interactivity-container'),
        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        }),
        html.Br(),
        html.Div([
        html.Div([
            dcc.Graph(
                figure={
                    "data": [
                        {
                            "x": df[df.columns[1]],
                            "y": df[df.columns[2]],
                            "type": "bar",
                            "marker": {"color": "#0074D9"},
                        }
                    ],
                    "layout": {
                        "xaxis":{"automargin": True},
                        "yaxis": {"automargin": True},
                        "height": 250,
                        "margin": {"t": 10, "l": 10, "r": 10},
                    },
                },
            )
        ],className="six columns",style={"width" : "50%",'display': 'inline-block'}),
        html.Div([
            dcc.Graph(
                figure={
                    "data": [
                        {
                            "x": df[df.columns[0]],
                            "y": df[df.columns[2]],
                            "type": "bar",
                            "marker": {"color": "#0074D9"},
                        }
                    ],
                    "layout": {
                        "xaxis":{"automargin": True},
                        "yaxis": {"automargin": True},
                        "height": 250,
                        "margin": {"t": 10, "l": 10, "r": 10},
                    },
                },
            )
        ],className="six columns",style={ "width" : "50%",'display': 'inline-block'})
        
        ],className="row"),

    ])
    return sayfa






app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})




#Selected Colum Callback
@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    [Input('datatable-interactivity', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]





#selected Rows
@app.callback(
    Output('datatable-interactivity-container', "children"),
    [Input('datatable-interactivity', "derived_virtual_data"),
     Input('datatable-interactivity', "derived_virtual_selected_rows")])
def update_graphs(rows, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        dcc.Graph(
            figure={
                "data": [
                    {
                       "x": dff[dff.columns[2]],
                        "y": dff[dff.columns[1]],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        
    ]









































@app.callback(Output('page-1-content', 'children'),
            [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output1(list_of_contents, list_of_names, list_of_dates):
        if list_of_contents is not None:
            children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)
            ]
        return children




# Update the Url
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return server[render_template("index.html")]
    else:
        return index_page

    # You could also return a 404 "URL not found" page here

if __name__ == '__main__':
    server.run(debug=True)  