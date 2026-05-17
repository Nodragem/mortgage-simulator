# -*- coding: utf-8 -*-
# %%
import pandas as pd

initial_debt = 125000 #pounds
mortgage_term = 25 #year
interest_rate = 5.07 #%

# also good for comparison: https://moneyfactscompare.co.uk/
# formula gives same results as https://www.moneysavingexpert.com/mortgages/mortgage-overpayment-calculator/
# and can be found on wikipedia: https://en.wikipedia.org/wiki/Mortgage_calculator
# could be more precise if we account for the variable rate after the fixed contract
r = interest_rate/100.0/12.0
P = initial_debt
N = mortgage_term*12.0 # total number of month of the fix rate


def get_monthly_repayment(r, P, N):
    return (r*P) / (1-(1+r)**(-N)) 

def repayment_curve(years, overpayment_month=0):
    # c: monthly_repayment
    # n: number of months
    n = years * 12
    c = get_monthly_repayment(r, P, N) + overpayment_month
    # see https://en.wikipedia.org/wiki/Mortgage_calculator
    result = (1+r)**n * P - (((1+r)**n - 1)* c )/r
    result[result < 0] = 0
    return result

#%%
import numpy as np
years = np.arange(mortgage_term+1)

print("Monthly Payment:")
print(get_monthly_repayment(r, P, N))

print("Remaining Debt per year:")
debt1 = pd.DataFrame({"years": years, "debt": repayment_curve(years)})
print(debt1)
debt1["scenario"] = "no overpayment"

print("Remaining Debt per year:")
debt2 = pd.DataFrame({"years": years, "debt": repayment_curve(years, 600)})
print(debt2)
debt2["scenario"] = "£600 per month"

df = pd.concat([debt1, debt2])

# %%
import plotly.express as px

fig = px.line(df, x="years", y="debt", color='scenario', markers=True)
fig.show()