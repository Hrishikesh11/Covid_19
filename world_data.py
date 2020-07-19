#!/usr/bin/env python
# coding: utf-8

# In[8]:


import pandas as pd
import requests, zipfile, io
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import plotly.graph_objects as go
import plotly.express as px


# In[11]:


class world_data:
    def __init__(self):
        #Confirmed world data
        df_conf_raw = requests.get("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
        data=df_conf_raw.text
        f = StringIO(data)
        df_conf = pd.read_csv(f)

        #Recovered world data
        df_recovered_raw = requests.get("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")
        data=df_recovered_raw.text
        f = StringIO(data)
        df_recovered = pd.read_csv(f)

        #Recovered world data
        df_death_raw = requests.get("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
        data=df_death_raw.text
        f = StringIO(data)
        df_death = pd.read_csv(f)

        df_conf=df_conf.groupby("Country/Region").sum().reset_index()
        df_death=df_death.groupby("Country/Region").sum().reset_index()
        df_recovered=df_recovered.groupby("Country/Region").sum().reset_index()

        df_conf.drop(columns=["Lat","Long"],inplace=True)
        df_death.drop(columns=["Lat","Long"],inplace=True)
        df_recovered.drop(columns=["Lat","Long"],inplace=True)

        df_conf=df_conf.rename(columns={"Country/Region":"Country"})
        df_death=df_death.rename(columns={"Country/Region":"Country"})
        df_recovered=df_recovered.rename(columns={"Country/Region":"Country"})

        df_conf=df_conf.set_index("Country",drop=True)
        df_death=df_death.set_index("Country",drop=True)
        df_recovered=df_recovered.set_index("Country",drop=True)

        df_conf=df_conf.T
        df_death=df_death.T
        df_recovered=df_recovered.T

        df_conf['Date'] = df_conf.index
        df_death['Date'] = df_death.index
        df_recovered['Date'] = df_recovered.index

        df_melt_c = pd.melt(df_conf, id_vars="Date", value_vars=df_conf.columns[:-1])
        df_melt_d = pd.melt(df_death, id_vars="Date", value_vars=df_death.columns[:-1])
        df_melt_r = pd.melt(df_recovered, id_vars="Date", value_vars=df_recovered.columns[:-1])

        df_melt_c.rename(columns={"value":"Confirmed"},inplace=True)

        df_melt_c["Recovered"]=df_melt_r["value"]

        df_melt_c["Deaths"]=df_melt_d["value"]
        df_melt_c["Date"]=pd.to_datetime(df_melt_c["Date"])
        df_melt_c["Date"]=df_melt_c["Date"].apply(lambda x:str(x.date()))
        df_melt_c["Active"]=df_melt_c["Confirmed"]-df_melt_c["Recovered"]-df_melt_c["Deaths"]
        self.world_data=df_melt_c

    def world_choropleth(self,status):
            
        # Manipulating the original dataframe
        #data_pro4 = world_data
        data_pro4 = self.world_data.groupby(['Date','Country']).sum().reset_index()
        data_pro4 = data_pro4[data_pro4[status]>0]
        # Creating the visualization
        world_fig_dy_confirm=go.Figure()
        world_fig_dy_confirm = px.choropleth(data_pro4,
                            locations="Country",
                            locationmode = "country names",
                            color=status,
                            hover_name="Country",
                            animation_frame="Date",
                            hover_data=["Confirmed","Active","Deaths","Recovered"],
                           )
        world_fig_dy_confirm.update_layout(
            title_text = 'Global Spread of Coronavirus',
            title_x = 0.5,
            geo=dict(
                showframe = False,
                showcoastlines = False,
            ))
        return (world_fig_dy_confirm)
   
    def world_stats(self):
        data_pro1=self.world_data.groupby(['Country', 'Date']).sum().reset_index().sort_values('Date', ascending=False)
        #Remove DUplicates
        data_pro2=data_pro1.drop_duplicates(subset = ['Country'])
        data_pro2 = data_pro2[data_pro2['Confirmed']>0]
        world_confirm=data_pro2["Confirmed"].sum()
        world_recover=data_pro2["Recovered"].sum()
        world_death=data_pro2["Deaths"].sum()
        world_active=world_confirm-world_recover-world_death
        #World data table
        world_stats = go.Figure(data=[go.Table(
            header=dict(values=['Confirmed Cases', 'Recovered Cases',"Active Cases","Death Cases"],
                        align='center'),
            cells=dict(values=[world_confirm,world_recover,world_active,world_death],

                       align='center'))
        ])
        world_stats.update_layout(height=230,title="WORLD COVID-19 CORONAVIRUS PANDEMIC")
        return (world_stats)


# In[ ]:




