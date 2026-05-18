import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide")
st.sidebar.title("💰 Mortgage Simulator")
initial_debt = st.sidebar.number_input("Initial Debt", value=125000) # £
mortgage_term = st.sidebar.number_input("Mortgage Term", value=25) # years
interest_rate = st.sidebar.number_input("Interest Rate", value=5.07) #%
overpayment = st.sidebar.number_input("Monthly Overpayment",value=200) #per month
overpayment_perc = st.sidebar.number_input("Yearly Overpayment %",value=0) / 100. #per month

# also good for comparison: https://moneyfactscompare.co.uk/
# formula gives same results as https://www.moneysavingexpert.com/mortgages/mortgage-overpayment-calculator/
# and can be found on wikipedia: https://en.wikipedia.org/wiki/Mortgage_calculator
# could be more precise if we account for the variable rate after the fixed contract
r = interest_rate/100.0/12.0 # r = 0.004225 if rate is 5.07%
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

def one_payment(debt, repayment, overpayment=0):
    # (1+r)*P-c that is P + P*r - c
    return (1+r)*debt - repayment - overpayment

def simulate(years, overpayment=0, ovp_perc=0.0):
    #TODO: probably be better to use a monthly dataframe
    output = [P]
    yearly_overpayments = [np.nan]
    payments = []
    previous_debt = P
    c = get_monthly_repayment() 
    for month in np.arange(1, (len(years)-1) * 12 + 1):
        if month % 12 == 0:
            monthly_output = one_payment(previous_debt, c, overpayment + previous_debt * ovp_perc)
            yearly_overpayments.append(previous_debt * ovp_perc)
            payments.append(c + overpayment + previous_debt * ovp_perc if monthly_output > 0 else 0)
            output.append(monthly_output)
        else:
            monthly_output = one_payment(previous_debt, c, overpayment)
            payments.append(c + overpayment if monthly_output > 0 else 0)
        previous_debt = monthly_output
    output = np.array(output)
    output[output < 0] = 0
    yearly_overpayments = np.array(yearly_overpayments)
    yearly_overpayments[yearly_overpayments < 0] = 0
    payments = np.array(payments)
    return output, yearly_overpayments, payments

output1, yearly_overpayments1, payments1 = simulate(years)
debt1 = pd.DataFrame({"years": years, "value": output1})
debt1["caption"] = "no overpayment"
output2, yearly_overpayments2, payments2 = simulate(years, overpayment, overpayment_perc)
debt2 = pd.DataFrame({"years": years, "value": output2})
debt2["caption"] = f"with overpayment"

if overpayment > 0:
    info = pd.DataFrame({"years": years, "value": overpayment*12* (100/10.)})
    info["caption"] = f"10% overpayment limit"
    df = pd.concat([debt1, debt2, info])
elif overpayment_perc > 0:
    info = pd.DataFrame({"years": years, "value": yearly_overpayments2})
    info["caption"] = f"yearly overpayments"
    df = pd.concat([debt1, debt2, info])
else:
    df = pd.concat([debt1, debt2])


overpayments_per_year = np.bincount(np.repeat(years[1:], 12), weights=payments2 - get_monthly_repayment()) 
overpayments_per_year[overpayments_per_year<0] = 0
summary_table = pd.DataFrame({
    "years": years, "Debt (no overpayment)": output1, "Debt (with overpayment)": output2, "Overpayments": overpayments_per_year 
})


c1, c2 = st.columns([2,2])
c1.write(f"Monthly Payment: :blue[£ {round(get_monthly_repayment(),2)}] + overpayment")
totals = pd.DataFrame({
    "Total Paid (No overpayment)" : [f":blue[£ {np.sum(payments1):,.0f}]"],
    "Total Paid (With overpayment)" : [f":blue[£ {np.sum(payments2):,.0f}]"],
    "Total Saved" : [f":blue[£ {np.sum(payments1) - np.sum(payments2):,.0f}]"] 
})
c1.table(totals.T, hide_header=True, border="horizontal")

fig = px.line(df, x="years", y="value", color='caption', markers=True,
              title = "Mortgage Debt over time:")
fig.update_layout(
    legend=dict(yanchor="top",y=0.99,xanchor="right",x=0.99))
c1.plotly_chart(fig,width=800, height=500, config = {'displayModeBar': False})

c2.write("In more details:")
c2.dataframe(summary_table, height=600, width="content", column_config = {
    "Debt (no overpayment)": st.column_config.NumberColumn(format="£ %,.0f"),
    "Debt (with overpayment)": st.column_config.NumberColumn(format="£ %,.0f"),
    "Overpayments": st.column_config.NumberColumn(format="£ %,.0f")
    })


