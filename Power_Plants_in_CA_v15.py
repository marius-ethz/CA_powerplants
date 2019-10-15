
######################################################################################################
########################                                                    ##########################
########################            Powerplants in CA                       ##########################
########################                                                    ##########################
######################################################################################################

#This notebook creates three different dataframes, which serve different purposes.

#First, we create the dataframe 'powerplants_ca_emitting'. This dataframe uses the existing dataset from https://www.psehealthyenergy.org/california-power-map/ that includes all emitting powerplants in California between 2010 and 2017, including their type, capacity [MW], capacity factor, and emissions per MWh electricity generated. Using this data, we analyse (i) which powerplants run how often (capacity factor) and (ii) how dirty they are (emissions per MWh). Especially the difference between the different powerplant types that use natural gas is interesting. For example, what is the difference between peaker plants and combined cycle plants.

#Second, we create the dataframe 'powerplants_ca', which - after its extension - lists all powerplants in California between 2005 and 2030, including powerplant type, capacity, capacity factors, and emission factor - all for each year. Based on this dataset we can deep dive into individual years, month, or days. This dataframe uses the existing dataset from https://ww2.energy.ca.gov/almanac/power_plant_data/ that includes all powerplants in California until 2016, including type, capacity [MW], and initial start date (so when was the powerplant running the first time). To develop a comprehensive dataset for the years 2005-2030, we extend this data as follows: 
#(i) Phase-out of Nuclear power plants: As this dataset only includes power plants that are still operational, thus it neglects pre-2016 power plant phase-outs. In California, in 2013 the first nuclear power plant 'San Onofre' was phased-out. We thus add 'San Onofre' for the years 2005-2012. Further, California announced to phase-out its second and last nuclear plant 'Diablo Canyon' in 2016. 
#(ii) Uptake of solar PV: This datasets begins to neglect solar power plants starting in 2015 (although the dataset is described as being up-to-date until end of 2016). To account for the historical installations until 2018 and future projections of solar PV diffusion in California, we add around 1700 historical-average-sized PV power plants until 2030 to the dataset. The projection of solar PV diffusion underlies two main assumptions. First, California reaches its policy goal of 60% electricity generation based on renewables excluding large hydro. Second, additional renewable capacity to reach this policy goals is mainly achieved by solar PV installations.
#(iii) Connecting with 'powerplants_ca_emitting' dataframe. Using the power plant name as a matching criteria, we add capacity factors and emission values to the powerplants in the 'powerplants_ca' dataframe. The matching percentage is xx%. That means xx% of powerplants of the power plants listed in the 'powerplants_ca_emitting' dataframe are found in the 'powerplant_ca' dataframe. The matching rate is not 100% as powerplan names are not written similarly. To achieve a 100% matching rate manual matching has to be conducted. 
#(iv) Extrapolating 2010-2017 capacity factors and emission values for emitting power plants: We add capacity factors and emission values for the remaining years (i.e., 2005-2009 & 2018-2030) based on the 2010-2017 values to the respective emitting powerplant. For explorating, we use the 2010-2017 average. 
#(v) Adding 2013-2019 capacity factor to non-emitting power plants. We add annual capacity factors from 2013-2019 for non-emitting powerplants in California provided by the EIA (Capacity Factors for Utility Scale Generators Not Primarily Using Fossil Fuels, January 2013-June 2019, link: https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_6_07_b). This data is not powerplant-specific and only provides annual capacity factors for a powerplant type such as 'solar' or 'wind'. Therefore, all non-emitting powerplants of the same type have the same capacity factor for a particular year. The capacity factors, however, can vary between the years. This is particularly true for hydro powerplants that show capacity factors between 10% and 30% between --> Is that true in our dataset? PROVE
#(vi) Extrapolating 2013-2019 capacity factors for non-emitting power plants: We add capacity factors for pre-2013 and post-2019 years based on the 2013-2019 average.
#(vii) Adding emission factors to all non-emitting powerplants: We assume that all non-emitting powerplants are carbon emission free. Thus we assign all non-emitting powerplants this value. 

#Third, we create the dataframe 'powerplants_ca_average_day'. This dataframe provides hourly data for the average day of a specific year. Applying this dataframe, we could analyse how hourly demand profiles require different powerplants to run. To define the hourly-available capacity we assume the following: 
#(i) Solar powerplants have hourly different capacity factors. We derive the hourly different capacity factors by the average capacity factor over the specific year and the PV generation profile, which indicates how the total electricity generated by a PV is spread over the day (in the sum the PV generation profile is 100% over one day). The PV generation profile is based on data by Darghouth et al. 2013. 
#(ii) low-marginal-cost powerplants - such as wind, hydro, and nuclear - provide capacity according to their max capacity times their capacity factor. High-marginal-cost powerplants, however, provide their full capacity. We do so, becauase the capacity factors of powerplants are below 100% mainly due to three factors. First, applying the merit order, their marginal costs were higher than the matching price (demand and supply). Second, downtime due to maintenance and fuel refueling. Third, lack of natural resources such as wind, sun, and water. While the former does not influence the max capacity powerplants can bid on the market, the latter two are constraints for the bid. 

#%%

import pandas as pd
import statistics 
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os 

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

matplotlib.rcdefaults()
#Plot Styles
plt.rcParams.update({'font.size': 12, 'font.family': 'Calibri'})
plt.rc('figure', titlesize=12)
plt.rc('axes', axisbelow=True)
plt.rcParams["figure.figsize"] = (20,10)

#Set working directory
os.chdir("Z:/Public/997 Collaboration/Marius Schwarz/03_VGI in California/00_Marius Schwarz/99_Python Code/01_CA_Powerplants")  


#%%

######################################################################################################
########################    Create Dataframe 'powerplants_ca_emitting'      ##########################
######################################################################################################

#First, we create the dataframe 'powerplants_ca_emitting'. This dataframe uses the existing dataset from https://www.psehealthyenergy.org/california-power-map/ that includes all emitting powerplants in California between 2010 and 2017, including their type, capacity [MW], capacity factor, and emissions per MWh electricity generated. Using this data, we analyse 
#- Which powerplants run how often (capacity factor) 
#- How dirty they are (emissions per MWh). Especially the difference between the different powerplant types that use natural gas is interesting. For example, what is the difference between peaker plants and combined cycle plants.

#We do the following dataprocessing steps:
#1. Data for emitting powerplants for the years 2010 to 2017
#2. Combine and process 2010-2017 dataframes
#3. Visualize the data



##################### Data for emitting powerplants for the years 2010 to 2017  ######################

#In a first step, we create dataframes for emitting powerplants between 2010 to 2017:
#1. Reading in files
#2. Keep only relevant columns
#3. Sort alphabetically according plant names
#4. Drop duplicates
#5. Rename Columns
#6. Set Plant names as index

#%%

# 1. Reading in files

# general file path
file_path_data = "../../06_CA Power Plants/00_Original Data/01_CA_powerplants_emitting_2010_2017/"
file_path_visualization = "../../06_CA Power Plants/01_DataVisualization/"

#read in annual power plant data from 2010-2017
years_short = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]

#%%

for x in years_short:
    globals()["powerplants_ca_emitting_" + str(x)] = pd.read_csv(file_path_data + "powerplants_ca_emitting_" + str(x) + ".csv", sep=';')

#%%
    
# 2. Keep only relevant columns

# For 2010 we also need the plant name and plant type general
years_short_2010 = [2011, 2012, 2013, 2014, 2015, 2016, 2017]

powerplants_ca_emitting_2010 = powerplants_ca_emitting_2010[['Plant name',\
                                     'Plant type general',\
                                     'Min. MW',\
                                     'Capacity factor',\
                                     'AverageCO2EmissionRate']]

for x in years_short_2010:
    globals()["powerplants_ca_emitting_" + str(x)] = \
                                     globals()["powerplants_ca_emitting_" + str(x)][[\
                                     'Plant name',
                                     'Min. MW',\
                                     'Capacity factor',
                                     'AverageCO2EmissionRate']]
    
    
#%%
    
# 3. Sort alphabetically according plant names

for x in years_short:
    globals()["powerplants_ca_emitting_" + str(x)] = \
                globals()["powerplants_ca_emitting_" + str(x)].sort_values(by=['Plant name'])

#%%
                
# 4. Drop duplicates

for x in years_short:
    globals()["powerplants_ca_emitting_" + str(x)] = \
            globals()["powerplants_ca_emitting_" + str(x)].drop_duplicates(subset='Plant name')
            
#%%
            
# 5. Rename Columns

powerplants_ca_emitting_2010 = powerplants_ca_emitting_2010.rename(columns={\
                                "Plant name": "PLANT_NAME",\
                                "AverageCO2EmissionRate": "EMISSIONS_[tCO2/MWh]",\
                                "Plant type general": "PLANT_TYPE",\
                                "Min. MW": "CAPACITY_[MW]",\
                                "Capacity factor": "CAPACITY_FACTOR"})

for x in years_short_2010:
    globals()["powerplants_ca_emitting_" + str(x)] = \
                        globals()["powerplants_ca_emitting_" + str(x)].rename(columns={\
                                "Plant name": "PLANT_NAME",\
                                "AverageCO2EmissionRate": "EMISSIONS_[tCO2/MWh]",\
                                "Min. MW": "CAPACITY_[MW]",\
                                "Capacity factor": "CAPACITY_FACTOR"})
    
#%%

# 6. Set Plant names as index

for x in years_short:
    globals()["powerplants_ca_emitting_" + str(x)].set_index('PLANT_NAME', inplace=True)
    
#%%
   
################################   Combine and process 2010-2017 dataframes ####################################
    
#In a second step, we combine the annual 2010-2017 dataframes and do some further data processing: 
#1. Join dataframes
#2. Replace wording in the dataset
#3. Delete outliers in the dataset
#4. Create plant-typ-specific dataframes for further dataprocessing
#5. Calculate mean capacities, capacity factors, and emission values 
#6. Replace missing values in dataframe with mean values
#7. Combine plant-type-specific dataframes to 'powerplants_ca_emitting'

#%%
   
# 1. join dataframes

## Create list 'years_short_2010_2017'
years_short_2010_2016_2017 = [2011, 2012, 2013, 2014, 2015,]

## 2010
powerplants_ca_emitting = powerplants_ca_emitting_2010.join(\
                 powerplants_ca_emitting_2011, lsuffix='_2010')

## 2011-2016
for x in years_short_2010_2016_2017:
    powerplants_ca_emitting = powerplants_ca_emitting.join(\
                 globals()["powerplants_ca_emitting_" + str(x + 1)], lsuffix='_' + str(x))

## 2017
powerplants_ca_emitting = powerplants_ca_emitting.join(\
                 powerplants_ca_emitting_2017, lsuffix='_2016', rsuffix='_2017')

#%%

# 2. Replace wording in the dataset

powerplants_ca_emitting.replace('Combined cycle', 'Combined_cycle', inplace = True)
powerplants_ca_emitting.replace('Once-through cooling', 'Once_through_cooling', inplace = True)
powerplants_ca_emitting.replace('Other', 'Once_through_cooling', inplace = True)

#%%

# (iii) Delete outliers in the dataset

for x in years_short:
    powerplants_ca_emitting.loc[powerplants_ca_emitting[\
                    'EMISSIONS_[tCO2/MWh]_' + str(x)] > 2, \
                    'EMISSIONS_[tCO2/MWh]_' + str(x)] = 2
    
#%%
    
# (iv) Create plant-typ-specific dataframes for further dataprocessing

## The usual way of creating an index list of powerplants that share one powerplant type ...
## ... is not working here, as fillna, inplace doesn't work with lists in .loc[]

## Create list with all powerplant types for iterating over this list
powerplants_ca_emitting_types = ['Biogas', 'Biomass', 'Cogen', 'Combined_cycle', 'Once_through_cooling', \
                    'Other', 'Peaker']

## Create new datasets for each plant type. After processing we combine these datasets
for y in powerplants_ca_emitting_types :
    globals()["powerplants_ca_emitting_" + y] = powerplants_ca_emitting.loc[\
                                powerplants_ca_emitting['PLANT_TYPE'] == y]


#%%
    
# (v) Calculate mean capacities, capacity factors, and emission values 

for y in powerplants_ca_emitting_types:
    
    capacities = []
    capacity_factors = []
    emissions = []
    
    for x in years_short:
        
        #capacities
        mean_capacity_in_year = globals()["powerplants_ca_emitting_" + y]['CAPACITY_[MW]_' + str(x)].mean()
        #capacity factors
        mean_capacity_factor_in_year = globals()["powerplants_ca_emitting_" + y]['CAPACITY_FACTOR_' + str(x)].mean()
        #emissions
        mean_emission_in_year = globals()["powerplants_ca_emitting_" + y]['EMISSIONS_[tCO2/MWh]_' + str(x)].mean()
                
        capacities.append(mean_capacity_in_year)
        capacity_factors.append(mean_capacity_factor_in_year)
        emissions.append(mean_emission_in_year)
        
    globals()[y + "_capacity"] = statistics.mean(capacities)
    globals()[y + "_capacity_factor"] = statistics.mean(capacity_factors)
    globals()[y + "_emissions"] = statistics.mean(emissions)

#%%
    
# (vi) Replace missing values in dataframe with mean values

for x in years_short:
    for y in powerplants_ca_emitting_types:
        
        # Capacity
        globals()["powerplants_ca_emitting_" + y].fillna({'CAPACITY_[MW]_' + str(x): \
                            globals()[y + '_capacity']}, inplace = True)
        
        # Capacity factor
        globals()["powerplants_ca_emitting_" + y].fillna({'CAPACITY_FACTOR_' + str(x): \
                            globals()[y + '_capacity_factor']}, inplace = True)
        
        # Emission
        globals()["powerplants_ca_emitting_" + y].fillna({'EMISSIONS_[tCO2/MWh]_' + str(x): \
                            globals()[y + '_emissions']}, inplace = True)

        
#%%

# (vii) Combine plant-type-specific dataframes to 'powerplants_ca_emitting'

## Create empty dataframe
powerplants_ca_emitting = pd.DataFrame()

### Fill empty datafram
for y in powerplants_ca_emitting_types:
    powerplants_ca_emitting = powerplants_ca_emitting.append(globals()['powerplants_ca_emitting_' + y])


#%%
    
##############################     Visualize the data ##############################################
    
#In a third step, we visualize the data. To do so we 
#1. Create Colors for Plot 
#2. Prepare annual Plot data. 

#We visualize the data in three plots:
#-  Plot I: Capacity factors over capacity
#-  Plot II: Emissions over capacity
#-  Plot III: Bubble Plot - Capacity, capacity factors, emissions, and plant type   

# (i) Create Colors for Plot

# Decide for color map
cmap = matplotlib.cm.get_cmap('Set2')

powerplants_ca_emitting_type = powerplants_ca_emitting['PLANT_TYPE']
colors = []

for x in powerplants_ca_emitting_type:
    if x == 'Biogas':
        colors.append(cmap(0.1))
    elif x == 'Biomass':
        colors.append(cmap(0.2))
    elif x == 'Cogen':
        colors.append(cmap(0.3))
    elif x == 'Combined_cycle':
        colors.append(cmap(0.4))
    elif x == 'Once_through_cooling':
        colors.append(cmap(0.5))
    elif x == 'Peaker':
        colors.append(cmap(0.7)) 
    elif x == 'Other':
        colors.append(cmap(0.9))
    else: 
        colors.append(cmap(0.9))

powerplants_ca_emitting['COLORS'] = colors

#%%

# (ii) Prepare annual Plot data

for x in years_short:
    globals()['powerplants_plot_' + str(x)] = powerplants_ca_emitting.sort_values(by=[\
                                    'CAPACITY_FACTOR_' + str(x)], ascending=False)
    
    globals()['capacity_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)][\
                                    'CAPACITY_[MW]_' + str(x)]

    globals()['capacity_factor_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)][\
                                    'CAPACITY_FACTOR_' + str(x)]
    
    globals()['emissions_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)][\
                                    'EMISSIONS_[tCO2/MWh]_' + str(x)]

    globals()['colors_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)]['COLORS']

    ## Create x_axis distance of bars for design
    globals()['x_pos_plot_' + str(x)] = []
    total = 0
    i = 0
    j = 0
    for num in globals()['capacity_plot_' + str(x)]:
        i = num / 2
        total = total + i + j
        j = num / 2
        globals()['x_pos_plot_' + str(x)].append(total)

#%%
        
# Plot I: Capacity factors over capacity
fig, axes = plt.subplots(4, 2, sharex=True, sharey=True, gridspec_kw={'hspace': 0.2, 'wspace': 0.1}, figsize=(12,8))

axes[0,0].bar(x_pos_plot_2010, capacity_factor_plot_2010, width=capacity_plot_2010, linewidth=1, color=colors_plot_2010)
axes[1,0].bar(x_pos_plot_2011, capacity_factor_plot_2011, width=capacity_plot_2011, linewidth=0, color=colors_plot_2011)
axes[2,0].bar(x_pos_plot_2012, capacity_factor_plot_2012, width=capacity_plot_2012, linewidth=0, color=colors_plot_2012)
axes[3,0].bar(x_pos_plot_2013, capacity_factor_plot_2013, width=capacity_plot_2013, linewidth=0, color=colors_plot_2013)
axes[0,1].bar(x_pos_plot_2014, capacity_factor_plot_2014, width=capacity_plot_2014, linewidth=0, color=colors_plot_2014)
axes[1,1].bar(x_pos_plot_2015, capacity_factor_plot_2015, width=capacity_plot_2015, linewidth=0, color=colors_plot_2015)
axes[2,1].bar(x_pos_plot_2016, capacity_factor_plot_2016, width=capacity_plot_2016, linewidth=0, color=colors_plot_2016)
axes[3,1].bar(x_pos_plot_2017, capacity_factor_plot_2017, width=capacity_plot_2017, linewidth=0, color=colors_plot_2017)

##### Define Plot Style
font_title = {'size':'12', 'color':'black', 'weight':'bold',
              'verticalalignment':'bottom'}
font_axis = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
font_subtitle = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}

tick_label_size = 12


axes[0,0].set_title('2010', **font_subtitle, y=0.7)
axes[0,0].yaxis.grid(True)
axes[0,0].set_xlim([0,40000])
axes[0,0].set_ylim([0,1])
axes[0,0].tick_params(axis="y", labelsize=tick_label_size)
axes[0,0].tick_params(axis="x", labelsize=tick_label_size)

axes[1,0].set_title('2011', **font_subtitle, y=0.7)
axes[1,0].yaxis.grid(True)
axes[1,0].set_xlim([0,40000])
axes[1,0].set_ylim([0,1])
axes[1,0].tick_params(axis="y", labelsize=tick_label_size)
axes[1,0].tick_params(axis="x", labelsize=tick_label_size)

axes[2,0].set_title('2012', **font_subtitle, y=0.7)
axes[2,0].yaxis.grid(True)
axes[2,0].set_xlim([0,40000])
axes[2,0].set_ylim([0,1])
axes[2,0].tick_params(axis="y", labelsize=tick_label_size)
axes[2,0].tick_params(axis="x", labelsize=tick_label_size)

axes[3,0].set_title('2013', **font_subtitle, y=0.7)
axes[3,0].yaxis.grid(True)
axes[3,0].set_xlim([0,40000])
axes[3,0].set_ylim([0,1])
axes[3,0].tick_params(axis="y", labelsize=tick_label_size)
axes[3,0].tick_params(axis="x", labelsize=tick_label_size)

axes[0,1].set_title('2014', **font_subtitle, y=0.7)
axes[0,1].yaxis.grid(True)
axes[0,1].set_xlim([0,40000])
axes[0,1].set_ylim([0,1])
axes[0,1].tick_params(axis="y", labelsize=tick_label_size)
axes[0,1].tick_params(axis="x", labelsize=tick_label_size)

axes[1,1].set_title('2015', **font_subtitle, y=0.7)
axes[1,1].yaxis.grid(True)
axes[1,1].set_xlim([0,40000])
axes[1,1].set_ylim([0,1])
axes[1,1].tick_params(axis="y", labelsize=tick_label_size)
axes[1,1].tick_params(axis="x", labelsize=tick_label_size)

axes[2,1].set_title('2016', **font_subtitle, y=0.7)
axes[2,1].yaxis.grid(True)
axes[2,1].set_xlim([0,40000])
axes[2,1].set_ylim([0,1])
axes[2,1].tick_params(axis="y", labelsize=tick_label_size)
axes[2,1].tick_params(axis="x", labelsize=tick_label_size)

axes[3,1].set_title('2017', **font_subtitle, y=0.7)
axes[3,1].yaxis.grid(True)
axes[3,1].set_xlim([0,40000])
axes[3,1].set_ylim([0,1])
axes[3,1].tick_params(axis="y", labelsize=tick_label_size)
axes[3,1].tick_params(axis="x", labelsize=tick_label_size)

#Creating the legend
cmap = matplotlib.cm.get_cmap('Set2')
legend_elements = [Line2D([0], [0], color=cmap(0.1), lw=4, label='Biogas'),\
                   Line2D([0], [0], color=cmap(0.2), lw=4, label='Biomass'),\
                   Line2D([0], [0], color=cmap(0.3), lw=4, label='Cogen'),\
                   Line2D([0], [0], color=cmap(0.4), lw=4, label='Combined Cycle'),\
                   Line2D([0], [0], color=cmap(0.5), lw=4, label='Once-through cooling'),\
                   Line2D([0], [0], color=cmap(0.7), lw=4, label='Peaker'),\
                   Line2D([0], [0], color=cmap(0.9), lw=4, label='Other')]

plt.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(-0.1, -1), ncol=7,  frameon=False)

# Axis labels
fig.suptitle("Power Plants in California - Capacity factor over capacity", **font_title, y=0.92)
fig.text(0.5, 0.03, 'Capacity [MW]', ha='center', va='center', **font_axis)
fig.text(0.07, 0.4, 'Capacity Factor', ha='center', va='center', rotation='vertical', **font_axis)

#Plotting
plt.savefig(file_path_visualization + 'Emitting Power Plants in California - Capacity Factor and Capacity.png', bbox_inches='tight')
plt.show()

#%%

# Plot II: Emissions over capacity

fig, axes = plt.subplots(4, 2, sharex=True, sharey=True, gridspec_kw={'hspace': 0.2, 'wspace': 0.1}, figsize=(12,8))

axes[0,0].bar(x_pos_plot_2010, emissions_plot_2010, width=capacity_plot_2010, linewidth=0, color=colors_plot_2010)
axes[1,0].bar(x_pos_plot_2011, emissions_plot_2011, width=capacity_plot_2011, linewidth=0, color=colors_plot_2011)
axes[2,0].bar(x_pos_plot_2012, emissions_plot_2012, width=capacity_plot_2012, linewidth=0, color=colors_plot_2012)
axes[3,0].bar(x_pos_plot_2013, emissions_plot_2013, width=capacity_plot_2013, linewidth=0, color=colors_plot_2013)
axes[0,1].bar(x_pos_plot_2014, emissions_plot_2014, width=capacity_plot_2014, linewidth=0, color=colors_plot_2014)
axes[1,1].bar(x_pos_plot_2015, emissions_plot_2015, width=capacity_plot_2015, linewidth=0, color=colors_plot_2015)
axes[2,1].bar(x_pos_plot_2016, emissions_plot_2016, width=capacity_plot_2016, linewidth=0, color=colors_plot_2016)
axes[3,1].bar(x_pos_plot_2017, emissions_plot_2017, width=capacity_plot_2017, linewidth=0, color=colors_plot_2017)

##### Define Plot Style
font_title = {'size':'12', 'color':'black', 'weight':'bold',
              'verticalalignment':'bottom'}
font_axis = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
font_subtitle = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}

tick_label_size = 12


axes[0,0].set_title('2010', **font_subtitle, y=0.7)
axes[0,0].yaxis.grid(True)
axes[0,0].set_xlim([0,40000])
axes[0,0].set_ylim([0,2])
axes[0,0].tick_params(axis="y", labelsize=tick_label_size)
axes[0,0].tick_params(axis="x", labelsize=tick_label_size)

axes[1,0].set_title('2011', **font_subtitle, y=0.7)
axes[1,0].yaxis.grid(True)
axes[1,0].set_xlim([0,40000])
axes[1,0].set_ylim([0,2])
axes[1,0].tick_params(axis="y", labelsize=tick_label_size)
axes[1,0].tick_params(axis="x", labelsize=tick_label_size)

axes[2,0].set_title('2012', **font_subtitle, y=0.7)
axes[2,0].yaxis.grid(True)
axes[2,0].set_xlim([0,40000])
axes[2,0].set_ylim([0,2])
axes[2,0].tick_params(axis="y", labelsize=tick_label_size)
axes[2,0].tick_params(axis="x", labelsize=tick_label_size)

axes[3,0].set_title('2013', **font_subtitle, y=0.7)
axes[3,0].yaxis.grid(True)
axes[3,0].set_xlim([0,40000])
axes[3,0].set_ylim([0,2])
axes[3,0].tick_params(axis="y", labelsize=tick_label_size)
axes[3,0].tick_params(axis="x", labelsize=tick_label_size)

axes[0,1].set_title('2014', **font_subtitle, y=0.7)
axes[0,1].yaxis.grid(True)
axes[0,1].set_xlim([0,40000])
axes[0,1].set_ylim([0,2])
axes[0,1].tick_params(axis="y", labelsize=tick_label_size)
axes[0,1].tick_params(axis="x", labelsize=tick_label_size)

axes[1,1].set_title('2015', **font_subtitle, y=0.7)
axes[1,1].yaxis.grid(True)
axes[1,1].set_xlim([0,40000])
axes[1,1].set_ylim([0,2])
axes[1,1].tick_params(axis="y", labelsize=tick_label_size)
axes[1,1].tick_params(axis="x", labelsize=tick_label_size)

axes[2,1].set_title('2016', **font_subtitle, y=0.7)
axes[2,1].yaxis.grid(True)
axes[2,1].set_xlim([0,40000])
axes[2,1].set_ylim([0,2])
axes[2,1].tick_params(axis="y", labelsize=tick_label_size)
axes[2,1].tick_params(axis="x", labelsize=tick_label_size)

axes[3,1].set_title('2017', **font_subtitle, y=0.7)
axes[3,1].yaxis.grid(True)
axes[3,1].set_xlim([0,40000])
axes[3,1].set_ylim([0,2])
axes[3,1].tick_params(axis="y", labelsize=tick_label_size)
axes[3,1].tick_params(axis="x", labelsize=tick_label_size)

#Creating the legend
cmap = matplotlib.cm.get_cmap('Set2')
legend_elements = [Line2D([0], [0], color=cmap(0.1), lw=4, label='Biogas'),\
                   Line2D([0], [0], color=cmap(0.2), lw=4, label='Biomass'),\
                   Line2D([0], [0], color=cmap(0.3), lw=4, label='Cogen'),\
                   Line2D([0], [0], color=cmap(0.4), lw=4, label='Combined Cycle'),\
                   Line2D([0], [0], color=cmap(0.5), lw=4, label='Once-through cooling'),\
                   Line2D([0], [0], color=cmap(0.7), lw=4, label='Peaker'),\
                   Line2D([0], [0], color=cmap(0.9), lw=4, label='Other')]

plt.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(-0.1, -1), ncol=7, frameon=False)

# Axis labels
fig.suptitle("Power Plants in California - Emissions and Capacity", **font_title, y=0.92)
fig.text(0.51, 0.03, 'Capacity [MW]', ha='center', va='center', **font_axis)
fig.text(0.08, 0.4, 'Emissions [tCO2 / MWh]', ha='center', va='center', rotation='vertical', **font_axis)

#Plotting
plt.savefig(file_path_visualization + 'Emitting Power Plants in California - Emissions over capacity.png', bbox_inches='tight')
plt.show()

#%%

# Plot III: Bubble Plot - Capacity, capacity factors, emissions, and plant type

fig, axes = plt.subplots(2, 2, sharex=True, sharey=True, figsize=(12,8))

##### Define Plot Style
font_title = {'size':'12', 'color':'black', 'weight':'bold',
              'verticalalignment':'bottom'}
font_axis = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
font_subtitle = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
tick_label_size = 12

##### Define Plot Content
axes[0,0].scatter(capacity_factor_plot_2010, emissions_plot_2010, s=capacity_plot_2010, \
            c=colors_plot_2010,alpha=0.5)
axes[0,1].scatter(capacity_factor_plot_2012, emissions_plot_2012, s=capacity_plot_2012, \
            c=colors_plot_2012,alpha=0.5)
axes[1,0].scatter(capacity_factor_plot_2015, emissions_plot_2015, s=capacity_plot_2015, \
            c=colors_plot_2015,alpha=0.5)
axes[1,1].scatter(capacity_factor_plot_2017, emissions_plot_2017, s=capacity_plot_2017, \
            c=colors_plot_2017,alpha=0.5)

# Add titles (main and on axis)
axes[0,0].set_title('2010', **font_subtitle)
axes[0,0].yaxis.grid(True)
axes[0,0].xaxis.grid(True)
axes[0,0].set_xlim([0,1])
axes[0,0].set_ylim([0,2])
axes[0,0].tick_params(axis="y", labelsize=tick_label_size)
axes[0,0].tick_params(axis="x", labelsize=tick_label_size)

axes[0,1].set_title('2012', **font_subtitle)
axes[0,1].yaxis.grid(True)
axes[0,1].xaxis.grid(True)
axes[0,1].set_xlim([0,1])
axes[0,1].set_ylim([0,2])
axes[0,1].tick_params(axis="y", labelsize=tick_label_size)
axes[0,1].tick_params(axis="x", labelsize=tick_label_size)

axes[1,0].set_title('2015', **font_subtitle)
axes[1,0].yaxis.grid(True)
axes[1,0].xaxis.grid(True)
axes[1,0].set_xlim([0,1])
axes[1,0].set_ylim([0,2])
axes[1,0].tick_params(axis="y", labelsize=tick_label_size)
axes[1,0].tick_params(axis="x", labelsize=tick_label_size)

axes[1,1].set_title('2017', **font_subtitle)
axes[1,1].yaxis.grid(True)
axes[1,1].xaxis.grid(True)
axes[1,1].set_xlim([0,1])
axes[1,1].set_ylim([0,2])
axes[1,1].tick_params(axis="y", labelsize=tick_label_size)
axes[1,1].tick_params(axis="x", labelsize=tick_label_size)

############  Legend
## Legend 1
legend_elements = [Line2D([0], [0], color=cmap(0.1), lw=4, label='Biogas'),\
                   Line2D([0], [0], color=cmap(0.2), lw=4, label='Biomass'),\
                   Line2D([0], [0], color=cmap(0.3), lw=4, label='Cogen'),\
                   Line2D([0], [0], color=cmap(0.4), lw=4, label='Combined Cycle'),\
                   Line2D([0], [0], color=cmap(0.5), lw=4, label='Once-through cooling'),\
                   Line2D([0], [0], color=cmap(0.7), lw=4, label='Peaker'),\
                   Line2D([0], [0], color=cmap(0.9), lw=4, label='Other')]

legend1 = plt.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(-0.2, -0.28), ncol=7, frameon=False)
ax = plt.gca().add_artist(legend1)

## Legend 2
area= 500
plot_legend = plt.scatter([], [], c='grey', alpha=0.5, edgecolors='none', s=area, label=str(area) + ' [MW]')

legend2 = plt.legend(handles=[plot_legend], loc='upper left', ncol=3, bbox_to_anchor=(0.6, 1), \
                     handletextpad=0.8, scatterpoints=1, frameon=True, labelspacing=1, edgecolor='none', \
                     facecolor='white', framealpha=0.8, title='Powerplant Capacity')

legend2._legend_box.align = 'left'


######### Titles 
fig.suptitle("Power Plants in California", **font_title, y=0.92)
fig.text(0.5, 0.01, 'Capacity Factor [%]', ha='center', va='center', **font_axis)
fig.text(0.08, 0.4, 'Emissions [tCO2/MWh]', ha='center', va='center', rotation='vertical', **font_axis)

#Plot
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.2, hspace=0.2)
plt.savefig(file_path_visualization + 'Emitting Power Plants in California - Bubble Plot.pdf', bbox_inches='tight')
plt.show()

#%%

######################################################################################################
########################    Create Dataframe 'powerplants_ca_emitting'      ##########################
######################################################################################################

#Second, we create the dataframe 'powerplants_ca', which - after its extension - lists all powerplants in California between 2005 and 2030, including powerplant type, capacity, capacity factors, and emission factor - all for each year. Based on this dataset we can deep dive into individual years, month, or days. This dataframe uses the existing dataset from https://ww2.energy.ca.gov/almanac/power_plant_data/ that includes all powerplants in California until 2016, including type, capacity [MW], and initial start date (so when was the powerplant running the first time). To develop a comprehensive dataset for the years 2005-2030, we extend this data as follows: 

#1. First data cleaning and processing
#- Phase-out of Nuclear power plants: As this dataset only includes power plants that are still operational, thus it neglects pre-2016 power plant phase-outs. In California, in 2013 the first nuclear power plant 'San Onofre' was phased-out. We thus add 'San Onofre' for the years 2005-2012. Further, California announced to phase-out its second and last nuclear plant 'Diablo Canyon' in 2016. 
#- Uptake of solar PV: This datasets begins to neglect solar power plants starting in 2015 (although the dataset is described as being up-to-date until end of 2016). To account for the historical installations until 2018 and future projections of solar PV diffusion in California, we add around 1700 historical-average-sized PV power plants until 2030 to the dataset. The projection of solar PV diffusion underlies two main assumptions. First, California reaches its policy goal of 60% electricity generation based on renewables excluding large hydro. Second, additional renewable capacity to reach this policy goals is mainly achieved by solar PV installations. 
#- Connecting with 'powerplants_ca_emitting' dataframe: Using the power plant name as a matching criteria, we add capacity factors and emission values to the powerplants in the 'powerplants_ca' dataframe. The matching percentage is xx%. That means xx% of powerplants of the power plants listed in the 'powerplants_ca_emitting' dataframe are found in the 'powerplant_ca' dataframe. The matching rate is not 100% as powerplan names are not written similarly. To achieve a 100% matching rate manual matching has to be conducted. 
#- Extrapolating 2010-2017 capacity factors and emission values for emitting power plants: We add capacity factors and emission values for the remaining years (i.e., 2005-2009 & 2018-2030) based on the 2010-2017 values to the respective emitting powerplant. For explorating, we use the 2010-2017 average. 
#- Adding 2013-2019 capacity factor to non-emitting power plants. We add annual capacity factors from 2013-2019 for non-emitting powerplants in California provided by the EIA (Capacity Factors for Utility Scale Generators Not Primarily Using Fossil Fuels, January 2013-June 2019, link: https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_6_07_b). This data is not powerplant-specific and only provides annual capacity factors for a powerplant type such as 'solar' or 'wind'. Therefore, all non-emitting powerplants of the same type have the same capacity factor for a particular year. The capacity factors, however, can vary between the years. This is particularly true for hydro powerplants that show capacity factors between 10% and 30% between --> Is that true in our dataset? PROVE 
#- Extrapolating 2013-2019 capacity factors for non-emitting power plants: We add capacity factors for pre-2013 and post-2019 years based on the 2013-2019 average. 
#- Adding emission factors to all non-emitting powerplants: We assume that all non-emitting powerplants are carbon emission free. Thus we assign all non-emitting powerplants this value.

#%%

##########################      First data cleaning and processing       ##############################

#For a first data cleaning and processing, we need to
#1. Read in files
#2. Keep columns that we need for further analysis
#3. Reduce amount of plant types
#4. Rename columns
#5. Set up columns for years 2005-2030

#%%

# 1. Read in files

# general path file
file_path_data = "../../06_CA Power Plants/00_Original Data/02_CA_powerplants_until_2016/"

powerplants_ca = pd.read_csv(file_path_data + "Overview Power Plants in CA_ until 2016.csv", sep=';', encoding = 'unicode_escape')

#%%

# 2. Keep columns that we need for further analysis

powerplants_ca = powerplants_ca[['Plant Name','General Fuel','MW','Initial Start Date']]

#%%

# 3. Reduce amount of plant types

powerplants_ca.replace('Landfill Gas', 'Biomass', inplace = True)
powerplants_ca.replace('MSW', 'Biomass', inplace = True)
powerplants_ca.replace('Digester Gas', 'Gas_undefined', inplace = True)
powerplants_ca.replace('Other', 'Gas_undefined', inplace = True)

#%%

# 4.  Rename columns

powerplants_ca = powerplants_ca.rename(columns={"Plant Name": "PLANT_NAME",\
                                "General Fuel": "PLANT_TYPE",\
                                "MW": "CAPACITY_[MW]",\
                                "Initial Start Date": "INITIAL_START_DATE"}).set_index('PLANT_NAME')
    
#%%
    
# 5. Set up columns for years 2005-2030

years_long = [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,\
              2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]

# Create new columns
add_columns = []

for x in years_long:
    add_columns.append('CAPACITY_[MW]_' + str(x))

# Add new columns to dataframe
powerplants_ca = powerplants_ca.reindex(columns = powerplants_ca.columns.tolist() + add_columns)

#%%

##########################      Uptake of solar PV       ##############################
 
#This datasets begins to neglect solar power plants starting in 2015 (although the dataset is described as being up-to-date until end of 2016). To account for the historical installations until 2018 and future projections of solar PV diffusion in California, we add around 1700 historical-average-sized PV power plants until 2030 to the dataset. The projection of solar PV diffusion underlies two main assumptions. First, California reaches its policy goal of 60% electricity generation based on renewables excluding large hydro. Second, additional renewable capacity to reach this policy goals is mainly achieved by solar PV installations. We extend the dataset as follows:
#1. Read in historical and projected solar PV diffusion
#2. Calculate difference to capacity in dataframe 'powerplant_ca'
#3. Add new solar powerplants to the dataframe 'powerplant_ca'

#%%

# 1. Read in historical and projected solar PV diffusion

file_path_add_data = "../../06_CA Power Plants/00_Original Data/05_Solar_capacity_installations/"

solar_capacity_installations_2015_2030 = pd.read_csv(file_path_add_data + "Solar_Capacity_Installations_2015_2030.csv", \
                            sep=';', encoding = 'unicode_escape')

solar_capacity_installations_2015_2030 = solar_capacity_installations_2015_2030.set_index(\
                                                    'Unnamed: 0').rename_axis('')

#%%

# 2. Calculate difference to capacity in dataframe 'powerplant_ca'
solar_capacity_difference = pd.Series([])
solar_capacity_difference.name = 'New Capacity'
solar_capacity_installations_2015_2030 = solar_capacity_installations_2015_2030.append(solar_capacity_difference)

years_solar_diffusion = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, \
                         2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030] 

for x in years_solar_diffusion:
    
    # Check for 2015 because its the first year the data is not comprehensive
    if  x == 2015: 
        capacity_this_year = solar_capacity_installations_2015_2030.loc[\
                                            'Solar Capacity', '2015']
        capacity_last_year = powerplants_ca.groupby('PLANT_TYPE').sum().loc[\
                                           'Solar','CAPACITY_[MW]']
    else:
        capacity_this_year = solar_capacity_installations_2015_2030.loc['Solar Capacity', str(x)]
        capacity_last_year = solar_capacity_installations_2015_2030.loc['Solar Capacity', str(x - 1)]
    
    capacity_difference = capacity_this_year - capacity_last_year
    solar_capacity_installations_2015_2030.loc['New Capacity', str(x)] = capacity_difference

#%%
    
# 3. Add new solar powerplants to the dataframe 'powerplant_ca'
solar_plant = pd.Series()
solar_plants = pd.DataFrame(columns={'CAPACITY_[MW]','PLANT_TYPE','INITIAL_START_DATE'})
solar_plant_names = []
plant_number = 1

# Average existing PV sizes
average_pv_size = powerplants_ca.groupby('PLANT_TYPE').mean().loc['Solar','CAPACITY_[MW]']

# Create new solar powerplants
for x in years_solar_diffusion:
    
    counter = solar_capacity_installations_2015_2030.loc['New Capacity', str(x)]
    
    while counter > average_pv_size:
        # create series with name
        solar_plant.name = 'solar_new_' + str(plant_number)
        # add series to dataframe
        solar_plants = solar_plants.append(solar_plant)
        solar_plants.loc['solar_new_' + str(plant_number), 'CAPACITY_[MW]'] = average_pv_size
        solar_plants.loc['solar_new_' + str(plant_number), 'PLANT_TYPE'] = 'Solar'
        solar_plants.loc['solar_new_' + str(plant_number), 'INITIAL_START_DATE'] = x
        
        # set counter
        counter = counter - average_pv_size
        plant_number = plant_number + 1

# Add powerplants to the dataframe 'powerplants_ca'
powerplants_ca = powerplants_ca.append(solar_plants) #, sort=False

#%%

######################    'Building' powerplant capacity after initial start date    ######################

for x in years_long:
    
    # Indexing powerplants that have been build before that particular year
    powerplants_active = powerplants_ca[powerplants_ca.loc[:, 'INITIAL_START_DATE'] <= x].index
    
    powerplants_ca.loc[powerplants_active, 'CAPACITY_[MW]_' + str(x)] = \
                            powerplants_ca.loc[powerplants_active, 'CAPACITY_[MW]']

#%%
                            
####################     Phase-out of Nuclear power plants    ############################

#As this dataset only includes power plants that are still operational, thus it neglects pre-2016 power plant phase-outs. In California, in 2013 the first nuclear power plant 'San Onofre' was phased-out. We thus add 'San Onofre' for the years 2005-2012. Further, California announced to phase-out its second and last nuclear plant 'Diablo Canyon' in 2016. We extend the dataset as follows:
#1. Nuclear Phase-out in 2026
#2. Nuclear Phase-out in 2013                            

#%%
                            
# 1. Nuclear Phase-out in 2026

years_nuclear_phaseout = [2026, 2027, 2028, 2029, 2030]

for x in years_nuclear_phaseout:
    powerplants_ca.loc['Diablo Canyon', 'CAPACITY_[MW]_' + str(x)] = 0

#%%
    
# 2. Nuclear Phase-out in 2012

## Nuclear phase-out already started in 2013
## We have to add a nuclear power plant before that time
## Size of the phased-out plant: 2063 MW
## Name of the phased-out plant: San Onofre

year_of_nuclear_phaseout = 2012
nuclear_plant_name = 'San Onofre'
nuclear_plant_size = 2063

# Create new power plant with index = name
nuclear_plant = pd.Series([])
nuclear_plant.name = nuclear_plant_name
powerplants_ca = powerplants_ca.append(nuclear_plant)

# Fill Capacity, Type, and initial start year
powerplants_ca.loc['San Onofre', 'CAPACITY_[MW]'] = nuclear_plant_size
powerplants_ca.loc['San Onofre', 'PLANT_TYPE'] = 'Nuclear'
powerplants_ca.loc['San Onofre', 'INITIAL_START_DATE'] = 1900

for x in years_long:
    
    if x < year_of_nuclear_phaseout:
        powerplants_ca.loc['San Onofre', 'CAPACITY_[MW]_' + str(x)] = nuclear_plant_size
    
    else:
        powerplants_ca.loc['San Onofre', 'CAPACITY_[MW]_' + str(x)] = 0
        
#%%
        
###########      Connecting with 'powerplants_ca_emitting' dataframe     ################
        
#Using the power plant name as a matching criteria, we add capacity factors and emission values to the powerplants in the 'powerplants_ca' dataframe. The matching percentage is xx%. That means 79% of powerplants of the power plants listed in the 'powerplants_ca_emitting' dataframe are found in the 'powerplant_ca' dataframe. The matching rate is not 100% as smaller powerplants are not listed in the dataframe 'powerplants_ca_emitting'. To match both dataframes we do the following adjustments:
#1. Create a new dataframe 'powerplants_ca_emitting_2015_20130' 
#- Add columns for 2005 - 2030
#- Matching 
#- Checking matching rate
#- Adding powerplant type details to 'PLANT_TYPE'
#- Adding powerplant type details to unmatched power plants
#    - Calculate capacity difference for all plant types
#    - Assign powerplants to types according the unmatched capacity
#    - Replace all remaining unmatched gas powerplants to 'gas_undefined'
        
#%%
        
# 1. Create a new dataframe 'powerplants_ca_emitting_2015_20130' 
powerplants_ca_emitting_2015_2030 = powerplants_ca_emitting

#%%

# 2. Add columns for 2005 - 2030
# Rename 'PLANT_TYPE'
powerplants_ca_emitting_2015_2030 = powerplants_ca_emitting_2015_2030.rename(columns={\
                                "PLANT_TYPE": "PLANT_TYPE_DETAILED",})
add_columns = []
add_columns.append('PLANT_TYPE_DETAILED')

for x in years_long:
    add_columns.append('CAPACITY_FACTOR_' + str(x))
    
for x in years_long:
    add_columns.append('EMISSIONS_[tCO2/MWh]_' + str(x))

powerplants_ca_emitting_2015_2030 = powerplants_ca_emitting_2015_2030.reindex(columns = add_columns)

#%%

# 3. Matching 
powerplants_ca = powerplants_ca.join(powerplants_ca_emitting_2015_2030)

#%%

# 4. Check matching rate

print("#####################  MATCHING RATE   ##################")
print("")

index_gas = powerplants_ca.loc[powerplants_ca['PLANT_TYPE'] == 'Gas'].index
capacity_gas = powerplants_ca.loc[index_gas,'CAPACITY_[MW]'].sum()
number_gas = powerplants_ca.loc[index_gas,'CAPACITY_[MW]'].count()

print("Capacity of gas powerplants in 'powerplants_ca' dataframe: ", \
      capacity_gas)
print("Number of gas powerplants in 'powerplants_ca' dataframe: ", \
      number_gas)

print("")

#%%
number_gas_em = len(powerplants_ca_emitting_2015_2030['PLANT_TYPE_DETAILED'])


#%%
#Capacity of gas powerplants that matched
index_na = powerplants_ca.loc[powerplants_ca['PLANT_TYPE_DETAILED'].isnull() == False].index
capacity_match = powerplants_ca.loc[index_na,'CAPACITY_[MW]'].sum()
# Number of gas powerplants that matched
number_match = powerplants_ca.loc[index_na,'CAPACITY_[MW]'].count()


print("Capacity of gas powerplants that matched: ", \
      capacity_match)
print("Number of gas powerplants that matched: ", \
      number_match)

print("")

print("Share of gas powerplants that matched, in capacity: ", \
      capacity_match / capacity_gas)

print("Share of gas powerplants that matched, in number of plants: ", \
      number_match / number_gas)

print("Share of gas powerplants were allocated, in number of plants: ", \
      number_match / number_gas_em)

#%%

# 5. Adding powerplant type details to 'PLANT_TYPE'
powerplants_ca_gas = powerplants_ca.loc[((powerplants_ca.loc[:,'PLANT_TYPE'] == 'Gas') |
                                     (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Biogas')) & \
                                    (powerplants_ca.loc[:,'PLANT_TYPE_DETAILED'].isnull() == False)].index

powerplants_ca.loc[powerplants_ca_gas,'PLANT_TYPE'] = \
                     powerplants_ca.loc[powerplants_ca_gas,'PLANT_TYPE_DETAILED']

#%%

# 6. Adding powerplant type details to unmatched power plants
                     
# 6a. Calculate capacity difference for all plant_types
for y in powerplants_ca_emitting_types:
    
    capacity_matched = powerplants_ca[powerplants_ca.loc[\
                                :, 'PLANT_TYPE'] == y]['CAPACITY_[MW]'].sum()
    
    capacity_total = powerplants_ca_emitting[powerplants_ca_emitting.loc[\
                                :, 'PLANT_TYPE'] == y]['CAPACITY_[MW]_2010'].sum()
    
    globals()['capacity_unmatched_' + str(y)] = max(0, capacity_total - capacity_matched)

#%%
    
# 6b. Assign powerplants to types according the unmatched_capacity
# Set counter for rows in dataset
i = 0
for y in powerplants_ca_emitting_types:
    
    # Set counter for 
    counter = globals()['capacity_unmatched_' + str(y)]
    # Change plant types
    while counter > 0:
    
        # change plant type only when typs is gas
        if (powerplants_ca.iloc[i, 28] == 'Gas'):
            powerplants_ca.iloc[i, 28] = y
            
            #decrease counter by capacity of the adjusted powerplant
            adjusted_powerplant_capacity = powerplants_ca.iloc[i, 1]
            counter = counter - adjusted_powerplant_capacity
            
        else:
            i = i + 1

#%%
            
# 6c. Replace all remaining unmatched gas powerplants to gas_undefined
powerplants_ca.replace('Gas', 'Gas_undefined', inplace = True)
            
#%%

#############################     Adding capacity factors and emissions values for emitting power plants   ######################

#So far, in the dataframe, not all powerplants have capacity factors for all years. This is due to two reasons:

#First, the dataframe "powerplants_ca_emitting" only included capacity factors and emission values for the years 2010-2017, pre-2010 and post-2017, we have to add values.
#Second, through the matching process, we add capacity factors and emission values to the powerplants that matched between the two datasets. However, as we show in the matching rate, only around 80% of the capacity and 50% of the powerplants could be matched. In the dataframe 'powerplants', the remaining 50% of emitting powerplants have no assigned capacity factor or emission value. There are two categories of "unmatched plants" to which we allocate capacity factors and emission values. 
#The first category are powerplants that we allocated a specific plant type due to the capacity differences of power plant types (see 2.4). 
#The second category are powerplants with the plant_type == gas_undefined 

#We add capacity factors and emission values to these powerplants as follows:

#1. Add pre-2010 capacity factors and emission values to emitting poer plants based on the 2010 values
#- Add post-2017 capacity factors and emission values to emitting power plants based on the 2016 values
#- Adjust list "powerplants_ca_emitting_types" for "gas_undefined"
#- Calculate annual mean capacity factor and emission values for different emitting power plant type
#- Fill nan capacity factors and emission values with the plant type averages

#%%

# 1. Add pre-2010 capacity factors and emission values to emitting power plants based on the 2010 values

#  Create list with years before 2010
years_start = [2005, 2006, 2007, 2008, 2009]

#(ii) Iterate through the list and set capacity factor and emission values

for x in years_start:
    
    fill_capacity_na = powerplants_ca[\
                          (powerplants_ca.loc[:,'INITIAL_START_DATE'] <= x) & \
                          (powerplants_ca.loc[:,'CAPACITY_FACTOR_' + str(x)].isnull() == True)\
                           ].index
    
    fill_emissions_na = powerplants_ca[\
                          (powerplants_ca.loc[:,'INITIAL_START_DATE'] <= x) & \
                          (powerplants_ca.loc[:,'EMISSIONS_[tCO2/MWh]_' + str(x)].isnull() == True)\
                           ].index    
    
    powerplants_ca.loc[fill_capacity_na, "CAPACITY_FACTOR_" + str(x)] = \
                        powerplants_ca.loc[fill_capacity_na, "CAPACITY_FACTOR_2010"]
    
    powerplants_ca.loc[fill_emissions_na, "EMISSIONS_[tCO2/MWh]_" + str(x)] = \
                 powerplants_ca.loc[fill_emissions_na, "EMISSIONS_[tCO2/MWh]_2010"]

#%%
                 
# 2. Add post-2017 capacity factors and emission values to emitting power plants based on the 2016 values
years_end = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]

for x in years_end:
    powerplants_ca['CAPACITY_FACTOR_' + str(x)] = powerplants_ca['CAPACITY_FACTOR_2016']
    powerplants_ca['EMISSIONS_[tCO2/MWh]_' + str(x)] = powerplants_ca['EMISSIONS_[tCO2/MWh]_2016']
       
#%%
    
# 3. Create list with all powerplants types in dataset
powerplants_ca_types = ['Biogas',\
                        'Biomass',\
                        'Coal',\
                        'Cogen',\
                        'Combined_cycle',\
                        'Geothermal',\
                        'Hydro',\
                        'Once_through_cooling',\
                        'Peaker',\
                        'Solar',\
                        'Solar Thermal',\
                        'Wind',\
                        'Gas_undefined']

#%%

# 4. Calculate annual mean capacity factor and emission values for different emitting power plant type
for y in powerplants_ca_types:
    
    # index of powerplants of different types
    globals()['powerplants_ca_' + str(y)] = powerplants_ca[powerplants_ca.loc[\
                                               :, 'PLANT_TYPE'] == y].index
    
    for x in years_long:
        
        # Calculate annual mean capacity factor for each emitting powerplant type
        globals()[str(y) + '_mean_capacity_factor_' + str(x)] = powerplants_ca.loc[\
                    globals()['powerplants_ca_' + str(y)],'CAPACITY_FACTOR_' + str(x)].mean()
    
        # Calculate annual mean emission values for each emitting powerplant type
        globals()[str(y) + '_mean_emissions_' + str(x)] = powerplants_ca.loc[\
                    globals()['powerplants_ca_' + str(y)],'EMISSIONS_[tCO2/MWh]_' + str(x)].mean()
    
        # check for 'Biogas' as emitting but not match for this type
        average_capacity_biogas = 0.51333 # This is based on 2010 powerplants_ca_emitting_2010 dataframe
    
        if y == 'Biogas':
            globals()['Biogas_mean_capacity_factor_' + str(x)] = average_capacity_biogas
            globals()['Biogas_mean_emissions_' + str(x)] = 0
            
#%%
            
# 5. Fill nan capacity factors and emission values with the plant type averages

for x in years_long:
    
    for y in powerplants_ca_types:    
        
        ## Capacity factor
        # index of powerplants of different types with nan capacity factor 
        no_capacity_factor = powerplants_ca[\
                            (powerplants_ca.loc[:, 'PLANT_TYPE'] == y) & \
                            (powerplants_ca.loc[:, 'CAPACITY_FACTOR_' + str(x)].isnull() == True) & \
                            (powerplants_ca.loc[:,'INITIAL_START_DATE'] <= x)\
                            ].index
        
        # Set mean capacity factors
        powerplants_ca.loc[no_capacity_factor, 'CAPACITY_FACTOR_' + str(x)] = \
                        globals()[str(y) + '_mean_capacity_factor_' + str(x)]
        
        
        ## Emissions
        # index of powerplants of different types with nan capacity factor 
        no_emissions = powerplants_ca[\
                        (powerplants_ca.loc[:, 'PLANT_TYPE'] == y) & \
                        (powerplants_ca.loc[:, 'EMISSIONS_[tCO2/MWh]_' + str(x)].isnull() == True) & \
                        (powerplants_ca.loc[:,'INITIAL_START_DATE'] <= x)\
                        ].index
        
        # Set mean capacity factors
        powerplants_ca.loc[no_emissions, 'EMISSIONS_[tCO2/MWh]_' + str(x)] = \
                        globals()[str(y) + '_mean_emissions_' + str(x)]

#%%
                        
##########            Adding capacity factor and emission values to non-emitting power plants         ############################
                        
#We add annual capacity factors from 2013-2019 for non-emitting powerplants in California provided by the EIA (Capacity Factors for Utility Scale Generators Not Primarily Using Fossil Fuels, January 2013-June 2019, link: https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_6_07_b). This data is not powerplant-specific and only provides annual capacity factors for a powerplant type such as 'solar' or 'wind'. Therefore, all non-emitting powerplants of the same type have the same capacity factor for a particular year. The capacity factors, however, can vary between the years. 

#We add the capacity factors as follows:
#1. Read in capacity factor values
#2. Add capacity factor values to 'powerplants_ca'

#%%
                        
# 1. Read in capacity factor values
file_path_add_data = "../../06_CA Power Plants/"
                        
capacity_factors_ca_2005_2030 = pd.read_csv(file_path_add_data + "Capacity Factors_2005-2030.csv", sep=';', \
                                  encoding = 'unicode_escape')

capacity_factors_ca_2005_2030.set_index('PLANT_TYPE', inplace=True)

#%%

# 2. Add capacity factor values to 'powerplants_ca'
powerplants_ca_non_emitting_types = ['Nuclear', 'Hydro', 'Wind', 'Solar', 'Solar Thermal', 'Geothermal']

for y in powerplants_ca_non_emitting_types:
    for x in years_long:
        non_emitting_plants = powerplants_ca[\
                            (powerplants_ca.loc[:,'PLANT_TYPE'] == y) &
                            (powerplants_ca.loc[:,'INITIAL_START_DATE'] <= x)].index
        
        powerplants_ca.loc[non_emitting_plants, "CAPACITY_FACTOR_" + str(x)] = \
                        capacity_factors_ca_2005_2030.loc[y, str(x)]
        
        powerplants_ca.loc[non_emitting_plants, "EMISSIONS_[tCO2/MWh]_" + str(x)] = 0

#%%
        
####################              Visualize the data               ############################
        
#In a third step, we visualize the data. To do so we 
#1. Create Colors for Plot 
#2. Prepare annual Plot data. 
#3. Visualization of the data
#    -  Plot I: Bubble Plot - Capacity, capacity factors, emissions, and plant type

#%%
        
# 1. Create Colors for Plot

# Decide for color map
greys = matplotlib.cm.get_cmap('Greys')
blues = matplotlib.cm.get_cmap('Blues')
purples = matplotlib.cm.get_cmap('Purples')
greens = matplotlib.cm.get_cmap('Greens')
reds = matplotlib.cm.get_cmap('Reds')

powerplants_ca_type = powerplants_ca['PLANT_TYPE']
colors = []

for x in powerplants_ca_type:
    if x == 'Coal':
        colors.append(greys(0.5)) 
    elif x == 'Nuclear':
        colors.append(greys(0.8))  
    elif x == 'Gas_undefined':
        colors.append(blues(0.3))
    elif x == 'Cogen':
        colors.append(blues(0.45))
    elif x == 'Combined_cycle':
        colors.append(blues(0.6))
    elif x == 'Once_through_cooling':
        colors.append(blues(0.75))
    elif x == 'Peaker':
        colors.append(blues(0.9))
    elif x == 'Biogas':
        colors.append(purples(0.5))
    elif x == 'Biomass':
        colors.append(purples(0.8))
    elif x == 'Geothermal':
        colors.append(greens(0.3)) 
    elif x == 'Hydro':
        colors.append(greens(0.45))
    elif x == 'Solar':
        colors.append(greens(0.6)) 
    elif x == 'Solar Thermal':
        colors.append(greens(0.75)) 
    elif x == 'Wind':
        colors.append(greens(0.9))
    else: 
        colors.append(reds(0.5))

powerplants_ca['COLORS'] = colors

#%%

# 2. Prepare annual Plot data

for x in years_long:
    globals()['powerplants_plot_' + str(x)] = powerplants_ca.sort_values(by=[\
                                    'CAPACITY_FACTOR_' + str(x)], ascending=False)
    
    globals()['capacity_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)][\
                                    'CAPACITY_[MW]_' + str(x)]

    globals()['capacity_factor_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)][\
                                    'CAPACITY_FACTOR_' + str(x)]
    
    globals()['emissions_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)][\
                                    'EMISSIONS_[tCO2/MWh]_' + str(x)]

    globals()['colors_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)]['COLORS']

    ## Create x_axis distance of bars for design
    globals()['x_pos_plot_' + str(x)] = []
    total = 0
    i = 0
    j = 0
    for num in globals()['capacity_plot_' + str(x)]:
        i = num / 2
        total = total + i + j
        j = num / 2
        globals()['x_pos_plot_' + str(x)].append(total)
        
#%%
    
# Plot I: Capacity factors over capacity
fig, axes = plt.subplots(6, 1, sharex=True, figsize=(7.5,10))

axes[0].bar(x_pos_plot_2011, capacity_factor_plot_2011, width=capacity_plot_2011, \
            linewidth=0, color=colors_plot_2011)
axes[1].bar(x_pos_plot_2012, capacity_factor_plot_2012, width=capacity_plot_2012, \
            linewidth=0, color=colors_plot_2012)
axes[2].bar(x_pos_plot_2013, capacity_factor_plot_2013, width=capacity_plot_2013, \
            linewidth=0, color=colors_plot_2013)
axes[3].bar(x_pos_plot_2020, capacity_factor_plot_2020, width=capacity_plot_2020, \
            linewidth=0, color=colors_plot_2020)
axes[4].bar(x_pos_plot_2025, capacity_factor_plot_2025, width=capacity_plot_2025, \
            linewidth=0, color=colors_plot_2025)
axes[5].bar(x_pos_plot_2030, capacity_factor_plot_2030, width=capacity_plot_2030, \
            linewidth=0, color=colors_plot_2030)

##### Define Plot Style
font_title = {'size':'12', 'color':'black', 'weight':'bold',
              'verticalalignment':'bottom'}
font_axis = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
font_subtitle = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
tick_label_size = 12


# Plot Design
axes[0].set_title('2011', **font_subtitle, y=0.75)
axes[0].yaxis.grid(True)
axes[0].set_xlim([0,120000])
axes[0].set_ylim([0,1])
axes[0].tick_params(axis="y", labelsize=tick_label_size)
axes[0].tick_params(axis="x", labelsize=tick_label_size)

axes[1].set_title('2012', **font_subtitle, y=0.75)
axes[1].yaxis.grid(True)
axes[1].set_xlim([0,120000])
axes[1].set_ylim([0,1])
axes[1].tick_params(axis="y", labelsize=tick_label_size)
axes[1].tick_params(axis="x", labelsize=tick_label_size)

axes[2].set_title('2013', **font_subtitle, y=0.75)
axes[2].yaxis.grid(True)
axes[2].set_xlim([0,120000])
axes[2].set_ylim([0,1])
axes[2].tick_params(axis="y", labelsize=tick_label_size)
axes[2].tick_params(axis="x", labelsize=tick_label_size)

axes[3].set_title('2020', **font_subtitle, y=0.75)
axes[3].yaxis.grid(True)
axes[3].set_xlim([0,120000])
axes[3].set_ylim([0,1])
axes[3].tick_params(axis="y", labelsize=tick_label_size)
axes[3].tick_params(axis="x", labelsize=tick_label_size)

axes[4].set_title('2025', **font_subtitle, y=0.75)
axes[4].yaxis.grid(True)
axes[4].set_xlim([0,120000])
axes[4].set_ylim([0,1])
axes[4].tick_params(axis="y", labelsize=tick_label_size)
axes[4].tick_params(axis="x", labelsize=tick_label_size)

axes[5].set_title('2030', **font_subtitle, y=0.75)
axes[5].yaxis.grid(True)
axes[5].set_xlim([0,120000])
axes[5].set_ylim([0,1])
axes[5].tick_params(axis="y", labelsize=tick_label_size)
axes[5].tick_params(axis="x", labelsize=tick_label_size)



#Legend
legend_elements = [Line2D([0], [0], color=greys(0.5), lw=4, label='Coal'),\
                   Line2D([0], [0], color=greys(0.8), lw=4, label='Nuclear'),\
                   Line2D([0], [0], color=blues(0.3), lw=4, label='Gas_undefined'),\
                   Line2D([0], [0], color=blues(0.45), lw=4, label='Cogen'),\
                   Line2D([0], [0], color=blues(0.6), lw=4, label='Combined_cycle'),\
                   Line2D([0], [0], color=blues(0.75), lw=4, label='Once_through_cooling'),\
                   Line2D([0], [0], color=blues(0.9), lw=4, label='Peaker'),\
                   Line2D([0], [0], color=purples(0.5), lw=4, label='Biogas'),\
                   Line2D([0], [0], color=purples(0.8), lw=4, label='Biomass'),\
                   Line2D([0], [0], color=greens(0.3), lw=4, label='Geothermal'),\
                   Line2D([0], [0], color=greens(0.45), lw=4, label='Hydro'),\
                   Line2D([0], [0], color=greens(0.6), lw=4, label='Solar'),\
                   Line2D([0], [0], color=greens(0.75), lw=4, label='Solar Thermal'),\
                   Line2D([0], [0], color=greens(0.9), lw=4, label='Wind')]

fig.legend(handles=legend_elements, loc='upper right', ncol=1, bbox_to_anchor=(1.22, 0.85), frameon=False)

# Axis labels
fig.suptitle("Power Plants in California - Capacity factor over capacity", **font_title, y=0.9)
fig.text(0.5, 0.05, 'Capacity [MW]', ha='center', va='center')
fig.text(0.03, 0.5, 'Capacity Factor', ha='center', va='center', rotation='vertical')

#Plotting
plt.savefig(file_path_visualization + 'All Power Plants in California - Capacity factor over capacity.png')
plt.show()

#%%

# Plot II: Emissionsover capacity
fig, axes = plt.subplots(6, 1, sharex=True, figsize=(7.5,10))

axes[0].bar(x_pos_plot_2011, emissions_plot_2011, width=capacity_plot_2011, \
            linewidth=0, color=colors_plot_2011)
axes[1].bar(x_pos_plot_2012, emissions_plot_2012, width=capacity_plot_2012, \
            linewidth=0, color=colors_plot_2012)
axes[2].bar(x_pos_plot_2013, emissions_plot_2013, width=capacity_plot_2013, \
            linewidth=0, color=colors_plot_2013)
axes[3].bar(x_pos_plot_2020, emissions_plot_2020, width=capacity_plot_2020, \
            linewidth=0, color=colors_plot_2020)
axes[4].bar(x_pos_plot_2025, emissions_plot_2025, width=capacity_plot_2025, \
            linewidth=0, color=colors_plot_2025)
axes[5].bar(x_pos_plot_2030, emissions_plot_2030, width=capacity_plot_2030, \
            linewidth=0, color=colors_plot_2030)

##### Define Plot Style
font_title = {'size':'12', 'color':'black', 'weight':'bold',
              'verticalalignment':'bottom'}
font_axis = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
font_subtitle = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
tick_label_size = 12


# Plot Design
axes[0].set_title('2011', **font_subtitle, y=0.75)
axes[0].yaxis.grid(True)
axes[0].set_xlim([0,120000])
axes[0].set_ylim([0,2])
axes[0].tick_params(axis="y", labelsize=tick_label_size)
axes[0].tick_params(axis="x", labelsize=tick_label_size)

axes[1].set_title('2012', **font_subtitle, y=0.75)
axes[1].yaxis.grid(True)
axes[1].set_xlim([0,120000])
axes[1].set_ylim([0,2])
axes[1].tick_params(axis="y", labelsize=tick_label_size)
axes[1].tick_params(axis="x", labelsize=tick_label_size)

axes[2].set_title('2013', **font_subtitle, y=0.75)
axes[2].yaxis.grid(True)
axes[2].set_xlim([0,120000])
axes[2].set_ylim([0,2])
axes[2].tick_params(axis="y", labelsize=tick_label_size)
axes[2].tick_params(axis="x", labelsize=tick_label_size)

axes[3].set_title('2020', **font_subtitle, y=0.75)
axes[3].yaxis.grid(True)
axes[3].set_xlim([0,120000])
axes[3].set_ylim([0,2])
axes[3].tick_params(axis="y", labelsize=tick_label_size)
axes[3].tick_params(axis="x", labelsize=tick_label_size)

axes[4].set_title('2025', **font_subtitle, y=0.75)
axes[4].yaxis.grid(True)
axes[4].set_xlim([0,120000])
axes[4].set_ylim([0,2])
axes[4].tick_params(axis="y", labelsize=tick_label_size)
axes[4].tick_params(axis="x", labelsize=tick_label_size)

axes[5].set_title('2030', **font_subtitle, y=0.75)
axes[5].yaxis.grid(True)
axes[5].set_xlim([0,120000])
axes[5].set_ylim([0,2])
axes[5].tick_params(axis="y", labelsize=tick_label_size)
axes[5].tick_params(axis="x", labelsize=tick_label_size)



#Legend
legend_elements = [Line2D([0], [0], color=greys(0.5), lw=4, label='Coal'),\
                   Line2D([0], [0], color=greys(0.8), lw=4, label='Nuclear'),\
                   Line2D([0], [0], color=blues(0.3), lw=4, label='Gas_undefined'),\
                   Line2D([0], [0], color=blues(0.45), lw=4, label='Cogen'),\
                   Line2D([0], [0], color=blues(0.6), lw=4, label='Combined_cycle'),\
                   Line2D([0], [0], color=blues(0.75), lw=4, label='Once_through_cooling'),\
                   Line2D([0], [0], color=blues(0.9), lw=4, label='Peaker'),\
                   Line2D([0], [0], color=purples(0.5), lw=4, label='Biogas'),\
                   Line2D([0], [0], color=purples(0.8), lw=4, label='Biomass'),\
                   Line2D([0], [0], color=greens(0.3), lw=4, label='Geothermal'),\
                   Line2D([0], [0], color=greens(0.45), lw=4, label='Hydro'),\
                   Line2D([0], [0], color=greens(0.6), lw=4, label='Solar'),\
                   Line2D([0], [0], color=greens(0.75), lw=4, label='Solar Thermal'),\
                   Line2D([0], [0], color=greens(0.9), lw=4, label='Wind')]

fig.legend(handles=legend_elements, loc='upper right', ncol=1, bbox_to_anchor=(1.22, 0.85), frameon=False)

# Axis labels
fig.suptitle("Power Plants in California - Capacity factor over capacity", **font_title, y=0.9)
fig.text(0.5, 0.05, 'Capacity [MW]', ha='center', va='center')
fig.text(0.03, 0.5, 'Emissions [tCO2/MWh]', ha='center', va='center', rotation='vertical')

#Plotting
plt.savefig(file_path_visualization + 'All Power Plants in California - Emissions over capacity.png')
plt.show()

#%%

#########################################################################################################
########################    Create Dataframe 'powerplants_ca_average_day'      ##########################
#########################################################################################################

#Third, we create the dataframe 'powerplants_ca_average_day'. This dataframe provides hourly data for the average day of a specific year. Applying this dataframe, we could analyse how hourly demand profiles require different powerplants to run. To define the hourly-available capacity we assume the following: 
#-  Solar powerplants have hourly different capacity factors. We derive the hourly different capacity factors by the average capacity factor over the specific year and the PV generation profile, which indicates how the total electricity generated by a PV is spread over the day (in the sum the PV generation profile is 100% over one day). The PV generation profile is based on data by Darghouth et al. 2013. 
#- low-marginal-cost powerplants - such as wind, hydro, and nuclear - provide capacity according to their max capacity times their capacity factor. High-marginal-cost powerplants, however, provide their full capacity. We do so, becauase the capacity factors of powerplants are below 100% mainly due to three factors. First, applying the merit order, their marginal costs were higher than the matching price (demand and supply). Second, downtime due to maintenance and fuel refueling. Third, lack of natural resources such as wind, sun, and water. While the former does not influence the max capacity powerplants can bid on the market, the latter two are constraints for the bid. 
#- Capacity factors ...

#To build a merit order of the powerplants in the "pwoerplants_ca' dataframe, we extend the dataframe as follows:

#- Year of average day
#- Create new powerplants dataframe
#- Set Merit Order Factors
#- Set Merit Order Capacities

#- Categorize powerplants according their marginal costs
#- Add columns for merit order capacity 'MO_CAPACITY_[MW]_'
#- Fill merir order capacity

#%%

###################             Year of average day             #############################

# 1. Set year of the average day
years = list(range(2005,2031))

for y in years: 

    ###################         Create new powerplants dataframe           ###############################

    #1. Create dataframe for the average day of this year
    powerplants_average_day = pd.DataFrame()

    # Add only those powerplants that have alread been built in this year
    powerplanst_built = powerplants_ca[powerplants_ca.loc[:, 'INITIAL_START_DATE'] <= y].index

    powerplants_average_day = powerplants_ca.loc[powerplanst_built,['PLANT_TYPE',\
                                            'INITIAL_START_DATE',\
                                            'CAPACITY_[MW]_' + str(y),\
                                            'CAPACITY_FACTOR_' + str(y),\
                                            'EMISSIONS_[tCO2/MWh]_' + str(y),\
                                            'COLORS']]



    #2. Add hourly merit order capacity and capacity factor columns
    hours_of_the_day = list(range(0,24))

    capacity_of_the_day = []
    capacity_factor_of_the_day = []
    emissions_of_the_day = []

    for x in hours_of_the_day:
        capacity_factor_of_the_day.append('MO_' + str(x))
        capacity_of_the_day.append('CAPACITY_MO_[MW]_' + str(x))

    powerplants_average_day = powerplants_average_day.reindex(columns = \
                            powerplants_average_day.columns.tolist() + capacity_of_the_day + capacity_factor_of_the_day + emissions_of_the_day) 



    #####################      Set Merit Order        #############################

    #To order powerplants in a merit Order - as we do not have the marginal costs for the individual powerplants - we develop a relative merit order, between 0 and 1. Powerplants close to 0 in the merit order typically run every hour while the powerplants close to 1 only run in extreme cases. 

    #To assign powerplants a merit order factor, we do three steps. 
    #1. Categorizing powerplants according their marginal costs: 
    #    - Low-marginal-cost power plants are: solar, solar thermal, wind, hydro, geothermal, nuclear. 
    #    - High-marginal-cost powerplants are: all gas types (i.e.,Cogen, Combined_cycle, Gas_undefined, Once_through_cooling, and Peaker), coal, and biomass. 
    #- Assigning low-marginal-cost powerplants a merit order factor close to 0
    #- Assigning high-marginal-cost powerplants a merit order factor based on their capacity factors, but 1 - capacity factor


    # 1. Categorize powerplants according their marginal costs
    controllable_plants = powerplants_average_day[\
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Cogen') |
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Combined_cycle') |
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Gas_undefined') |
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Peaker') |
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Biomass') |
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Geothermal') |
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Nuclear') |
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Coal') |
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Biogas') |
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Once_through_cooling')\
                                                   ].index

    intermittant_plants = powerplants_average_day[\
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Hydro') |
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Solar Thermal') |
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Wind')\
                             ].index

    solar_plants = powerplants_average_day[\
                             (powerplants_ca.loc[:,'PLANT_TYPE'] == 'Solar')].index
  
    #2. Assigning intermittent powerplants a merit order factor close to 0
    for x in hours_of_the_day:
    
        #   We do not set it to 0 to make them appear in the graph
        powerplants_average_day.loc[intermittant_plants, 'MO_' + str(x)] = 0.05
        powerplants_average_day.loc[solar_plants, 'MO_' + str(x)] = 0.025
                                           

    # 3. Assigning controllable powerplants a merit order factor based on their capacity factors
    ## but 1 - capacity factor

    for x in hours_of_the_day: 
        
        powerplants_average_day.loc[controllable_plants, 'MO_' + str(x)] = \
                1 - powerplants_average_day['CAPACITY_FACTOR_' + str(y)]
                


          
    ##################           Set Merit Order Capacities             ############################
                
    #Powerplants contribute differently to the merit oder capacity:

    #- For intermittant powerplants we add their capacity according their capacity factor to the merit order, e.g., hydro has a mean capacity factor of 0.389 and a capacity of around 13 GW -> 5GW for the merit order.
    #- Solar has a diurnal cycle and thus contributes to the merit order differnetly over one day
    #- For adjustable (controllable) powerplants such as gas, biomass and digester gas, we add them with their full capacity to the merit order

    #We extend the dataframe as follows:
    #1.  Calculate solar hourly capacity factors: We calculate hourly solar capacity factors based on the PV generation profile, which we also use in the agent-based model (Schwarz et al. 2018). The PV generation profile is from Darghouth et al. 2013.
    #2. Set merit order capacity 
    #3. Set cumulative Merit Order Capacity               


                
    #1. Define hourly solar capacity factors for this year

    # Read in "pv_generation_profile.csv"
                
    file_path_add_data = "../../06_CA Power Plants/00_Original Data/04_PV_generation_profile/"
  
    hourly_capacity_factor_solar = pd.read_csv(file_path_add_data + "pv_generation_profile.csv", \
                            sep=';', encoding = 'unicode_escape')

    # Formatting the dataframe
    hourly_capacity_factor_solar = hourly_capacity_factor_solar.set_index(\
                                                'Unnamed: 0').rename_axis('')

    hourly_capacity_factor = pd.Series()
    hourly_capacity_factor.name = 'HOURLY_CAPACITY_FACTOR'
    hourly_capacity_factor_solar = hourly_capacity_factor_solar.append(hourly_capacity_factor)

    # Define hourly solar capacity factors based on:
    # (i) annual capacity factor and 
    # (ii) hourly generation profile

    this_year_capacity_factor = capacity_factors_ca_2005_2030.loc['Solar',str(y)]

    for x in hours_of_the_day:
        hourly_capacity_factor_solar.loc['HOURLY_CAPACITY_FACTOR', str(x)] = \
                    this_year_capacity_factor * 24 * hourly_capacity_factor_solar.loc[\
                    'PV_GENERATION_PROFILE', str(x)]
                    

                
    # 2. Set merit order 

    for x in hours_of_the_day:
    
        #Adjustable powerplants
        powerplants_average_day.loc[controllable_plants, "CAPACITY_MO_[MW]_" + str(x)] = \
            powerplants_average_day.loc[controllable_plants, "CAPACITY_[MW]_" + str(y)]
    
        #Intermittant powerplants
        powerplants_average_day.loc[intermittant_plants, "CAPACITY_MO_[MW]_" + str(x)] = \
            powerplants_average_day.loc[intermittant_plants, "CAPACITY_FACTOR_" + str(y)] * \
            powerplants_average_day.loc[intermittant_plants, "CAPACITY_[MW]_" + str(y)]
    
        #Solar    
        powerplants_average_day.loc[solar_plants, "CAPACITY_MO_[MW]_" + str(x)] = \
            powerplants_average_day.loc[solar_plants, "CAPACITY_[MW]_" + str(y)] * \
            hourly_capacity_factor_solar.loc['HOURLY_CAPACITY_FACTOR', str(x)]
        

        
    ## Set cumulative Merit Order Capacity
    for x in hours_of_the_day:
    
        globals()['cumululative_capacity_' + str(x)] = []
        total = 0
        
        for num in powerplants_average_day['CAPACITY_MO_[MW]_' + str(x)] :
            
            total = total + num
            globals()['cumululative_capacity_' + str(x)].append(total)
        
        powerplants_average_day['MO_CAPACITY_CUM_' + str(x)] = globals()['cumululative_capacity_' + str(x)] 
        
    globals()['powerplants_average_day_' + str(y)] = powerplants_average_day
    
    #####################      Export Dataset         ################################
    
    # Save dataframe 'powerplants_average_day' to csv
    # Remove commas and semicolons in index 
    powerplants_average_day = powerplants_average_day.replace(r',', '', regex=True) 
    powerplants_average_day = powerplants_average_day.replace(r';', '', regex=True)
    
    path_results = "../../06_CA Power Plants/"
    export_csv = powerplants_average_day.to_csv(path_results + "powerplants_average_day_" + str(y) + ".csv")
    
    
        
#%%
       
# set year for plotting:

year = 2026 

powerplants_average_day = globals()['powerplants_average_day_' + str(year)]
                         
##########################          Visualize data           ############################

# 1. Prepare annual Plot data

for x in hours_of_the_day:
    
    globals()['powerplants_plot_' + str(x)] = powerplants_average_day.sort_values(by=[\
                                    'MO_' + str(x)], ascending=True)
    
    globals()['capacity_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)][\
                                    'CAPACITY_MO_[MW]_' + str(x)]

    globals()['merit_order_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)][\
                                    'MO_' + str(x)]
    
    globals()['emissions_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)][\
                                    'EMISSIONS_[tCO2/MWh]_' + str(year)]

    globals()['colors_plot_' + str(x)] = globals()['powerplants_plot_' + str(x)]['COLORS']

    ## Create x_axis distance of bars for design
    globals()['x_pos_plot_' + str(x)] = []
    total = 0
    i = 0
    j = 0
    for num in globals()['capacity_plot_' + str(x)]:
        i = num / 2
        total = total + i + j
        j = num / 2
        globals()['x_pos_plot_' + str(x)].append(total)


#%%
        
       
# Plot I: Capacity factors over capacity
fig, axes = plt.subplots(4, 1, sharex=True, figsize=(7.5,10))

axes[0].bar(x_pos_plot_23, merit_order_plot_23, width=capacity_plot_23, \
            linewidth=0, color=colors_plot_23)
axes[1].bar(x_pos_plot_7, merit_order_plot_7, width=capacity_plot_7, \
            linewidth=0, color=colors_plot_7)
axes[2].bar(x_pos_plot_11, merit_order_plot_11, width=capacity_plot_11, \
            linewidth=0, color=colors_plot_11)
axes[3].bar(x_pos_plot_15, merit_order_plot_15, width=capacity_plot_15, \
            linewidth=0, color=colors_plot_15)

##### Define Plot Style
font_title = {'size':'12', 'color':'black', 'weight':'bold',
              'verticalalignment':'bottom'}
font_axis = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
font_subtitle = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
tick_label_size = 12


# Plot Design
axes[0].set_title('0h', **font_subtitle, y=0.8, x = 0.1)
axes[0].yaxis.grid(True)
axes[0].set_xlim([0,90000])
axes[0].set_ylim([0,1])
axes[0].tick_params(axis="y", labelsize=tick_label_size)
axes[0].tick_params(axis="x", labelsize=tick_label_size)

axes[1].set_title('8h', **font_subtitle, y=0.8, x = 0.1)
axes[1].yaxis.grid(True)
axes[1].set_xlim([0,90000])
axes[1].set_ylim([0,1])
axes[1].tick_params(axis="y", labelsize=tick_label_size)
axes[1].tick_params(axis="x", labelsize=tick_label_size)

axes[2].set_title('12h', **font_subtitle, y=0.8, x = 0.1)
axes[2].yaxis.grid(True)
axes[2].set_xlim([0,90000])
axes[2].set_ylim([0,1])
axes[2].tick_params(axis="y", labelsize=tick_label_size)
axes[2].tick_params(axis="x", labelsize=tick_label_size)

axes[3].set_title('16h', **font_subtitle, y=0.8, x = 0.1)
axes[3].yaxis.grid(True)
axes[3].set_xlim([0,90000])
axes[3].set_ylim([0,1])
axes[3].tick_params(axis="y", labelsize=tick_label_size)
axes[3].tick_params(axis="x", labelsize=tick_label_size)


#Legend
legend_elements = [Line2D([0], [0], color=greys(0.5), lw=4, label='Coal'),\
                   Line2D([0], [0], color=greys(0.8), lw=4, label='Nuclear'),\
                   Line2D([0], [0], color=blues(0.3), lw=4, label='Gas_undefined'),\
                   Line2D([0], [0], color=blues(0.45), lw=4, label='Cogen'),\
                   Line2D([0], [0], color=blues(0.6), lw=4, label='Combined_cycle'),\
                   Line2D([0], [0], color=blues(0.75), lw=4, label='Once_through_cooling'),\
                   Line2D([0], [0], color=blues(0.9), lw=4, label='Peaker'),\
                   Line2D([0], [0], color=purples(0.5), lw=4, label='Biogas'),\
                   Line2D([0], [0], color=purples(0.8), lw=4, label='Biomass'),\
                   Line2D([0], [0], color=greens(0.3), lw=4, label='Geothermal'),\
                   Line2D([0], [0], color=greens(0.45), lw=4, label='Hydro'),\
                   Line2D([0], [0], color=greens(0.6), lw=4, label='Solar'),\
                   Line2D([0], [0], color=greens(0.75), lw=4, label='Solar Thermal'),\
                   Line2D([0], [0], color=greens(0.9), lw=4, label='Wind')]

fig.legend(handles=legend_elements, loc='upper right', ncol=1, bbox_to_anchor=(1.22, 0.85), frameon=False)

# Axis labels
fig.suptitle(str (year) + " - Average day - Merit Order", **font_title, y=0.9)
fig.text(0.5, 0.05, 'Capacity [MW]', ha='center', va='center', **font_axis)
fig.text(0.03, 0.5, 'Merit Order [0-1]', ha='center', va='center', rotation='vertical', **font_axis)

#Plotting
plt.savefig(file_path_visualization + str (year) + ' - Average day - Merit Order.png')
plt.show()

#%%

# Plot II: Emissions
fig, axes = plt.subplots(4, 1, sharex=True, figsize=(7.5,10))

axes[0].bar(x_pos_plot_23, emissions_plot_23, width=capacity_plot_23, \
            linewidth=0, color=colors_plot_23)
axes[1].bar(x_pos_plot_7, emissions_plot_7, width=capacity_plot_7, \
            linewidth=0, color=colors_plot_7)
axes[2].bar(x_pos_plot_11, emissions_plot_11, width=capacity_plot_11, \
            linewidth=0, color=colors_plot_11)
axes[3].bar(x_pos_plot_15, emissions_plot_15, width=capacity_plot_15, \
            linewidth=0, color=colors_plot_15)

##### Define Plot Style
font_title = {'size':'12', 'color':'black', 'weight':'bold',
              'verticalalignment':'bottom'}
font_axis = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
font_subtitle = {'size':'12', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'}
tick_label_size = 12

# Plot Design
axes[0].set_title('0h', **font_subtitle, y=0.8, x = 0.1)
axes[0].yaxis.grid(True)
axes[0].set_xlim([0,90000])
axes[0].set_ylim([0,2])
axes[0].tick_params(axis="y", labelsize=tick_label_size)
axes[0].tick_params(axis="x", labelsize=tick_label_size)

axes[1].set_title('8h', **font_subtitle, y=0.8, x = 0.1)
axes[1].yaxis.grid(True)
axes[1].set_xlim([0,90000])
axes[1].set_ylim([0,2])
axes[1].tick_params(axis="y", labelsize=tick_label_size)
axes[1].tick_params(axis="x", labelsize=tick_label_size)

axes[2].set_title('12h', **font_subtitle, y=0.8, x = 0.1)
axes[2].yaxis.grid(True)
axes[2].set_xlim([0,90000])
axes[2].set_ylim([0,2])
axes[2].tick_params(axis="y", labelsize=tick_label_size)
axes[2].tick_params(axis="x", labelsize=tick_label_size)

axes[3].set_title('16h', **font_subtitle, y=0.8, x = 0.1)
axes[3].yaxis.grid(True)
axes[3].set_xlim([0,90000])
axes[3].set_ylim([0,2])
axes[3].tick_params(axis="y", labelsize=tick_label_size)
axes[3].tick_params(axis="x", labelsize=tick_label_size)


#Legend
legend_elements = [Line2D([0], [0], color=greys(0.5), lw=4, label='Coal'),\
                   Line2D([0], [0], color=greys(0.8), lw=4, label='Nuclear'),\
                   Line2D([0], [0], color=blues(0.3), lw=4, label='Gas_undefined'),\
                   Line2D([0], [0], color=blues(0.45), lw=4, label='Cogen'),\
                   Line2D([0], [0], color=blues(0.6), lw=4, label='Combined_cycle'),\
                   Line2D([0], [0], color=blues(0.75), lw=4, label='Once_through_cooling'),\
                   Line2D([0], [0], color=blues(0.9), lw=4, label='Peaker'),\
                   Line2D([0], [0], color=purples(0.5), lw=4, label='Biogas'),\
                   Line2D([0], [0], color=purples(0.8), lw=4, label='Biomass'),\
                   Line2D([0], [0], color=greens(0.3), lw=4, label='Geothermal'),\
                   Line2D([0], [0], color=greens(0.45), lw=4, label='Hydro'),\
                   Line2D([0], [0], color=greens(0.6), lw=4, label='Solar'),\
                   Line2D([0], [0], color=greens(0.75), lw=4, label='Solar Thermal'),\
                   Line2D([0], [0], color=greens(0.9), lw=4, label='Wind')]

fig.legend(handles=legend_elements, loc='upper right', ncol=1, bbox_to_anchor=(1.22, 0.85), frameon=False)


# Axis labels
fig.suptitle(str (year) + " - Average day - Merit Order", **font_title, y=0.9)
fig.text(0.5, 0.05, 'Capacity [MW]', ha='center', va='center', **font_axis)
fig.text(0.03, 0.4, 'Emissions [tCO2/MWh]', ha='center', va='center', rotation='vertical', **font_axis)

#Plotting
plt.savefig(file_path_visualization + str (year) + ' - Average day - Emissions in Merit Order.png')
plt.show()













