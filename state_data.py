#!/usr/bin/env python
# coding: utf-8

# In[136]:


import pandas as pd
import requests, zipfile, io
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# In[255]:


#State Wise file prepararation(Transpose)
class state_data:
    def __init__(self):
        resp = requests.get('https://api.covid19india.org/csv/latest/state_wise_daily.csv')
        data=resp.text
        f = StringIO(data)
        state_daily1 = pd.read_csv(f)
        state_daily1["Date"]=pd.to_datetime(state_daily1["Date"],format="%d-%b-%y")
        state_conf=state_daily1[state_daily1["Status"]=="Confirmed"].copy()
        state_recovered=state_daily1[state_daily1["Status"]=="Recovered"].copy()
        state_deaths=state_daily1[state_daily1["Status"]=="Deceased"].copy()

        state_conf.drop(columns=["TT","Status"],axis=1,inplace=True)
        state_recovered.drop(columns=["TT","Status"],axis=1,inplace=True)
        state_deaths.drop(columns=["TT","Status"],axis=1,inplace=True)

        df_melt_c = pd.melt(state_conf, id_vars="Date", value_vars=state_conf.columns[state_conf.columns!="Date"])
        df_melt_r = pd.melt(state_recovered, id_vars="Date", value_vars=state_recovered.columns[state_recovered.columns!="Date"])
        df_melt_d = pd.melt(state_deaths, id_vars="Date", value_vars=state_deaths.columns[state_deaths.columns!="Date"])
        df_melt_c.rename(columns={"value":"Confirmed","variable":"State_Code"},inplace=True)
        df_melt_c["Recovered"]=df_melt_r["value"]
        df_melt_c["Deaths"]=df_melt_d["value"]
        self.state_name={'AN': 'Andaman and Nicobar Islands','AP': 'Andhra Pradesh','AR': 'Arunachal Pradesh','AS': 'Assam','BR': 'Bihar','CH': 'Chandigarh','CT': 'Chhattisgarh',
             'DN': 'Dadra and Nagar Haveli','DD': 'Daman and Diu','DL': 'Delhi','GA': 'Goa','GJ': 'Gujarat','HR': 'Haryana','HP': 'Himachal Pradesh','JK': 'Jammu and Kashmir',
             'JH': 'Jharkhand','KA': 'Karnataka','KL': 'Kerala','LD': 'Lakshadweep','MP': 'Madhya Pradesh','MH': 'Maharashtra','MN': 'Manipur','ML': 'Meghalaya','MZ': 'Mizoram',
             'NL': 'Nagaland','OR': 'Odisha','PY': 'Puducherry','PB': 'Punjab','RJ': 'Rajasthan','SK': 'Sikkim','TN': 'Tamil Nadu','TG': 'Telangana','TR': 'Tripura',
             'UP': 'Uttar Pradesh','UT': 'Uttarakhand','WB': 'West Bengal'}
        df_melt_c['State_Code']=df_melt_c['State_Code'].map(self.state_name)
        df_melt_c["State_Code"]=df_melt_c["State_Code"].fillna("UN")
        state_code=df_melt_c["State_Code"].unique()
        df_melt_c["Total_Confirmed"]=""
        df_melt_c["Total_Recovered"]=""
        df_melt_c["Total_Deaths"]=""
        for i in state_code:
            df_melt_c["Total_Confirmed"][df_melt_c["State_Code"]==i]=df_melt_c["Confirmed"][df_melt_c["State_Code"]==i].cumsum()
            df_melt_c["Total_Recovered"][df_melt_c["State_Code"]==i]=df_melt_c["Recovered"][df_melt_c["State_Code"]==i].cumsum()
            df_melt_c["Total_Deaths"][df_melt_c["State_Code"]==i]=df_melt_c["Deaths"][df_melt_c["State_Code"]==i].cumsum()
    
        self.state_daily=df_melt_c
        #Downlaoding districtwise data
        resp = requests.get('https://api.covid19india.org/csv/latest/district_wise.csv')
        data=resp.text
        f = StringIO(data)
        self.district_data = pd.read_csv(f)
        self.district_data.rename(columns={"Deceased":"Deaths"},inplace=True)
    
    def states_line_graph(self,status):
        #State wise data for confirmed cases
        state_fig = px.line(self.state_daily, x="Date", y=status, color="State_Code")
        return state_fig

    def go_scatter_graph(self,data,x,y,name,mode):
        #State wise data for confirmed cases
        fig=go.Scatter(
            x=data[x],
            y=data[y],
            name=name,
            mode=mode,
            marker=dict( size=12),
        )
        return fig
    
    def top_15_states(self):
        #Top 15 states
        top_15_state=self.state_daily.groupby("State_Code").agg("sum").nlargest(15,columns="Confirmed").reset_index()
        top15_fig = go.Figure()
        top15_fig.add_trace(self.go_scatter_graph(top_15_state,"Confirmed","State_Code","Confirmed","markers"))

        top15_fig.add_trace(self.go_scatter_graph(top_15_state,"Recovered","State_Code","Recovered","markers"))
        top15_fig.add_trace(self.go_scatter_graph(top_15_state,"Deaths","State_Code","Deaths","markers"))
        top15_fig.update_layout(title="Top 15 States in India",
                          xaxis_title="Cases",
                          yaxis_title="States")
        return top15_fig
        
    def state_stats(self,state=""):
        if state =="":
            state=self.state_daily["State_Code"].unique()[0]
        #Single State data
        single_state_data=self.get_state_data(state)
        state_confirm=single_state_data["Confirmed"].sum()
        state_recover=single_state_data["Recovered"].sum()
        state_death=single_state_data["Deaths"].sum()
        state_active=state_confirm-state_recover-state_death
        #States table
        state_stats = go.Figure(data=[go.Table(
            header=dict(values=['Confirmed Cases', 'Recovered Cases',"Active Cases","Death Cases"],
                        align='center'),
            cells=dict(values=[state_confirm,state_recover,state_active,state_death],
                       align='center'))
        ])
        state_stats.update_layout(height=230,title=state+" COVID-19 CASES")
        return state_stats
    
    def get_state_data(self,state):
        #Single State data
        single_state_data=self.state_daily[self.state_daily["State_Code"]==state]
        return single_state_data
    
    def state_piechart(self,state=""):
        if state =="":
            state=self.state_daily["State_Code"].unique()[0]
        piechartclr=["rgb(0, 204, 150)","rgb(99, 110, 250)","rgb(239, 85, 59)"]
        single_state_data=self.get_state_data(state)
        active=single_state_data["Confirmed"].sum()-single_state_data["Recovered"].sum()-single_state_data["Deaths"].sum()
        piechart_sum=[active,single_state_data["Recovered"].sum(),single_state_data["Deaths"].sum()]

        state_fig_pie = go.Figure()
        state_fig_pie = px.pie(piechart_sum,values=0 , names=['Active',"Recovered","Deaths"], title=state+' COVID-19 Stats',labels=['Active',"Recovered","Deaths"],color_discrete_sequence=piechartclr)
        state_fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        return state_fig_pie
        
    def get_district_data(self,state):
        dist_data=self.district_data[self.district_data["State"]==state]
        return dist_data
    
    def go_bar_graph(self,data,status):
        #district wise data as per status
        fig=go.Bar(
            x=data["District"],
            y=data[status],
            name=status,
            text=data[status]
        )
        return fig
    
    def district_graph(self,state=""):
        #District Total Cases can be seprated for Confirmed, Recovered and Deceased for individual graph
        if state =="":
            state=self.state_daily["State_Code"].unique()[0]
        district_fig = go.Figure()
        dist_data=self.get_district_data(state)
        dist_data=dist_data.nlargest(10,columns="Confirmed")
        district_fig = make_subplots(
            rows=2, cols=2, subplot_titles=("Confirmed", "Recovered", "Deaths", "Active")
        )
        district_fig.add_trace(self.go_bar_graph(dist_data,"Confirmed"), row=1, col=1)
        district_fig.add_trace(self.go_bar_graph(dist_data,"Recovered"), row=1, col=2)
        district_fig.add_trace(self.go_bar_graph(dist_data,"Deaths"), row=2, col=1)
        district_fig.add_trace(self.go_bar_graph(dist_data,"Active"), row=2, col=2)
        return district_fig
        
    def state_graph(self,state=""):
        #Update state chart
        if state =="":
            state=self.state_daily["State_Code"].unique()[0]
        single_state_data=self.get_state_data(state)
        state_fig_total = go.Figure()
        state_fig_total.add_trace(self.go_scatter_graph(single_state_data,"Date","Total_Confirmed","Confirmed","lines"))
        state_fig_total.add_trace(self.go_scatter_graph(single_state_data,"Date","Total_Recovered","Recovered","lines"))
        state_fig_total.add_trace(self.go_scatter_graph(single_state_data,"Date","Total_Deaths","Deaths","lines"))
        state_fig_total.update_layout( title_text=str(state)+" Total Cases")
        return state_fig_total
    


# In[ ]:




