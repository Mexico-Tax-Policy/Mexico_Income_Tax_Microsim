"""
pitaxcalc-demo functions that calculate personal income tax liability.
"""
# CODING-STYLE CHECKS:
# pycodestyle functions.py
# pylint --disable=locally-disabled functions.py

import math
import copy
import numpy as np
from taxcalc.decorators import iterate_jit

@iterate_jit(nopython=True)
def cal_gross_wages(wage_w_pr, piecework_w_pr, comissions_w_pr, overtime_w_pr, 
                    rewards_w_pr, bonus_w_pr, vacation_w_pr, profit_sharing_w_pr, 
                    profit_sharing_w_se, christmas_bonus_w_pr, christmas_bonus_w_se, 
                    wage_b_pr, profit_b_pr, other_b_pr, wage_b_se, profit_b_se, other_b_se,                
                    other_other_lastmonth, other_other_prev5, wage_w_se, gross_wage):
    """
    Compute total gross income from wages.
    """
    gross_wage = (wage_w_pr + piecework_w_pr + comissions_w_pr + overtime_w_pr + 
                  rewards_w_pr + bonus_w_pr + vacation_w_pr + profit_sharing_w_pr + 
                  profit_sharing_w_se + christmas_bonus_w_pr + christmas_bonus_w_se + 
                  wage_b_pr + profit_b_pr + other_b_pr + wage_b_se + profit_b_se + other_b_se + 
                  other_other_lastmonth + other_other_prev5 + wage_w_se)
    return gross_wage

@iterate_jit(nopython=True)
def calc_total_wage(wage_w_pr, wage_b_pr, wage_w_se, wage_b_se, wage_inc):
    """
    This function calculates the Christmas bonus taxable income.
    
    """
    wage_inc = wage_w_pr + wage_b_pr + wage_w_se + wage_b_se
    return wage_inc

@iterate_jit(nopython=True)
def calc_overtime_bonus_w_t(minimum_wage, UMA_value_d, allowance_bonus_overtime,
                            wage_inc, overtime_w_pr, rewards_w_pr, bonus_w_pr, overtime_bonus_w_t):
    """
    This function calculates the taxable income from bonuses and overtime.
    According to the Income Law, 5 UMA per worked week are exempt. 
    That is why I multiplied the limit per week for 52 weeks of the year.
    """
    if wage_inc > minimum_wage:
        overtime_bonus_w_t = max(0.5 * ((overtime_w_pr + rewards_w_pr + bonus_w_pr) - UMA_value_d * allowance_bonus_overtime * 52), 0)
    else:
        overtime_bonus_w_t = 0
    return overtime_bonus_w_t

@iterate_jit(nopython=True)
def calc_christmas_t(UMA_value_d, allowance_christmas, christmas_bonus_w_pr, 
                     christmas_bonus_w_se, christmas_bonus_t):
    """
    This function calculates the Christmas bonus taxable income.
    """
    christmas_bonus_t = max((christmas_bonus_w_pr + christmas_bonus_w_se) - UMA_value_d * allowance_christmas, 0)
    return christmas_bonus_t

@iterate_jit(nopython=True)
def calc_vacations_t(UMA_value_d, allowance_vacations_profit_sharing, vacation_w_pr, vacation_t):
    """
    This function calculates the Christmas bonus taxable income.
    """
    vacation_t = max(vacation_w_pr - UMA_value_d * allowance_vacations_profit_sharing, 0)
    return vacation_t

@iterate_jit(nopython=True)
def calc_profit_sharing_t(UMA_value_d, allowance_vacations_profit_sharing, 
                          profit_sharing_w_pr, profit_sharing_w_se):
    """
    This function calculates the profit sharing taxable income.
    """
    profit_sharing_t = max((profit_sharing_w_pr + profit_sharing_w_se) - UMA_value_d * allowance_vacations_profit_sharing, 0)
    return profit_sharing_t

@iterate_jit(nopython=True)
def calc_wage_bu_t(wage_b_pr, profit_b_pr, other_b_pr, wage_b_se, profit_b_se, other_b_se, wage_bu_t):
    """
    This function calculates the total wage income from businesses,
    including primary and secondary businesses: wage, profit, and other business income.
    """
    wage_bu_t = (wage_b_pr + profit_b_pr + other_b_pr + wage_b_se + profit_b_se + other_b_se)
    return wage_bu_t

@iterate_jit(nopython=True)
def calc_layoff_w_t(wage_inc, transfers_compensation_layoff, layoff_w_t, layoff_pending):
    """
    This function calculates the taxable income from layoffs.
    It compares the monthly wage income to the layoff compensation and returns the taxable layoff income and any pending amount.
    """
    if (wage_inc / 12) > transfers_compensation_layoff:
        layoff_w_t = transfers_compensation_layoff
        layoff_pending = 0
    else:
        layoff_w_t = wage_inc / 12
        layoff_pending = transfers_compensation_layoff - (wage_inc / 12)

    return layoff_w_t, layoff_pending


@iterate_jit(nopython=True)
def calc_income_wages_t(allowance_wages, UMA_value_y, wage_inc, overtime_bonus_w_t, christmas_bonus_t, vacation_t, 
                        profit_sharing_t, wage_bu_t, layoff_w_t, piecework_w_pr, comissions_w_pr,
                        other_other_lastmonth, other_other_prev5, income_wages_t):
    """
    This function calculates the taxable income from all wages-related concepts.
    """
    income_wages_t = max((wage_inc + overtime_bonus_w_t + christmas_bonus_t + vacation_t + profit_sharing_t + wage_bu_t + layoff_w_t + piecework_w_pr + comissions_w_pr + other_other_lastmonth + other_other_prev5) - allowance_wages*UMA_value_y, 0)
    return income_wages_t

@iterate_jit(nopython=True)
def calc_pensions_t(allowance_pensions, UMA_value_d, transfers_pension_mx, transfers_pension_abroad):
    """
    This function calculates the taxable income from pensions.
    It subtracts the allowable exemptions (calculated using UMA) from the total pension transfers.
    """
    pensions_w_t = max((transfers_pension_mx + transfers_pension_abroad) - UMA_value_d * allowance_pensions * 30 * 12, 0)
    return pensions_w_t

@iterate_jit(nopython=True)
def calc_rent_t(rent_building_abroad, rent_building_mx, rent_land, rent_intangibles, rent_other, income_rent_t):
    """
    This function calculates the taxable income rent of assets.
    For buildings and land, Income law allows to deduct 35% of the income instead of applying the specific applicable deductions.
    """
    income_rent_t =  0.65 * (rent_building_abroad + rent_building_mx + rent_land) + rent_intangibles + rent_other
    return income_rent_t

@iterate_jit(nopython=True)
def calc_real_estate_t(allowance_realestate, capital_realproperty, capital_real_estate_t):
    """
    This function calculates the taxable income from sales of real property.
    It is exempt up to 700,000 UDIS (the average value of this unit in 2022 was 7.380710885).
    To cumulate the income, the law set forth to divide the income between the years of property (maximum 20)
    This exemption can only be applied once every three years.
    """
    capital_real_estate_t = max(((capital_realproperty - allowance_realestate * 7.380710885) / 10 / 3),0)
    return capital_real_estate_t

@iterate_jit(nopython=True)
def calc_land_t(UMA_value_y, allowance_land_sales, capital_land, capital_land_t):
    """
    This function calculates the taxable income from sales of land.
    It is exempt up to 3 UMAS (annual value).
    """
    capital_land_t = max((capital_land - allowance_land_sales* UMA_value_y),0)
    return capital_land_t

@iterate_jit(nopython=True)
def calc_capital_t(capital_jewelryorart, capital_intangibles, capital_real_estate_t, 
                   capital_land_t, capital_m_and_e, capital_vehicles, capital_hhitems, income_capital_t):
    """
    This function calculates the taxable income from sales of capital.
    """
    income_capital_t = (capital_jewelryorart + capital_intangibles + capital_real_estate_t + 
                 capital_land_t + capital_m_and_e + capital_vehicles + capital_hhitems)
    return income_capital_t

@iterate_jit(nopython=True)
def calc_capital_pending(capital_realproperty, capital_real_estate_t, capital_land, capital_land_t):
    """
    This function calculates the taxable income pending from sales of land and real estate.
    """
    pending_capital_t = (capital_realproperty / 3 - capital_real_estate_t) + (capital_land - capital_land_t)
    return pending_capital_t

@iterate_jit(nopython=True)
def calc_other_t(other_financial_capital, transfers_othercountries):
    """
    This function calculates the taxable income pending from sales of land and real estate.
    """
    income_other_t = (other_financial_capital + transfers_othercountries)
    return income_other_t

@iterate_jit(nopython=True)
def calc_donations_t(allowance_bonus_overtime, UMA_value_y, transfers_donation_nongov, transfers_donation_otherHH):
    """
    This function calculates the taxable income pending from sales of land and real estate.
    """
    income_donations_t = max((transfers_donation_nongov + transfers_donation_otherHH) - allowance_bonus_overtime * UMA_value_y, 0)
    return income_donations_t

@iterate_jit(nopython=True)
def calc_interest_t(interest_inv, interest_savings, interest_loans, interest_bonds, investment_withdrawal, payments_loan_otherHH, life_insurance):
    """
    This function calculates the taxable income pending from sales of land and real estate.
    """
    income_interest_t = (interest_inv + interest_savings + interest_loans + interest_bonds + investment_withdrawal + payments_loan_otherHH + life_insurance)

    return income_interest_t

@iterate_jit(nopython=True)
def exempt_total_income(transfers_scholarship_nongov, transfers_scholarship_gov, life_insurance_headshh,
                         welfare_procampo, welfare_elders, welfare_other_social_benefits, welfare_other_nonreported,
                         inheritances, welfare_scholarship_PROSPERA, welfare_scholarship_BJ, welfare_scholarship_JEF,
                         welfare_older, welfare_disabilities, welfare_children_workingmothers, welfare_JCF, 
                         transfers_compensation_insurance, transfers_compensation_workaccident):
    
    exempt_total_income = (transfers_scholarship_nongov + transfers_scholarship_gov + life_insurance_headshh + 
                           welfare_procampo + welfare_elders + welfare_other_social_benefits + 
                           welfare_other_nonreported + inheritances + welfare_scholarship_PROSPERA + 
                           welfare_scholarship_BJ + welfare_scholarship_JEF + welfare_older + 
                           welfare_disabilities + welfare_children_workingmothers + welfare_JCF + 
                           transfers_compensation_insurance + transfers_compensation_workaccident)
    
    return exempt_total_income

@iterate_jit(nopython=True)
def cal_total_gross_income (tot_inc, exempt_total_income, total_gross_income):
    """
    Compute total gross income (excluding exempt incomes).
    """
    total_gross_income = (tot_inc - exempt_total_income)
    return total_gross_income

@iterate_jit(nopython=True)
def cal_t_cum_income(allowance_general, UMA_value_y, income_wages_t, income_dividend_t, income_interest_t, income_capital_t, income_other_t,     
                          income_rent_t, income_donations_t, pensions_w_t, tax_cum_income):
    """
    Compute total cumulable incomes.
    """
    tax_cum_income = max((income_wages_t + income_dividend_t + income_interest_t + income_capital_t + income_other_t +     
                              income_rent_t + income_donations_t + pensions_w_t) - allowance_general*UMA_value_y, 0)
    return tax_cum_income

@iterate_jit(nopython=True)
def cal_deductions(limit_deduction_of_inc, limit_deduction_as_UMA, UMA_value_y, deductible_expenses, total_gross_income, authorized_deduction):
    """
    Compute authorized deductions.
    """
    authorized_deduction = min(min(deductible_expenses, total_gross_income * limit_deduction_of_inc),  UMA_value_y * limit_deduction_as_UMA) 
    return authorized_deduction

@iterate_jit(nopython=True)
def cal_taxable_income(authorized_deduction, tax_cum_income):
    """
    Compute taxable income.
    """    
    taxable_income = max((tax_cum_income - authorized_deduction), 0)
    return taxable_income

@iterate_jit(nopython=True)
def cal_tax_refund(authorized_deduction, tax_cum_income):
    """
    Compute taxable income.
    """    
    tax_refund = (min((tax_cum_income - authorized_deduction), 0))*-1
    return tax_refund

@iterate_jit(nopython=True)
def cal_pit_w(rate1, rate2, rate3, rate4, rate5, rate6, rate7, rate8, rate9, rate10, rate11, 
              tbrk1, tbrk2, tbrk3, tbrk4, tbrk5, tbrk6, tbrk7, tbrk8, tbrk9, tbrk10, 
              taxable_income, pitax_w, highest_rate_applied):
    """
    Compute PIT and store the highest marginal rate applied.
    """
    inc = taxable_income

    if inc <= tbrk1:
        pitax_w = (inc - 0.01) * rate1
        highest_rate_applied = rate1
    elif inc > tbrk1 and inc <= tbrk2:
        pitax_w = (inc - tbrk1) * rate2 + (tbrk1 - 0.01) * rate1
        highest_rate_applied = rate2
    elif inc > tbrk2 and inc <= tbrk3:
        pitax_w = (inc - tbrk2) * rate3 + (tbrk2 - tbrk1) * rate2 + (tbrk1 - 0.01) * rate1
        highest_rate_applied = rate3
    elif inc > tbrk3 and inc <= tbrk4:
        pitax_w = (inc - tbrk3) * rate4 + (tbrk3 - tbrk2) * rate3 + (tbrk2 - tbrk1) * rate2 + (tbrk1 - 0.01) * rate1
        highest_rate_applied = rate4
    elif inc > tbrk4 and inc <= tbrk5:
        pitax_w = (inc - tbrk4) * rate5 + (tbrk4 - tbrk3) * rate4 + (tbrk3 - tbrk2) * rate3 + (tbrk2 - tbrk1) * rate2 + (tbrk1 - 0.01) * rate1
        highest_rate_applied = rate5
    elif inc > tbrk5 and inc <= tbrk6:
        pitax_w = (inc - tbrk5) * rate6 + (tbrk5 - tbrk4) * rate5 + (tbrk4 - tbrk3) * rate4 + (tbrk3 - tbrk2) * rate3 + (tbrk2 - tbrk1) * rate2 + (tbrk1 - 0.01) * rate1
        highest_rate_applied = rate6
    elif inc > tbrk6 and inc <= tbrk7:
        pitax_w = (inc - tbrk6) * rate7 + (tbrk6 - tbrk5) * rate6 + (tbrk5 - tbrk4) * rate5 + (tbrk4 - tbrk3) * rate4 + (tbrk3 - tbrk2) * rate3 + (tbrk2 - tbrk1) * rate2 + (tbrk1 - 0.01) * rate1
        highest_rate_applied = rate7
    elif inc > tbrk7 and inc <= tbrk8:
        pitax_w = (inc - tbrk7) * rate8 + (tbrk7 - tbrk6) * rate7 + (tbrk6 - tbrk5) * rate6 + (tbrk5 - tbrk4) * rate5 + (tbrk4 - tbrk3) * rate4 + (tbrk3 - tbrk2) * rate3 + (tbrk2 - tbrk1) * rate2 + (tbrk1 - 0.01) * rate1
        highest_rate_applied = rate8
    elif inc > tbrk8 and inc <= tbrk9:
        pitax_w = (inc - tbrk8) * rate9 + (tbrk8 - tbrk7) * rate8 + (tbrk7 - tbrk6) * rate7 + (tbrk6 - tbrk5) * rate6 + (tbrk5 - tbrk4) * rate5 + (tbrk4 - tbrk3) * rate4 + (tbrk3 - tbrk2) * rate3 + (tbrk2 - tbrk1) * rate2 + (tbrk1 - 0.01) * rate1
        highest_rate_applied = rate9
    elif inc > tbrk9 and inc <= tbrk10:
        pitax_w = (inc - tbrk9) * rate10 + (tbrk9 - tbrk8) * rate9 + (tbrk8 - tbrk7) * rate8 + (tbrk7 - tbrk6) * rate7 + (tbrk6 - tbrk5) * rate6 + (tbrk5 - tbrk4) * rate5 + (tbrk4 - tbrk3) * rate4 + (tbrk3 - tbrk2) * rate3 + (tbrk2 - tbrk1) * rate2 + (tbrk1 - 0.01) * rate1
        highest_rate_applied = rate10
    elif inc > tbrk10:
        pitax_w = (inc - tbrk10) * rate11 + (tbrk10 - tbrk9) * rate10 + (tbrk9 - tbrk8) * rate9 + (tbrk8 - tbrk7) * rate8 + (tbrk7 - tbrk6) * rate7 + (tbrk6 - tbrk5) * rate6 + (tbrk5 - tbrk4) * rate5 + (tbrk4 - tbrk3) * rate4 + (tbrk3 - tbrk2) * rate3 + (tbrk2 - tbrk1) * rate2 + (tbrk1 - 0.01) * rate1
        highest_rate_applied = rate11

    return pitax_w, highest_rate_applied

@iterate_jit(nopython=True)
def cal_subsidy_wage(subsidy_rate, UMA_value_y, wage_inc, minimum_wage, subsidy_w):
    """
   Calculate wage subsidy only for workers with wages > 0 and <= 1.2 * minimum wage.
    """

    if wage_inc  >= minimum_wage and wage_inc <= (minimum_wage * 1.2):
        subsidy_w = UMA_value_y * subsidy_rate
    else:
        subsidy_w = 0
    return subsidy_w

@iterate_jit(nopython=True)
def cal_additional_dividends(additional_dividend_rate, income_dividend_t, additional_dividend_pitax):
    
    """
    Compute additional 10% tax for dividends.
    """
   
    additional_dividend_pitax =(income_dividend_t*additional_dividend_rate)
    return additional_dividend_pitax

@iterate_jit(nopython=True)
def cal_gambling_pitax(gambling_rate, lotteries, gambling_pitax):
    """
    Compute tax for gambling incomes.
    """
    gambling_pitax =  (lotteries*gambling_rate)
    return gambling_pitax

@iterate_jit(nopython=True)
def cal_capitalgains_pitax(capitalgains_bonds_rate, capital_bonds, capitalgains_pitax):
    
    """
    Compute additional 10% tax for dividends.
    """
   
    capitalgains_pitax =(capital_bonds*capitalgains_bonds_rate)
    return capitalgains_pitax

@iterate_jit(nopython=True)
def cal_pendingconcepts_pitax(highest_rate_applied, layoff_pending, pending_capital_t, pending_pitax):
    
    """
    Compute tax for pending amounts (layoff compensations, sales of land and housing, etc.).
    """
    pending_pitax = (layoff_pending + pending_capital_t)*highest_rate_applied
    return pending_pitax

@iterate_jit(nopython=True)
def cal_total_pit(pitax_w, additional_dividend_pitax, gambling_pitax, capitalgains_pitax, pending_pitax, subsidy_w, pitax):
    """
    Compute Total PIT.
    """
    pitax = max((pitax_w + additional_dividend_pitax + gambling_pitax + capitalgains_pitax + pending_pitax - subsidy_w), 0)
    return pitax