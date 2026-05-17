import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide")
st.sidebar.title("💰 Mortgage Simulator")
initial_debt = st.sidebar.number_input("Initial Debt", value=125000) # £
mortgage_term = st.sidebar.number_input("Mortgage Term", value=25) # years
interest_rate = st.sidebar.number_input("Interest Rate", value=5.07) #%
overpayment = st.sidebar.number_input("Overpayment",value=600) #per month

# also good for comparison: https://moneyfactscompare.co.uk/
# formula gives same results as https://www.moneysavingexpert.com/mortgages/mortgage-overpayment-calculator/
# and can be found on wikipedia: https://en.wikipedia.org/wiki/Mortgage_calculator
# could be more precise if we account for the variable rate after the fixed contract
r = interest_rate/100.0/12.0
P = initial_debt
N = mortgage_term*12.0 # total number of month of the fix rate
years = np.arange(mortgage_term+1)


def get_monthly_repayment():
    return (r*P) / (1-(1+r)**(-N)) 

def repayment_curve(years, overpayment_month=0):
    # c: monthly_repayment
    # n: number of months
    n = years * 12
    c = get_monthly_repayment() + overpayment_month
    # see https://en.wikipedia.org/wiki/Mortgage_calculator
    result = (1+r)**n * P - (((1+r)**n - 1)* c )/r
    result[result < 0] = 0
    return result


c1, c2, c3 = st.columns([2,1,1])
c1.write(f"Monthly Payment: :blue[£{round(get_monthly_repayment(),2)}]")

c2.write("No Overpayment:")
debt1 = pd.DataFrame({"years": years, "debt": repayment_curve(years)})
c2.table(debt1)
debt1["scenario"] = "no overpayment"

c3.write(f"Overpayment of £{overpayment}")
debt2 = pd.DataFrame({"years": years, "debt": repayment_curve(years, overpayment)})
c3.table(debt2, height="stretch")
debt2["scenario"] = f"£{overpayment} per month"

df = pd.concat([debt1, debt2])


c1.write("Remaining Debt per year:")
fig = px.line(df, x="years", y="debt", color='scenario', markers=True)
fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.99
))
c1.plotly_chart(fig,width=800, height=500)
