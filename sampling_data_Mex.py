"""
This is a file that allows sampling of a large dataset.
"""
import sys
sys.path.insert(0, r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\MexicoTaxation\Mexico_Income_Tax_Microsim')
from stata_python import *
import pandas as pd
import numpy as np

p_df=pd.read_csv(r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\MexicoTaxation\Mexico_Income_Tax_Microsim\data_mexico_big.csv')
p_df = p_df.rename(columns={'id_n':'id_n1'})
p_df['id_n']=range(1, len(p_df) + 1)
p_df['weight'] = p_df['factor']

pit_weight = p_df[['factor']]

pit_weight.columns = ['WT2022']
pit_weight['WT2023'] = pit_weight['WT2022']
pit_weight['WT2024'] = pit_weight['WT2022']
pit_weight['WT2025'] = pit_weight['WT2022']
pit_weight['WT2026'] = pit_weight['WT2022']
pit_weight['WT2027'] = pit_weight['WT2022']
pit_weight['WT2028'] = pit_weight['WT2022']
pit_weight['WT2029'] = pit_weight['WT2022']
pit_weight['WT2030'] = pit_weight['WT2022']
pit_weight['WT2031'] = pit_weight['WT2022']
pit_weight['WT2032'] = pit_weight['WT2022']

pit_weight.to_csv('taxcalc/pit_mexico_big_weights.csv')

#Before running this one, go to aap1_pit_Mex_big.py to run and estimate the tax coolection_syn_billion
# After running the app1, run this section to reweight using tax projections calibrated
tax_collection_2022_billion =  1129.99 

# synthetic data has only 100,000 observations
tax_collection_big_billion = 484.01

multiplicative_factor1 = tax_collection_2022_billion/tax_collection_big_billion

#I adjust reported revenues (2023 and 2024) for subsequent years vs revenues from 2022
#I used the mean of 2022-2024 for 2025-2031
rev_vs2022 = [
    1.000,  # 2022
    1.111,  # 2023
    1.184,  # 2024
    1.098,  # 2025
    1.098,  # 2026
    1.098,  # 2027
    1.098,  # 2028
    1.098,  # 2029
    1.098,  # 2030
    1.098,   # 2031
    1.098   # 2032    
]

for i, year in enumerate(range(2022, 2033)):
    col = f"WT{year}"
    pit_weight[col] = pit_weight[col] * multiplicative_factor1 * rev_vs2022[i]
# Save to CSV
pit_weight.to_csv('taxcalc/pit_mexico_big_weights.csv', index=False)

#I did not saved the changes in id_n before, so that is why I am saving the big file too, this time in taxcalc
#Remeber that id_n is at the right extrem of the data
p_df.to_csv('taxcalc/pit_mexico_big.csv')

sys.path.insert(0, r'C:/Users/Sayra Martínez/OneDrive/Documents/MIDP/Tax Microsim Mexico/Mexico_Income_Tax_Microsim')
from stata_python import *
import pandas as pd
import numpy as np


#the first time, I ran only the part of sampling and the creation of weights file, but not the part of calibration
#To avoid changes in the future, I saved that sample and keep using it
#pit_sample= p_df.sample(n=100000, weights=p_df['factor'], replace=True)
pit_sample=pd.read_csv('taxcalc/pit_mexico_sample.csv')
pit_sample['weight'] = 1.0
#plot_density_chart(pit_sample, 'tot_inc', logx=True)

plot_density_chart_mult(p_df, 'Original Dataset', pit_sample, 'Sample', 'tot_inc', title=None, xlabel=None, logx=True, vline=None)


total_weight_sample = pit_sample['weight'].sum()
total_weight_population = p_df['weight'].sum()
#comparing the statistic of the population and sample
varlist = ['tot_inc']
for var in varlist:
    pit_sample['weighted_'+var] = pit_sample[var]*pit_sample['weight']
    sample_sum = pit_sample['weighted_'+var].sum()
    p_df['weighted_'+var] = p_df[var]*p_df['weight']
    population_sum = p_df['weighted_'+var].sum()
    
    sample_mean = sample_sum/total_weight_sample    
    population_mean = population_sum/total_weight_population
    print("           Sample Mean for ", var, " = ", sample_mean)
    print("       Population Mean for ", var, " = ", population_mean)
    print("Sampling Error for Mean(%) ", var, " = ", "{:.2%}".format((population_mean-sample_mean)/population_mean))

#unless I want to create a different sample, do not save a new one
#pit_sample.to_csv('taxcalc/pit_mexico_sample.csv')

#I run this part and THEN GO TO RUN THE app1_pit_Mex_sample.py 
df_weight = pit_sample[['weight']]

df_weight.columns = ['WT2022']
df_weight['WT2023'] = df_weight['WT2022']
df_weight['WT2024'] = df_weight['WT2022']
df_weight['WT2025'] = df_weight['WT2022']
df_weight['WT2026'] = df_weight['WT2022']
df_weight['WT2027'] = df_weight['WT2022']
df_weight['WT2028'] = df_weight['WT2022']
df_weight['WT2029'] = df_weight['WT2022']
df_weight['WT2030'] = df_weight['WT2022']
df_weight['WT2031'] = df_weight['WT2022']
df_weight['WT2032'] = df_weight['WT2022']

df_weight.to_csv('taxcalc/pit_mexico_sample_weights.csv')

#Before running this one, go to aap1_pit_Mex_sample.py to run and estimate the tax coolection_syn_billion
# After running the app1, run this section to reweight using tax projections calibrated
tax_collection_2022_billion =  1129.99 

# synthetic data has only 100,000 observations
tax_collection_syn_billion = 0.88

multiplicative_factor = tax_collection_2022_billion/tax_collection_syn_billion

#I adjust reported revenues (2023 and 2024) for subsequent years vs revenues from 2022
#I used the mean of 2022-2024 for 2025-2031
rev_vs2022 = [
    1.000,  # 2022
    1.111,  # 2023
    1.184,  # 2024
    1.098,  # 2025
    1.098,  # 2026
    1.098,  # 2027
    1.098,  # 2028
    1.098,  # 2029
    1.098,  # 2030
    1.098,   # 2031
    1.098   # 2032    
]

# Apply factor to each weight column
for i, year in enumerate(range(2022, 2033)):
    col = f"WT{year}"
    df_weight[col] = df_weight[col] * multiplicative_factor * rev_vs2022[i]

# Save to CSV
df_weight.to_csv('taxcalc/pit_mexico_sample_weights.csv', index=False)

#RERUN the app1



