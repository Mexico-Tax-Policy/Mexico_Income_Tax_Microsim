"""
app1.py illustrates use of pitaxcalc-demo release 2.0.0 (India version).
USAGE: python app1.py > app1.res
CHECK: Use your favorite Windows diff utility to confirm that app1.res is
       the same as the app1.out file that is in the repository.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, r'C:\Users\Sayra Martínez\OneDrive\Documents\MIDP\MexicoTaxation\Mexico_Income_Tax_Microsim')
from stata_python import plot_kakwani_lorenz_curve_reform

# Initialize the variables

vars = {}

vars['pit'] = 1
vars['cit'] = 0
vars['vat'] = 0

tax_type = 'pit'
vars['DEFAULTS_FILENAME'] = "current_law_policy_pit_Mex.json"
vars['GROWFACTORS_FILENAME'] = "growfactors_pit_Mex.csv" 
vars['pit_data_filename'] = "pit_mexico_big.csv"
vars['pit_weights_filename'] = "pit_mexico_big_weights.csv"
vars['pit_records_variables_filename'] = "records_variables_pit_Mex.json"
vars['pit_benchmark_filename'] = "tax_incentives_benchmark_pit_training.json"
vars['pit_elasticity_filename'] = "pit_elasticity_selection.json"
vars['pit_functions_filename'] = "functions_pit_Mex.py"
vars['pit_function_names_filename'] = "function_names_pit_Mex.json"
vars['pit_distribution_json_filename'] = 'pit_distribution_training.json'

vars['vat_data_filename'] = "gst.csv"
vars['vat_weights_filename'] = "gst_weights.csv"
vars['vat_records_variables_filename'] = "gstrecords_variables.json"  

vars['cit_data_filename'] = "cit_cross.csv"
vars['cit_weights_filename'] = "cit_cross_wgts1.csv"
vars['cit_records_variables_filename'] = "corprecords_variables.json"

vars['gdp_filename'] = 'gdp_nominal_training.csv'
vars["start_year"] = 2022
vars["end_year"] = 2027
vars["SALARY_VARIABLE"] = "gross_wage"
vars['elasticity_filename'] = "pit_elasticity_selection.json"
vars['DIST_VARIABLES'] = ['weight', 'gross_wage', 'pitax']
vars['DIST_TABLE_COLUMNS'] = ['weight', 'gross_wage', 'pitax']        
vars['DIST_TABLE_LABELS'] = ['Returns',
                     'Gross Wages',
                     'PITax']
vars['DECILE_ROW_NAMES'] = ['0-10n', '0-10z', '0-10p',
                    '10-20', '20-30', '30-40', '40-50',
                    '50-60', '60-70', '70-80', '80-90', '90-100',
                    'ALL',
                    '90-95', '95-99', 'Top 1%']
vars['STANDARD_ROW_NAMES'] = [ "<0", "=0", "0-0.5 m", "0.5-1m", "1-1.5m", "1.5-2m",
                      "2-3m", "3-4m", "4-5m", "5-10m", ">10m", "ALL"]
vars['STANDARD_INCOME_BINS'] = [-9e99, -1e-9, 1e-9, 5e5, 10e5, 15e5, 20e5, 30e5,
                        40e5, 50e5, 100e5, 9e99]
vars['income_measure'] = "total_gross_income"
vars['show_error_log'] = 0
vars['verbose'] = 0
vars['data_start_year'] = 2022

f = open('taxcalc/'+vars['pit_distribution_json_filename'])
distribution_vardict_dict = json.load(f)
f.close()
#print(distribution_vardict_dict)
           
with open('global_vars.json', 'w') as f:
    f.write(json.dumps(vars, indent=2))
f.close()

from taxcalc import *


# create Records object containing pit.csv and pit_weights.csv input data
recs = Records()

# create Policy object containing current-law policy
pol = Policy()

# specify Calculator object for current-law policy
calc1 = Calculator(policy=pol, records=recs, verbose=False)
calc1.calc_all()

# specify Calculator object for reform in JSON file
reform = Calculator.read_json_param_objects('app0_reform_pit_Mex_statusquo.json', None)
pol.implement_reform(reform['policy'])
calc2 = Calculator(policy=pol, records=recs, verbose=False)
calc2.calc_all()


# compare aggregate results from two calculators
weighted_tax1 = calc1.weighted_total_pit('pitax')
weighted_tax2 = calc2.weighted_total_pit('pitax')
total_weights = calc1.total_weight_pit()
print(f'Tax 1 {weighted_tax1 * 1e-9:,.2f}')
print(f'Tax 2 {weighted_tax2 * 1e-9:,.2f}')
print(f'Total weight {total_weights * 1e-6:,.2f}')

calc1.advance_to_year(2026)
calc2.advance_to_year(2026)
calc1.calc_all()
calc2.calc_all()

# compare aggregate results from two calculators
weighted_tax3 = calc1.weighted_total_pit('pitax')
weighted_tax4 = calc2.weighted_total_pit('pitax')
total_weights = calc1.total_weight_pit()
print(f'Tax 3 {weighted_tax3 * 1e-9:,.2f}')
print(f'Tax 4 {weighted_tax4 * 1e-9:,.2f}')
print(f'Total weight {total_weights * 1e-6:,.2f}')

# dump out records
dump_vars = ['id_n', 'age', 'weight', 'tot_inc','gross_wage', 'wage_inc', 'total_gross_income', 'taxable_income', 'tax_cum_income', 'authorized_deduction', 'subsidy_w', 'pending_pitax', 'capitalgains_pitax', 'gambling_pitax', 'additional_dividend_pitax', 'pitax']
dumpdf = calc1.dataframe(dump_vars)
dumpdf['pitax1'] = calc1.array('pitax')
dumpdf['pitax2'] = calc2.array('pitax')
dumpdf['pitax_diff'] = dumpdf['pitax2'] - dumpdf['pitax1']
column_order = dumpdf.columns

dumpdf.to_csv('app1-dump_pit_Mex.csv', columns=column_order,
              index=False, float_format='%.0f')
#I additionaly save it for pareto analysis
#dumpdf.to_csv('forpareto_mex.csv', columns=column_order,
#              index=False, float_format='%.0f')

def calc_gini(values):
    """Calculate the Gini coefficient."""
    n = len(values)
    sorted_vals = np.sort(values)
    cumvals = np.cumsum(sorted_vals)
    gini_index = ((2 * np.sum((np.arange(1, n + 1) * sorted_vals))) / (n * cumvals[-1])) - ((n + 1) / n)
    return gini_index

# Filter and sort data
dumpdf = dumpdf[dumpdf['total_gross_income'] > 0]
dumpdf = dumpdf.sort_values(by='total_gross_income')

# Extract arrays
values_inc = dumpdf['total_gross_income'].dropna().values
values_pit1 = dumpdf['pitax1'].dropna().values
values_pit2 = dumpdf['pitax2'].dropna().values

# --- Calculate Gini Coefficients ---
gini_income = calc_gini(values_inc)
gini_tax1 = calc_gini(values_pit1)
gini_tax2 = calc_gini(values_pit2)

print(f"Gini (Income): {gini_income:.4f}")
print(f"Gini (Current Tax): {gini_tax1:.4f}")
print(f"Gini (Reform Tax): {gini_tax2:.4f}")

# --- Plot Lorenz Curve with Kakwani Index ---
plot_kakwani_lorenz_curve_reform(
    income=values_inc,
    tax1=values_pit1,
    tax2=values_pit2,
    label1="Lorenz Curve PIT Pre-reform",
    label2="Lorenz Curve PIT Post-Reform",
    title="Lorenz Curves and Kakwani Index (2026)"
)

# --- Compute weighted average ETRs by income percentile for smoother plot ---

# Filter valid income values
df_filtered = dumpdf[dumpdf['total_gross_income'] > 0].copy()

# Compute ETRs
df_filtered['ETR'] = df_filtered['pitax1'] / df_filtered['total_gross_income']
df_filtered['ETR_ref'] = df_filtered['pitax2'] / df_filtered['total_gross_income']

# Remove NaNs and infinite values
df_filtered = df_filtered.replace([np.inf, -np.inf], np.nan)
df_filtered = df_filtered.dropna(subset=['ETR', 'ETR_ref', 'weight'])

# Create income percentiles using qcut
df_filtered['percentile'] = pd.qcut(df_filtered['total_gross_income'], 100, labels=False) + 1

# Group by percentile and compute weighted average ETR
etr_summary = df_filtered.groupby('percentile').apply(
    lambda x: pd.Series({
        'ETR': np.average(x['ETR'], weights=x['weight']),
        'ETR_ref': np.average(x['ETR_ref'], weights=x['weight'])
    })
).reset_index()

# Define annual minimum wage value
#2025
#min_wage_annual = 100368.00
min_wage_annual = 62233.20 * 1.036
s_min_wage_annual = min_wage_annual * 1.21
GDP_pc = 19.3615 * 11.26 * 1000

# Compute percentile for minimum wage
min_wage_percentile = (
    df_filtered[df_filtered['total_gross_income'] <= min_wage_annual]['weight'].sum() /
    df_filtered['weight'].sum()
) * 100

# Percentile for 1.2x minimum wage
s_min_wage_percentile = (
    df_filtered[df_filtered['total_gross_income'] <= s_min_wage_annual]['weight'].sum() /
    df_filtered['weight'].sum()
) * 100

# Percentile for GDP per capita
gdp_pc_percentile = (
    df_filtered[df_filtered['total_gross_income'] <= GDP_pc]['weight'].sum() /
    df_filtered['weight'].sum()
) * 100

print(f"Minimum wage is at approx. percentile: {min_wage_percentile:.1f}")
print(f"1.2 Minimum wage is at approx. percentile: {s_min_wage_percentile:.1f}")
print(f"GDP per capita is at approx. percentile: {gdp_pc_percentile:.1f}")

# --- Plot ---
plt.figure(figsize=(10, 6))
plt.plot(etr_summary['percentile'], etr_summary['ETR'], label="ETR Current Law", linewidth=2)
plt.plot(etr_summary['percentile'], etr_summary['ETR_ref'], label="ETR Reform", linewidth=2)

# Min wage line
plt.axvline(x=min_wage_percentile, color='gray', linestyle='--', linewidth=1.5)
plt.text(min_wage_percentile + 1, 0.02, 'Min Wage', rotation=90, color='black', fontsize=9)

# GDP per capita line
plt.axvline(x=gdp_pc_percentile, color='gray', linestyle='-.', linewidth=1.5)
plt.text(gdp_pc_percentile + 1, 0.02, 'GDP per Capita - tax rate: 21.36%', rotation=90, color='black', fontsize=9)

# Optional: 1.2x min wage
plt.axvline(x=s_min_wage_percentile, color='red', linestyle=':', linewidth=1.5)
plt.text(s_min_wage_percentile + 1, 0.02, '1.2 Min Wage - tax rate: 10.88%', rotation=90, color='black', fontsize=9)

# Formatting
plt.xlabel("Income Percentile")
plt.ylabel("Effective Tax Rate")
plt.title("Effective Tax Rate (ETR) by Percentile")
plt.xticks(np.arange(0, 101, 10))
plt.ylim(0, 0.25)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# Create a new figure for just the original ETR
plt.figure(figsize=(10, 6))

# Plot only the original ETR line
plt.plot(etr_summary['percentile'], etr_summary['ETR'], label="ETR Current Law", linewidth=2, color='#4373B9')

# Keep the same reference lines for context
# Min wage line
plt.axvline(x=min_wage_percentile, color='gray', linestyle='--', linewidth=1.5)
plt.text(min_wage_percentile + 1, 0.02, 'Min Wage', rotation=90, color='black', fontsize=9)

# GDP per capita line
plt.axvline(x=gdp_pc_percentile, color='gray', linestyle='-.', linewidth=1.5)
plt.text(gdp_pc_percentile + 1, 0.02, 'GDP per Capita - tax rate: 21.36%', rotation=90, color='black', fontsize=9)

# Optional: 1.2x min wage
plt.axvline(x=s_min_wage_percentile, color='red', linestyle=':', linewidth=1.5)
plt.text(s_min_wage_percentile + 1, 0.02, '1.2 Min Wage - tax rate: 10.88%', rotation=90, color='black', fontsize=9)

# Formatting
plt.xlabel("Income Percentile")
plt.ylabel("Effective Tax Rate")
plt.title("Effective Tax Rate (ETR) by Percentile for Gross Income excluding cash transfers")
plt.xticks(np.arange(0, 101, 10))
plt.ylim(0, 0.25)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()