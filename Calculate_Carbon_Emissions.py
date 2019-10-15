# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 17:18:13 2019

@author: mschwarz
"""

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os 
import numpy as np 

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

matplotlib.rcdefaults()
#Plot Styles
plt.rcParams.update({'font.size': 12, 'font.family': 'Calibri'})
plt.rc('figure', titlesize=12)
plt.rc('axes', axisbelow=True)
plt.rcParams["figure.figsize"] = (20,10)

#Set working directory
os.chdir("Z:/Public/997 Collaboration/Marius Schwarz/03_VGI in California/00_Marius Schwarz/99_Python Code/03_NetLogo Results Processing")  

#%%

#####################################################################################################
########################           Calculating emission changes             ##########################
######################################################################################################

# We calculate carbon emissions that occur from using power plants to meet (residential) electricity demand
# To do so, we need the following data:
# 1) Dataframe that includes an hourly load profile (each hour needs to be a seperate column)
# 2) Dataframe on 'powerplants_average_day.csv'  (here: Z:\Public\997 Collaboration\Marius Schwarz\03_VGI in California\00_Marius Schwarz\06_CA Power Plants)
# 3) Total emissions list that is filled during the calculation
# 4) Delta emission list that includes the reduced emission compared to the first entry of the total emissions list
# 5) Adjusted dataframe that include the hourly load profile (save this adjusted file to the same location as the original file with the suffix '_co2_adj)

#%%

# 0) Read Reference Scenario, which we use to calculate emission savings

df_list = []

file_path_ref = "../../04_Results/01_NetLogo Results/20190920/"
csv_file_to_read = "20190911 - Reference - No Tech Adoption"

df_list.append(pd.read_csv(file_path_ref + csv_file_to_read + "_pre.csv", sep=',', low_memory=False))


#%%

# 1) Read in Dataframe that includes an hourly load profile

csv_file_to_read_list = [0]


# Sensitivities

file_path = "../../04_Results/01_NetLogo Results/20190916/"

# Sensitivity Analyses - EV owners with PV
#csv_file_to_read_list.append("20190916 - Tiered - sensitivity - EV owners with PV")
#csv_file_to_read_list.append("20190916 - TOU - sensitivity - EV owners with PV")
#csv_file_to_read_list.append("20190916 - Hourly Pricing - sensitivity - EV owners with PV")


# Sensitivity Analyses - Tech Resizing
#csv_file_to_read_list.append("20190916 - Tiered - sensitivity - Tech resizing")
#csv_file_to_read_list.append("20190916 - TOU - sensitivity - Tech resizing")
#csv_file_to_read_list.append("20190916 - Hourly Pricing - sensitivity - Tech resizing")
 
 
# Sensitivity Analyses - EV rollout scenarios
csv_file_to_read_list.append("20190916 - Tiered - sensitivity - EV rollout scenarios")
csv_file_to_read_list.append("20190916 - TOU - sensitivity - EV rollout scenarios")
csv_file_to_read_list.append("20190916 - Hourly Pricing - sensitivity - EV rollout scenarios")


# Sensitivity Analyses - Work Charging
csv_file_to_read_list.append("20190916 - Tiered - sensitivity - work charging possible")
csv_file_to_read_list.append("20190916 - TOU - sensitivity - work charging possible")
csv_file_to_read_list.append("20190916 - Hourly Pricing - sensitivity - work charging possible")


# Sensitivity Analyses - Respond to price signals
#csv_file_to_read_list.append("20190916 - Tiered - sensitivity - response to price signals")
#csv_file_to_read_list.append("20190916 - TOU - sensitivity - response to price signals")
#csv_file_to_read_list.append("20190916 - Hourly Pricing - sensitivity - response to price signals")



# Scenarios
#general path for files
#file_path = "../../04_Results/01_NetLogo Results/20190911/"
#
#csv_file_to_read_list.append("20190911 - pricing Tiered 078 response - S1")
#csv_file_to_read_list.append("20190911 - pricing TOU 078 response - S2")
#csv_file_to_read_list.append("20190911 - pricing Hourly Pricing 078 response - S3")


# Scenarios  *** NEW
#general path for files
#file_path = "../../04_Results/01_NetLogo Results/20191009/"
#
#csv_file_to_read_list.append("20191009 - pricing Tiered 078 response - S1")
#csv_file_to_read_list.append("20191009 - pricing TOU 078 response - S2")
#csv_file_to_read_list.append("20191009 - pricing Hourly Pricing 078 response - S3")




for csv in csv_file_to_read_list: 
    
    if csv != 0:
        df_list.append(pd.read_csv(file_path + csv + "_pre.csv", sep=',', low_memory=False))


#%%

# 2) Read in Dataframe on 'powerplants_average_day.csv'
years = list(range(2005,2031))
hours = list(range(0,24)) 

for y in years:

    path_powerplants = "../../06_CA Power Plants/"
    
    globals()["powerplants_average_day_" + str(y)] = pd.read_csv(path_powerplants + "powerplants_average_day_" + str(y) + ".csv") 
    
    
#%%

#dataframe_loads = dataframe_loads.iloc[:5]
#dataframe_loads.shape
# Out[12]: (5, 977)

#%%

# 3. Total emissions list that is filled during the calculation
    
# Add new columns to dataframe

for df in df_list: 
    
    for x in hours:
    
        df['HOURLY_EMISSIONS_' + str(x)] = np.nan
    
    #%%

# Sort dataframe according merit order
#powerplants_ca_mo = powerplants_average_day.sort_values(by=[\
#                                    'MO_' + str(x)], ascending=True)

for df in df_list:

    for y in years:
    
        print("NEW YEAR")
        print(y)
    
        indexing_year = df[df.loc[:,'Year'] == y].index
    
        for x in hours:
        
            plants = globals()["powerplants_average_day_" + str(y)].sort_values(by=['MO_' + str(x)], ascending=True)
            cum_capacity = []
        
        
            for index, row in plants.iterrows():
            
                if len(cum_capacity) == 0:
                    cum_capacity.append(row['CAPACITY_MO_[MW]_' + str(x)])
                else:
                    cum_capacity.append(cum_capacity[-1] + row['CAPACITY_MO_[MW]_' + str(x)])
        
            plants['capacity_cum'] = cum_capacity
        
        
            Hourly_emissions_all_plants = []
        
            for index, row2 in df.loc[indexing_year,:].iterrows():
            
                demand = row2['system-load-profile_' + str(x)]
    
                #indexing
            
                indexing_demand = plants[plants.loc[:,'capacity_cum'] <= demand].index
            
                hourly_emissions_calc_list = plants.loc[indexing_demand, 'CAPACITY_MO_[MW]_' + str(x)] * plants.loc[indexing_demand, 'EMISSIONS_[tCO2/MWh]_' + str(y)]
                hourly_emissions_calc = sum(hourly_emissions_calc_list)
            
                Hourly_emissions_all_plants.append(hourly_emissions_calc)
        
            df.loc[indexing_year, 'HOURLY_EMISSIONS_' + str(x)] = Hourly_emissions_all_plants
            
    
#%%
    
# Calculate Annual Emissions
   
for df in df_list: 
    df['ANNUAL_EMISSIONS'] = np.nan
   
    annual_total_emissions = pd.DataFrame()
    annual_total_emissions['ANNUAL_EMISSIONS'] = np.nan
   
    for x in hours: 
        if x == 0:
            annual_total_emissions['ANNUAL_EMISSIONS'] = df['HOURLY_EMISSIONS_' + str(x)]
        else: 
            annual_total_emissions['ANNUAL_EMISSIONS'] = annual_total_emissions['ANNUAL_EMISSIONS'] + df['HOURLY_EMISSIONS_' + str(x)]
       
        df['ANNUAL_EMISSIONS'] = annual_total_emissions['ANNUAL_EMISSIONS'] * 365
        
        
#%%
        
# Calculate Cumulative Emissions
        
for df in df_list:
    df['CUMULATIVE_EMISSIONS'] = np.nan
    
    
    # for every year in the run
    runs_number= len(df.drop_duplicates(subset='[run number]', keep='first'))
    runs_list = list(range(1, runs_number + 1))
    
    for r in runs_list: 
        
        cumulative_emissions = 0
    
        for y in years:
            indexing = df[(df.loc[:,'[run number]'] == r) & \
                          (df.loc[:,'Year'] == y)].index
    
            cumulative_emissions = cumulative_emissions + df.loc[indexing, 'ANNUAL_EMISSIONS'].values[0]
            df.loc[indexing, 'CUMULATIVE_EMISSIONS'] = cumulative_emissions
    

#%%
        
## Calculate Annual Emission Savings
number_df = list(range(0,len(df_list)))
#
## reference dataframe
reference = pd.DataFrame()
reference['Average'] = np.nan
                      
    
for df, num in zip(df_list,number_df):
    
    df['ANNUAL_EMISSION_SAVINGS'] = np.nan
           
    for y in years:
        
        indexing =  df[df.loc[:, 'Year'] == y].index
       
        # reference
        if num == 0:
            reference.at[y - 2005, 'Average'] = df.loc[indexing,'ANNUAL_EMISSIONS'].mean()          
        
        #emission savings
        df.loc[indexing, 'ANNUAL_EMISSION_SAVINGS'] = reference.at[y - 2005,'Average'] - df.loc[indexing, 'ANNUAL_EMISSIONS']
      
    
    
#%%
        
# Calculate Cumulative Emission Savings

reference = pd.DataFrame()
reference['Average'] = np.nan
                      
    
for df, num in zip(df_list,number_df):
    
    df['CUMULATIVE_EMISSION_SAVINGS'] = np.nan
           
    for y in years:
        
        indexing =  df[df.loc[:, 'Year'] == y].index
       
        # reference
        if num == 0:
            reference.at[y - 2005, 'Average'] = df.loc[indexing,'CUMULATIVE_EMISSIONS'].mean()          
        
        #emission savings
        df.loc[indexing, 'CUMULATIVE_EMISSION_SAVINGS'] = reference.at[y - 2005,'Average'] - df.loc[indexing, 'CUMULATIVE_EMISSIONS']

#%%
        
# Add EV emission savings to electricity emission savings
        
# Annual        
for df in df_list: 
    df['ANNUAL_EMISSION_SAVINGS_INCL_EV'] = np.nan
   
    annual_total_emissions_incl_ev = pd.DataFrame()
    annual_total_emissions_incl_ev['ANNUAL_EMISSION_SAVINGS_INCL_EV'] = np.nan
   
    annual_total_emissions_incl_ev['ANNUAL_EMISSION_SAVINGS_INCL_EV'] = df['ANNUAL_EMISSION_SAVINGS'] + df['annual-CO2-emission-reductions-from-gasoline-displacement'] * 1000000

    df['ANNUAL_EMISSION_SAVINGS_INCL_EV'] = annual_total_emissions_incl_ev['ANNUAL_EMISSION_SAVINGS_INCL_EV']

#Cumulative
for df in df_list:
    df['CUMULATIVE_EMISSION_SAVINGS_INCL_EV'] = np.nan
    
    
    # for every year in the run
    runs_number= len(df.drop_duplicates(subset='[run number]', keep='first'))
    runs_list = list(range(1, runs_number + 1))
    
    for r in runs_list: 
        
        cumulative_emissions_incl_ev = 0
    
        for y in years:
            indexing = df[(df.loc[:,'[run number]'] == r) & \
                          (df.loc[:,'Year'] == y)].index
    
            cumulative_emissions_incl_ev = cumulative_emissions_incl_ev + df.loc[indexing, 'ANNUAL_EMISSION_SAVINGS_INCL_EV'].values[0]
            df.loc[indexing, 'CUMULATIVE_EMISSION_SAVINGS_INCL_EV'] = cumulative_emissions_incl_ev

     
#%%

# 6. Save adjusted framework 
df_list[0].to_csv(file_path_ref + csv_file_to_read + "_pre_em.csv", index=False)

        
for csv, num in zip(csv_file_to_read_list, number_df):
    
    if num != 0:
        df_list[num].to_csv(file_path + csv + "_pre_em.csv", index=False)
















     




