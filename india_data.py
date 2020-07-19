#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests, zipfile, io
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# In[28]:


class india_data:
    def __init__(self):
        #Live data Reading India Data
        resp = requests.get('https://api.covid19india.org/csv/latest/case_time_series.csv')
        data=resp.text
        f = StringIO(data)
        india_data = pd.read_csv(f)
        india_data["Date"]=india_data["Date"]+" 2020"
        india_data["Date"]=pd.to_datetime(india_data["Date"])
        india_data.rename(columns={"Daily Deceased":"Daily_Deaths","Total Deceased":"Total_Deaths","Daily Confirmed":"Daily_Confirmed","Total Confirmed":"Total_Confirmed","Daily Recovered":"Daily_Recovered","Total Recovered":"Total_Recovered"},inplace=True)
        self.india_data=india_data

    def stats_graph(self):
        india_confirm=self.india_data["Daily_Confirmed"].sum()
        india_recover=self.india_data["Daily_Recovered"].sum()
        india_death=self.india_data["Daily_Deaths"].sum()
        india_active=india_confirm-india_recover-india_death
        india_stats = go.Figure(data=[go.Table(
            header=dict(values=['Confirmed Cases', 'Recovered Cases',"Active Cases","Death Cases"],
                        align='center'),
            cells=dict(values=[india_confirm,india_recover,india_active,india_death],

                       align='center'))
        ])
        india_stats.update_layout(height=230,title="INDIA COVID-19 CASES")
        return india_stats
    
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
    
    def india_graph(self,graph_type="Total"):
        #India total Cases
        india_fig_total = go.Figure()
        india_fig_total.add_trace(self.go_scatter_graph(self.india_data,"Date",graph_type+"_Confirmed","Confirmed","lines"))         
        india_fig_total.add_trace(self.go_scatter_graph(self.india_data,"Date",graph_type+"_Recovered","Recovered","lines"))
        india_fig_total.add_trace(self.go_scatter_graph(self.india_data,"Date",graph_type+"_Deaths","Deaths","lines"))
        india_fig_total.update_layout(title="India "+graph_type+" Cases")
        return india_fig_total
    


# In[ ]:




