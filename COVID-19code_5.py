import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from state_data import state_data
from india_data import india_data
from world_data import world_data


#State data object
s=state_data()

#India data object
i=india_data()

#World data object
w=world_data()

#India total Cases

india_fig_total = i.india_graph("Total")

#India Daily Cases 
india_fig_daily = i.india_graph("Daily")

#India Stats 
india_stats=i.stats_graph()

#State wise daily data for confirmed cases
state_fig_con = s.states_line_graph("Total_Confirmed")

#State wise total data for Recovered cases
state_fig_rec = s.states_line_graph("Total_Recovered")

#State wise total data for Death cases
state_fig_dec = s.states_line_graph("Total_Deaths")

#Single State data

state_fig_total = s.state_graph()

#States table
state_stats = s.state_stats()


#Top 15 states
top_15_states=s.top_15_states()


#state piew chart
state_fig_pie = s.state_piechart()

#District Total Cases can be seprated for Confirmed, Recovered and Deceased for individual graph
district_fig = s.district_graph()

# Creating the visualization
world_fig_dy_confirm=w.world_choropleth("Confirmed")

# Creating the visualization
world_fig_dy_active=w.world_choropleth("Active")

# Creating the visualization
world_fig_dy_deaths=w.world_choropleth("Deaths")

# Creating the visualization
world_fig_dy_Recovered=w.world_choropleth("Recovered")

#World table
world_stats = w.world_stats()


#########Main##########################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title="Vinsys COVID 19"
app.layout = html.Div([
    html.Div([
        
         dcc.Graph(id='world_stats',figure=world_stats),
         dcc.RadioItems(id='Typeselect',
                      options=[{'label':i,'value':i} for i in ['Confirmed','Active','Recovered','Deaths']],
                      value='Confirmed',
                      labelStyle={'display': 'inline-block'}),
        
        dcc.Graph(id='world_fig_dy',figure=world_fig_dy_confirm)
    ]),
    
    html.Div([
        
        dcc.Graph(id='india_stats',figure=india_stats),
        dcc.RadioItems(
                id='country_radio',
                options=[{'label': i, 'value': i} for i in ['Total Cases', 'Daily Cases']],
                value='Total Cases',
                labelStyle={'display': 'inline-block'}
            ),
        dcc.Graph(id='india_fig_total',figure=india_fig_total),
        
        #dcc.Graph(id='india_fig_daily',figure=india_fig_daily),
    ]),
    html.Div([
        dcc.Graph(id='top_15_states',figure=top_15_states),
    ]),
    html.Div([
                html.Div([
                dcc.Dropdown(
                id='statename',
                options=[{'label': i, 'value': i} for i in s.state_name.values()],
                value = list(s.state_name.values())[0]
                ),
            ]),
    dcc.Graph(id='state_stats',figure=state_stats),
       html.Div([        
        html.Div([
            dcc.Graph(id='state_fig_total',figure=state_fig_total),
        ], className="six columns"),

        html.Div([

            dcc.Graph(id='state_fig_pie',figure=state_fig_pie),
        ], className="six columns"),
    ], className="row")
    ]),
    html.Div([
         dcc.Graph(id='district_fig',figure=district_fig),
    ])
])

@app.callback(
    Output('world_fig_dy','figure'),
    [Input('Typeselect','value')])
def update_graph3(Typeselect):
    if(Typeselect=="Confirmed"):
        returnfig=world_fig_dy_confirm
    elif(Typeselect=="Recovered"):
        returnfig=world_fig_dy_Recovered
    elif(Typeselect=="Deaths"):
        returnfig=world_fig_dy_deaths
    else:
        returnfig=world_fig_dy_active
    return returnfig
    
@app.callback(
    Output('india_fig_total', 'figure'),
    [Input('country_radio', 'value'),
     ])
def update_graph1(country_radio):
    if(country_radio=="Total Cases"):
        returnfig=india_fig_total
    else:
        returnfig=india_fig_daily
    return returnfig

@app.callback(
    [Output('state_fig_total', 'figure'),
     Output('state_fig_pie', 'figure'),
     Output('state_stats', 'figure'),
    Output('district_fig', 'figure')],
    [Input('statename', 'value'),
     ])
def update_graph2(statename):
    #Update state chart
    
    state_fig_total = s.state_graph(statename)
    #Update pie chart
    
    state_fig_pie=s.state_piechart(statename)

    
    #Update satate stats
    state_stats= s.state_stats(statename)
    
    #update district level chart
    district_fig = s.district_graph(statename)
    return state_fig_total,state_fig_pie,state_stats,district_fig

if __name__=="__main__":
    app.run_server(port=4040)