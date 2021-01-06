# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 12:09:39 2021

@author: aa63
"""


################################################################
# Import the libraries again
import pandas as pd, numpy as np, os, shutil, streamlit as st, base64, datetime as dt, altair as alt, seaborn as sns, matplotlib.pyplot as plt, more_itertools as mit
# from bokeh.plotting import figure
from datetime import datetime, date, timedelta
from statsmodels.tsa.seasonal import STL
from pandas.plotting import register_matplotlib_converters
import plotly.express as px
# import plotly.express as px
register_matplotlib_converters()
sns.set_style('darkgrid')


# change the os directory
# os.chdir(r'C:\Users\aa63\Desktop\IMM Project\Data')





################################################################
# Add the title of the application
st.title('Vaccination Analysis')




################################################################
# My main function, used to get the data from the excel sheets
@st.cache   # effortless caching
def load_data():
    # Specify which sheets to join and which one to select by itself
    names = pd.ExcelFile('https://raw.githubusercontent.com/abirashedanna/datasets/master/Immunization-coverage-by-antigen-country-regional-and-global-trends-WUENIC-2019revision.xlsx').sheet_names
    sheets_to_join = names[:-1]
    regional_global = names[-1:]
    
    # read the sheets into different DF
    sheets_all_df = pd.concat(pd.read_excel('https://raw.githubusercontent.com/abirashedanna/datasets/master/Immunization-coverage-by-antigen-country-regional-and-global-trends-WUENIC-2019revision.xlsx',
                                 sheet_name=sheets_to_join), ignore_index=True)
    
    regional_global_df = pd.concat(pd.read_excel('https://raw.githubusercontent.com/abirashedanna/datasets/master/Immunization-coverage-by-antigen-country-regional-and-global-trends-WUENIC-2019revision.xlsx',
                                 sheet_name=regional_global), ignore_index=True)
    
    
    # Read the income group dataframe so that we can add the income group to the original data set
    income_grp = pd.read_csv('https://raw.githubusercontent.com/abirashedanna/datasets/master/Income_Group.csv')
    income_grp = income_grp[income_grp['Region'].notna()]
    income_grp = income_grp.drop(['Region', 'SpecialNotes', 'TableName', 'Unnamed: 5'], axis=1)
    income_grp = income_grp.rename(columns={"Country Code": "iso3",
                                            "IncomeGroup": "INC_GRP"})
    
    df_merged = sheets_all_df.merge(income_grp, how='left', on=['iso3'])
    
    
    # melting the dataframe into a long dataframe
    df_melted = df_merged.melt(id_vars= ['unicef_region', 'iso3', 'country', 'vaccine', 'INC_GRP'],
                                 var_name = "Year",
                                 value_name = "Percentage")
    # Sort the values
    df_melted = df_melted.sort_values(by=['vaccine', 'iso3', 'Year'])
    df_melted['Year'] = pd.to_datetime(df_melted.Year.astype(str), format='%Y').dt.date
    # df_melted['Year_c'] = df_melted['Year']
    df_melted['Year'] = pd.DatetimeIndex(df_melted['Year']).year # this changes the date format to years only
    return df_melted, regional_global_df

# load the data
df_melted, regional_global_df = load_data()



################################################################
# Here we will create lists and values to use in the
# interactive widgets, having unique values from the main df
vaccine_dstnct = df_melted['vaccine'].unique()
years_dstct = df_melted['Year'].unique()
# date_beg_temp = df_melted['Year_c'].unique().min()
# date_end_temp = df_melted['Year_c'].unique().max()

income_grp_dstct = df_melted['INC_GRP'].dropna().unique()
cont_dstct = df_melted['country'].dropna().unique()
reg_dstct = df_melted['unicef_region'].dropna().unique()



################################################################
# Here we define the buttons and sidebar


# Add an About button to show the details about this data set and analysis
if st.sidebar.checkbox('About'):
    st.markdown(""" Write Things About the data Click inspect for the data Webpage and enter them """,unsafe_allow_html=True)

# Select box for the Vaccine Type
vaccine_slc = st.sidebar.selectbox('Vaccine Type', vaccine_dstnct.tolist())


# Multi-selct box for the date field
date_slc = st.sidebar.multiselect('Year Select',
                                  years_dstct.tolist(),
                                  default = years_dstct[years_dstct >= 2010])


# Multi-selct box for the date field
# date_slc = st.sidebar.date_input('Enter Beginning Date', value = date_beg_temp)
# date_slc2 = st.sidebar.date_input('Enter Ending Date', value = date_end_temp)



# Multi-selct box for the Income Group
income_grp_slc = st.sidebar.multiselect('Income Group',
                                        income_grp_dstct.tolist(),
                                        default = ["Upper middle income"])

# Radio button for the Country or Region, to selct either or
cont_reg_radio = st.sidebar.radio('Choose by Country or By Region',
                          options = ('Country', 'Region', 'Country and Region'))

# check = st.sidebar.checkbox('All')
# check

# If we choose country, then show Multi-selct box for the Countries which reads from the list of the selected Income Groups
if cont_reg_radio == 'Country':
    country_grp_slc = st.sidebar.multiselect('Country',
                                         df_melted.loc[df_melted['INC_GRP'].isin(income_grp_slc)].iloc[:,2].unique().tolist())

# If we choose Region, then show Multi-selct box for the Regions which reads from the list of the selected Income Groups
if cont_reg_radio == 'Region':
    region_grp_slc = st.sidebar.multiselect('Region',
                                        df_melted.loc[df_melted['INC_GRP'].isin(income_grp_slc)].iloc[:,0].unique().tolist())

# If we choose Country and Region, then show Multi-selct box for the sRegions which reads from the list of the selected Income Groups
if cont_reg_radio == 'Country and Region':
    region_grp_slc2 = st.sidebar.multiselect('Region',
                                    df_melted.loc[df_melted['INC_GRP'].isin(income_grp_slc)].iloc[:,0].unique().tolist())

# If we choose Country and Region, then show Multi-selct box for the Countries which reads from the list of the selected Income Groups and Regions
if cont_reg_radio == 'Country and Region':
    country_grp_slc2 = st.sidebar.multiselect('Country',
                                         df_melted.loc[df_melted['INC_GRP'].isin(income_grp_slc) & df_melted['unicef_region'].isin(region_grp_slc2)].iloc[:,2].unique().tolist())

# pd.DatetimeIndex(df_melted['Year']



################################################################
# In the below steps we will create data sets filtered 
# on the conditions we specify in our interactive widgets


# Create a data frame from the selected filters. If the radio button is Country then filter by the selected buttons

# if we selected only the country
if cont_reg_radio == 'Country':
    data_1=df_melted.loc[(df_melted['Year'].isin(date_slc))\
                      &(df_melted['vaccine']==vaccine_slc)\
                          &(df_melted['INC_GRP'].isin(income_grp_slc))\
                              &(df_melted['country'].isin(country_grp_slc))].reset_index(drop=True)

# # if we selected only the country
# if cont_reg_radio == 'Country':
#     data_1=df_melted.loc[(df_melted['Year'] >= pd.DatetimeIndex(date_beg_temp).year)\
#                          &(df_melted['Year'] <= pd.DatetimeIndex(date_end_temp).year)\
#                              &(df_melted['vaccine']==vaccine_slc)\
#                                  &(df_melted['INC_GRP'].isin(income_grp_slc))\
#                                      &(df_melted['country'].isin(country_grp_slc))].reset_index(drop=True)

# Create a data frame from the selected filters. If the radio button is Region then filter by the selected buttons
# If we selected region
if cont_reg_radio == 'Region':
    data_1=df_melted.loc[(df_melted['Year'].isin(date_slc))\
                      &(df_melted['vaccine']==vaccine_slc)\
                          &(df_melted['INC_GRP'].isin(income_grp_slc))\
                              &(df_melted['unicef_region'].isin(region_grp_slc))].reset_index(drop=True)

# # If we selected region
# if cont_reg_radio == 'Region':
#     data_1=df_melted.loc[(df_melted['Year'] >= pd.DatetimeIndex(date_beg_temp).year)\
#                          &(df_melted['Year'] <= pd.DatetimeIndex(date_end_temp).year)\
#                              &(df_melted['vaccine']==vaccine_slc)\
#                                  &(df_melted['INC_GRP'].isin(income_grp_slc))\
#                                      &(df_melted['unicef_region'].isin(region_grp_slc))].reset_index(drop=True)


# Create a data frame from the selected filters. If the radio button is Country and Region then filter by the selected buttons
# If we selected Country and Region
if cont_reg_radio == 'Country and Region':
    data_1=df_melted.loc[(df_melted['Year'].isin(date_slc))\
                      &(df_melted['vaccine']==vaccine_slc)\
                          &(df_melted['INC_GRP'].isin(income_grp_slc))\
                              &(df_melted['unicef_region'].isin(region_grp_slc2))\
                                  &(df_melted['country'].isin(country_grp_slc2))].reset_index(drop=True)

# # If we selected Country and Region
# if cont_reg_radio == 'Country and Region':
#     data_1=df_melted.loc[(df_melted['Year'] >= pd.DatetimeIndex(date_beg_temp).year)\
#                          &(df_melted['Year'] <= pd.DatetimeIndex(date_end_temp).year)\
#                              &(df_melted['vaccine']==vaccine_slc)\
#                                  &(df_melted['INC_GRP'].isin(income_grp_slc))\
#                                      &(df_melted['unicef_region'].isin(region_grp_slc2))\
#                                          &(df_melted['country'].isin(country_grp_slc2))].reset_index(drop=True)




################################################################
# Add download Button to the canvas
def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'


# display the data in a matrix
# st.write(data_1)

# Display the data frame in a tableau 
# Using a checkbox, if the checkbox is checked then show data
# Else don't show data
if st.checkbox('Show data table'):
    st.subheader('Data table')
    st.dataframe(data_1, width = 1000)
    # """ Press the Download Button to download a copy of the data in CSV format """
    st.markdown(get_table_download_link(data_1), unsafe_allow_html=True)   # download data button
    # st.write(data)


################################################################
# Display the min and max by country
# Here we relied on the min value and max value
# if cont_reg_radio == 'Region':
#     data_min = data_1.drop(['iso3', 'country', 'vaccine', 'INC_GRP'], axis=1)\
#     .groupby(['unicef_region'])['Percentage'].min().reset_index().sort_values(by=['unicef_region'])
#     data_max = data_1.drop(['iso3', 'country', 'vaccine', 'INC_GRP'], axis=1)\
#     .groupby(['unicef_region'])['Percentage'].max().reset_index().sort_values(by=['unicef_region'])
#     # data_min_max_.iloc[0,1]
#     min = data_1[data_1['Percentage']==data_min.iloc[0,1]][['unicef_region', 'Year', 'Percentage']]
#     min
#     max = data_1[data_1['Percentage']==data_max.iloc[0,1]][['unicef_region', 'Year', 'Percentage']]
#     max
# else:
#     data_min = data_1.drop(['iso3', 'unicef_region', 'vaccine', 'INC_GRP'], axis=1)\
#     .groupby(['country'])['Percentage'].min().reset_index().sort_values(by=['country'])
#     data_max = data_1.drop(['iso3', 'unicef_region', 'vaccine', 'INC_GRP'], axis=1)\
#     .groupby(['country'])['Percentage'].max().reset_index().sort_values(by=['country'])
#     # data_min_max_.iloc[0,1]
#     """Min Percentage if Vaccinations per Country"""
#     min = data_1[data_1['Percentage']==data_min.iloc[0,1]][['country', 'Year', 'Percentage']]
#     min
#     """Max Percentage if Vaccinations per Country"""
#     max = data_1[data_1['Percentage']==data_max.iloc[0,1]][['country', 'Year', 'Percentage']]
#     max

# """Percetage change in vaccinations between the Min and Max"""
# min_value = min.iloc[:,2:3].values
# max_value = max.iloc[:,2:3].values
# percentage_change = (max_value[1]-min_value[1])/min_value[1] *100
# (percentage_change)




# Display the min and max by country
# Here we relied on the min date and max date
if cont_reg_radio == 'Region':
    st.header('Percetage change in vaccinations between the Min and Max by Region')
    
    data_min = data_1.drop(['iso3', 'country', 'vaccine', 'INC_GRP'], axis=1)\
    .groupby(['unicef_region', 'Year'])['Percentage'].mean().reset_index().sort_values(by=['unicef_region'])
    data_min2 = data_min[data_min['Year']==data_min['Year'].min()].reset_index(drop=True)
    min2 = data_min2
    min2 = min2.rename(columns={"unicef_region": "Region",
                              "Year": "Year Min",
                              "Percentage": "Min %"})

    data_max = data_1.drop(['iso3', 'country', 'vaccine', 'INC_GRP'], axis=1)\
    .groupby(['unicef_region', 'Year'])['Percentage'].mean().reset_index().sort_values(by=['unicef_region'])
    data_max2 = data_max[data_max['Year']==data_max['Year'].max()].reset_index(drop=True)
    max2 = data_max2
    max2 = max2.rename(columns={"unicef_region": "Region",
                          "Year": "Year Max",
                          "Percentage": "Max %"})
    percentage_change = pd.merge(min2, max2, how='left', on='Region')
    percentage_change['% Change'] = ((percentage_change['Max %'] - percentage_change['Min %'])/percentage_change['Min %'] ) * 100
    percentage_change
else:
    st.header('Percetage change in vaccinations between the Min and Max by Country')
    data_min = data_1.drop(['iso3', 'unicef_region', 'vaccine', 'INC_GRP'], axis=1)\
    .groupby(['country', 'Year'])['Percentage'].mean().reset_index().sort_values(by=['country'])
    data_min2 = data_min[data_min['Year']==data_min['Year'].min()].reset_index(drop=True)
    min2 = data_min2
    min2 = min2.rename(columns={"country": "Country",
                              "Year": "Year Min",
                              "Percentage": "Min %"})
    
    data_max = data_1.drop(['iso3', 'unicef_region', 'vaccine', 'INC_GRP'], axis=1)\
    .groupby(['country', 'Year'])['Percentage'].mean().reset_index().sort_values(by=['country'])
    data_max2 = data_max[data_max['Year']==data_max['Year'].max()].reset_index(drop=True)
    max2 = data_max2
    max2 = max2.rename(columns={"country": "Country",
                          "Year": "Year Max",
                          "Percentage": "Max %"})
    percentage_change = pd.merge(min2, max2, how='left', on='Country')
    percentage_change['% Change'] = ((percentage_change['Max %'] - percentage_change['Min %'])/percentage_change['Min %'] ) * 100
    percentage_change





# Display the Average by country
# Here we relied on the min date and max date
if cont_reg_radio == 'Region':
    st.header('Average of Percentage of Vaccinations by Region')
    
    data_mean = data_1.drop(['iso3', 'country', 'vaccine', 'INC_GRP'], axis=1)\
    .groupby(['unicef_region'])['Percentage'].mean().reset_index().sort_values(by=['unicef_region'])
    # data_min2 = data_min[data_min['Year']==data_min['Year'].mean()].reset_index(drop=True)
    mean = data_mean
    mean = mean.rename(columns={"country": "Country
                              "iso3": "Country Abbr"})
    mean

else:
    st.header('Average of Percentage of Vaccinations by Country')
    
    data_mean = data_1.drop(['unicef_region', 'vaccine', 'INC_GRP'], axis=1)\
    .groupby(['country', 'iso3'])['Percentage'].mean().reset_index().sort_values(by=['country'])
    # data_min2 = data_min[data_min['Year']==data_min['Year'].mean()].reset_index(drop=True)
    mean = data_mean
    mean = mean.rename(columns={"country": "Country",
                              "iso3": "Country Abbr"})
    mean




################################################################
# From the data we selected, drop all columns, select only the year and percentage
# then take the average of the percentage
if cont_reg_radio == 'Region':
    st.header('Timeline of the Percetage change in vaccinations on the Aggregate Region Level')
    data_line_chart = data_1.drop(['unicef_region', 'iso3', 'country', 'vaccine', 'INC_GRP'], axis=1)\
        .groupby(['Year'])['Percentage'].mean().reset_index().sort_values(by=['Year'])
    data_line_chart = data_line_chart[['Year', 'Percentage']]
    data_line_chart['Year'] = pd.to_datetime(data_line_chart.Year.astype(str), format='%Y').dt.date  # Change back the year to date format so we can plot correctly
    data_line_chart = data_line_chart.rename(columns={'Year':'index'}).set_index('index')
else:
    st.header('Timeline of the Percetage change in vaccinations on the Aggregate Country Level')
    data_line_chart = data_1.drop(['unicef_region', 'iso3', 'country', 'vaccine', 'INC_GRP'], axis=1)\
        .groupby(['Year'])['Percentage'].mean().reset_index().sort_values(by=['Year'])
    data_line_chart = data_line_chart[['Year', 'Percentage']]
    data_line_chart['Year'] = pd.to_datetime(data_line_chart.Year.astype(str), format='%Y').dt.date  # Change back the year to date format so we can plot correctly
    data_line_chart = data_line_chart.rename(columns={'Year':'index'}).set_index('index')


# print the chart
st.line_chart(data_line_chart)



# Plot the map of the countries/regions and their percentages
if cont_reg_radio != 'Region':
    st.header('Map of the Average Percentages of Vaccinations by Country')
    coords = pd.read_excel('https://raw.githubusercontent.com/abirashedanna/datasets/master/coords.xlsx')
    data_12 = mean.merge(coords, how='left', left_on=['iso3'], right_on=['Alpha-3 code'])
    fig = px.scatter_mapbox(data_12, lat="latitude", lon="longitude", hover_name="Country", hover_data=["Country", "Percentage"],
                    size="Percentage",color_discrete_sequence=["red"], zoom=1, height=500,width=1300)
    fig.update_layout(mapbox_style="carto-positron")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)



# Plot the bar chart of the countries/regions and their percentages
if cont_reg_radio != 'Region':
    st.header('Bar Chart Comparison of Different Countries Percentage of Vaccinations')
    fig = px.bar(mean, x=mean['country'], y=mean['Percentage'] ,height=500,width=700)
    fig.update_layout(
       title="Bar Chart Comparison of Different Countries Percentage of Vaccinations <br>",
       xaxis_title="Countries",
       yaxis_title="Percentage of Population Vaccination",
    
        font=dict(
            family="Courier New, monospace",
            size=11,
            color="RebeccaPurple"
        )
    )
    st.plotly_chart(fig)
else:
    st.header('Bar Chart Comparison of Different Regions Percentage of Vaccinations')
    fig = px.bar(mean, x=mean['unicef_region'], y=mean['Percentage'] ,height=500,width=700)
    fig.update_layout(
       title="Bar Chart Comparison of Different Regions Percentage of Vaccinations <br>",
       xaxis_title="Regions",
       yaxis_title="Percentage of Population Vaccination",
    
        font=dict(
            family="Courier New, monospace",
            size=11,
            color="RebeccaPurple"
        )
    )
    st.plotly_chart(fig)






