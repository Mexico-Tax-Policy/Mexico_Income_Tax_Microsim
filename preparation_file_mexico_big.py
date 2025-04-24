# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, r'C:/Users/Sayra Martínez/OneDrive/Documents/MIDP/Tax Microsim Mexico/Mexico_Income_Tax_Microsim')
from stata_python import *
import pandas as pd
import numpy as np

#This is the master file with the characteristics of the population, I'll take it to drop all rows corresponding to people below 18
#as they are not registered taxpayers
file_path_pop = r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\Tax Microsim Mexico\ENIGH 2022_Mex\conjunto_de_datos_poblacion_enigh2022_ns\conjunto_de_datos\conjunto_de_datos_poblacion_enigh2022_ns.csv'
pop = pd.read_csv(file_path_pop)

pop['id_n'] = pop['folioviv'].astype('str')+'_'+pop['foliohog'].astype('str')+'_'+pop['numren'].astype('str')

#Dataset for incomes
# Loading the dataset with the incomes information (it does not include all the population, as not everyone receives incomes)
file_path = r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\Tax Microsim Mexico\ENIGH 2022_Mex\conjunto_de_datos_ingresos_enigh2022_ns\conjunto_de_datos\conjunto_de_datos_ingresos_enigh2022_ns.csv'
df = pd.read_csv(file_path)

df['id_n'] = df['folioviv'].astype('str')+'_'+df['foliohog'].astype('str')+'_'+df['numren'].astype('str')

#print(f"DataFrame has {df.shape[0]} rows and {df.shape[1]} columns")

# Merge only the edad column from pop into df
df = df.merge(pop[['id_n', 'edad']], on='id_n', how='left')

# Verify the merge worked
#print(f"DataFrame now has {df.shape[0]} rows and {df.shape[1]} columns")
#print("First few rows with edad column:")
#print(df[['id_n', 'edad']].head())

# Check the initial number of rows
initial_rows = df.shape[0]
print(f"Initial number of rows: {initial_rows}")

# Verify the filtering worked
print("\nVerification:")
print(f"Rows with clave='P067': {(df['clave'] == 'P067').sum()}")
print(f"Rows with edad < 16: {(df['edad'] < 16).sum()}")

# I droped the incomes of people under 12 as taxpayers should be 16+ (legal age to formally work)
df = df[df['clave'] != 'P067']
# Drop rows where edad is less than 18
df = df[df['edad'] >= 16]

# Check how many rows were removed
final_rows = df.shape[0]
removed_rows = initial_rows - final_rows
print(f"Removed {removed_rows} rows ({removed_rows/initial_rows:.2%} of data)")
print(f"Final number of rows: {final_rows}")

# Verify the filtering worked
print("\nVerification:")
print(f"Rows with clave='P067': {(df['clave'] == 'P067').sum()}")
print(f"Rows with edad < 16: {(df['edad'] < 16).sum()}")

df['yearly_income'] =df['ing_tri']*4
df = df.rename(columns={
    'edad': 'age',
    'clave': 'income_group'
})

# Pivot the data
p_df = df.pivot_table(index=['id_n', 'folioviv', 'foliohog', 'numren', 'age', 'factor'], 
                            columns='income_group', 
                            values='yearly_income', 
                            aggfunc='sum',
                            fill_value=0).reset_index()

# Define the dictionary with old column names as keys and new names as values
column_name_mapping = {
    'P001': 'wage_w_pr',
    'P002': 'piecework_w_pr',
    'P003': 'comissions_w_pr',
    'P004': 'overtime_w_pr',
    'P005': 'rewards_w_pr',
    'P006': 'bonus_w_pr',
    'P007': 'vacation_w_pr',
    'P008': 'profit_sharing_w_pr',
    'P009': 'christmas_bonus_w_pr',
    'P011': 'wage_b_pr',
    'P012': 'profit_b_pr',
    'P013': 'other_b_pr',
    'P014': 'wage_w_se',
    'P015': 'profit_sharing_w_se',
    'P016': 'christmas_bonus_w_se',
    'P018': 'wage_b_se',
    'P019': 'profit_b_se',
    'P020': 'other_b_se',
    'P021': 'other_other_lastmonth',
    'P022': 'other_other_prev5',
    'P023': 'rent_land',
    'P024': 'rent_building_mx',
    'P025': 'rent_building_abroad',
    'P026': 'interest_inv',
    'P027': 'interest_savings',
    'P028': 'interest_loans',
    'P029': 'interest_bonds',
    'P030': 'rent_intangibles',
    'P031': 'rent_other',
    'P032': 'transfers_pension_mx',
    'P033': 'transfers_pension_abroad',
    'P034': 'transfers_compensation_insurance',
    'P035': 'transfers_compensation_workaccident',
    'P036': 'transfers_compensation_layoff',
    'P037': 'transfers_scholarship_nongov',
    'P038': 'transfers_scholarship_gov',
    'P039': 'transfers_donation_nongov',
    'P040': 'transfers_donation_otherHH',
    'P041': 'transfers_othercountries',
    'P043': 'welfare_procampo',
    'P045': 'welfare_elders',
    'P048': 'welfare_other_social_benefits',
    'P049': 'welfare_other_nonreported',
    'P050': 'dividends',
    'P051': 'investment_withdrawal',
    'P052': 'payments_loan_otherHH',
    'P053': 'loan_except_mortgage',
    'P054': 'capital_jewelryorart',
    'P055': 'capital_bonds',
    'P056': 'capital_intangibles',
    'P057': 'inheritances',
    'P058': 'lotteries',
    'P059': 'capital_realproperty',
    'P060': 'capital_land',
    'P061': 'capital_m&e',
    'P062': 'capital_vehicles',
    'P063': 'capital_hhitems',
    'P064': 'loan_mortgage',
    'P065': 'life_insurance',
    'P066': 'other_financial_capital',
    'P068': 'business_pr_industrial',
    'P069': 'business_pr_commercial',
    'P070': 'business_pr_services',
    'P071': 'business_pr_agriculture',
    'P072': 'business_pr_breeding',
    'P073': 'business_pr_reforestation',
    'P074': 'business_pr_fishing',
    'P075': 'business_se_industrial',
    'P076': 'business_se_commercial',
    'P077': 'business_se_services',
    'P078': 'business_se_agriculture',
    'P079': 'business_se_breeding',
    'P080': 'business_se_reforestation',
    'P081': 'business_se_fishing',
    'P101': 'welfare_scholarship_PROSPERA',
    'P102': 'welfare_scholarship_BJ',
    'P103': 'welfare_scholarship_JEF',
    'P104': 'welfare_older',
    'P105': 'welfare_disabilities',
    'P106': 'welfare_children_workingmothers',
    'P107': 'life_insurance_headshh',
    'P108': 'welfare_JCF'
}

p_df = p_df.rename(columns=column_name_mapping)

p_df['tot_inc'] = 0
for k, v in column_name_mapping.items():
   p_df['tot_inc'] = p_df['tot_inc'] + p_df[v]
   
#I adjusted the weights for the big file considering that in Q4 2022, the rate of employments in informality reached 28.1%  https://www.inegi.org.mx/temas/empleo/
p_df = p_df.rename(columns={'factor':'factor1'})
p_df['factor']= p_df['factor1'] * 0.719   

# Define the output path for the new CSV
#output_path = r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\Tax Microsim Mexico\income_pit_mex_4sampling.csv'
# Save the pivoted DataFrame to a new CSV
#p_df.to_csv(output_path, index=False)

#print(f"Income File saved to: {output_path}")

# Load the dataset for personal expenses
file_path = r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\4S\MP\conjunto_de_datos_gastospersona_enigh2022_ns.csv'
df_e = pd.read_csv(file_path)

df_e['id_n'] = df_e['folioviv'].astype('str')+'_'+df_e['foliohog'].astype('str')+'_'+df_e['numren'].astype('str')

df_e['gasto_tri'] = pd.to_numeric(df_e['gasto_tri'], errors='coerce')
df_e['yearly_expenses'] = df_e['gasto_tri'] * 4
df_e = df_e.rename(columns={'clave': 'expenses'})

# I have defined a specific list of expense codes to focus on, as the raw data contains over 700 codes.
# By filtering for only those that are related to deductions, I can create a more manageable and focused dataset for analysis.
gasto_codes = {
    'E013': 'School_transport',
    'J001': 'Medical_services_childbirth',
    'J002': 'Hospitalization_childbirth',
    'J003': 'Clinical_tests_childbirth',
    'J004': 'Prescribed_medications_childbirth',
    'J007': 'Medical_consultations_preg',
    'J008': 'Dental_consultations_preg',
    'J009': 'Prescribed_medications_preg',
    'J011': 'Clinical_tests_preg',
    'J012': 'Hospitalization_preg',
    'J015': 'Other_services_preg',
    'J016': 'General_medical_consultations',
    'J017': 'Specialist_medical_consultations',
    'J018': 'Dental_consultations',
    'J019': 'Clinical_tests',
    'J039': 'Professional_services_other',
    'J040': 'Hospitalization_other',
    'J041': 'Clinical_tests_other',
    'J042': 'Prescribed_medications_other',
    'J043': 'Services_ambulance_other',
    'J065': 'Glasses',
    'J066': 'Hearing_aids',
    'J067': 'Orthopedic_therapy_devices',
    'J068': 'Orthopedic_device_or_repairs',
    'J069': 'Other_services',
    'J070': 'Hospital_clinic_fees',
    'J071': 'Insurance_medical_fees',
    'N002': 'Funerals',
    'N014': 'Charity_contributions',
    'T916': 'Financial_capital_expenditures'
}

# Filter the dataset to include only the rows for the selected gasto codes
df_filteredexpenses = df_e[df_e['expenses'].isin(gasto_codes.keys())]

# Pivot the dataset by type of expense
df_exp = df_filteredexpenses.pivot_table(
    index=['id_n'
],
    columns='expenses',
    values=['yearly_expenses'],
    aggfunc='sum',
    fill_value=0
)

df_exp = df_exp.rename(columns=gasto_codes)

# Flatten the multi-level columns created by the pivot and rename them as the last level (gasto code names)(if I delete this, I get a row with all columns call "yearly_expenses" and a second row with the names in gasto_code)
df_exp.columns = [
    f'{col[1]}' for col in df_exp.columns
]

# Check which columns from gasto_codes exist in the pivoted DataFrame
expense_columns = [col for col in df_exp.columns if col not in ['id_n']]

df_exp['deductible_expenses'] = 0
for v in expense_columns:
    df_exp['deductible_expenses'] = df_exp['deductible_expenses'] + df_exp[v]

# Display the updated DataFrame
#print(df_exp[['deductible_expenses']].head())

# Reset the index to make the DataFrame clean
df_exp.reset_index(inplace=True)

# Define the full path to save the output CSV
#output_path2 = r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\Tax Microsim Mexico\expenses_4sampling.csv'

# Save the resulting dataset to the new CSV file in the specified folder
#df_exp.to_csv(output_path2, index=False)

#CREATE A MERGED DATABASE 
merged_df = pd.merge(p_df, df_exp, on=['id_n'], how='left')

merged_df['Year']=2022
#merged_df['id_n'] = merged_df['folioviv'].astype('str')+'_'+merged_df['foliohog'].astype('str')+'_'+merged_df['numren'].astype('str')

# Check the first few rows to verify
print(merged_df['id_n'].head())

# Arranging
desired_column_order = [
    'id_n', 'age', 'factor', 'Year',
    'tot_inc', 'deductible_expenses'
] + [col for col in merged_df.columns if col not in [
    'id_n', 'age', 'factor', 'Year',
    'tot_inc', 'deductible_expenses'
]]
        
# Reorder the columns in the dataframe
merged_df = merged_df[desired_column_order]

# List of columns to exclude from coercion
exclude_columns = ['id_n', 'age', 'factor', 'Year']

# Select the columns to apply coercion on (all columns except the ones in exclude_columns)
cols_to_convert = merged_df.columns.difference(exclude_columns)

# Apply numeric conversion to the selected columns
merged_df[cols_to_convert] = merged_df[cols_to_convert].apply(pd.to_numeric, errors='coerce')

# Fill NaN values with 0 for all columns
merged_df = merged_df.fillna(0)

#Plot the density of total income (including exempted income)
plot_density_chart(merged_df, 'tot_inc', category_var=None, title=None, logx=True, vline=None)

print(merged_df[['id_n', 'age', 'factor']].head())

# Output the first few rows to verify the result
#print(merged_df.head())

# Define the path to save the final dataset
output_final_path = r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\MexicoTaxation\Mexico_Income_Tax_Microsim\data_mexico_big.csv'

# Save the final dataset
merged_df.to_csv(output_final_path, index=False)

print(f"Final PREPARED dataset saved to {output_final_path}")
