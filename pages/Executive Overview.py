import streamlit as st
import pandas as pd
import plotly.express as px

import config
from Utils.data_loader import load_dataset
from Utils.helper import calculate_default_rate, get_average_income

st.title("Home Credit | Executive Overview")
st.caption("Home Credit Default Risk Analytics Dashboard")
st.divider()

try:
    df = load_dataset(config.DATASET_FILES["application"])
except FileNotFoundError:
    st.error("application_train.csv was not found in the Data folder.")
    st.info("Please make sure the dataset is available in the project Data folder and try again.")
    st.stop()

st.success(f"Dataset loaded successfully: {df.shape[0]} rows and {df.shape[1]} columns")

for col in ["TARGET", "AMT_INCOME_TOTAL", "AMT_CREDIT"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

if "TARGET" not in df.columns:
    st.error("TARGET column is missing from the dataset.")
    st.stop()

valid_target = df[df["TARGET"].isin([0, 1])].copy()

total_applications = len(valid_target)
total_defaults = int((valid_target["TARGET"] == 1).sum())
non_defaults = int((valid_target["TARGET"] == 0).sum())
default_rate = calculate_default_rate(valid_target)
average_income = get_average_income(valid_target["AMT_INCOME_TOTAL"]) if "AMT_INCOME_TOTAL" in valid_target.columns else 0
average_credit = get_average_income(valid_target["AMT_CREDIT"]) if "AMT_CREDIT" in valid_target.columns else 0

st.subheader("Key Performance Indicators")

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
kpi_col1.metric("Total Applications", f"{total_applications:,}")
kpi_col2.metric("Total Defaults", f"{total_defaults:,}")
kpi_col3.metric("Default Rate", f"{default_rate:.2f}%")

kpi_col4, kpi_col5, kpi_col6 = st.columns(3)
kpi_col4.metric("Non-Default Customers", f"{non_defaults:,}")
kpi_col5.metric("Average Credit Amount", f"{average_credit:,.2f}")
kpi_col6.metric("Average Income", f"{average_income:,.2f}")

st.divider()
st.subheader("Application and Credit Analysis")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    status_counts = valid_target["TARGET"].value_counts().reindex([0, 1], fill_value=0)
    status_df = pd.DataFrame(
        {
            "Loan Status": ["Non-Default", "Default"],
            "Customers": [status_counts.get(0, 0), status_counts.get(1, 0)],
        }
    )

    pie_fig = px.pie(
        status_df,
        names="Loan Status",
        values="Customers",
        hole=0.55,
        title="Default vs Non-Default Customers",
        color="Loan Status",
        color_discrete_map={"Non-Default": "#087F8C", "Default": "#DC3545"},
    )
    st.plotly_chart(pie_fig, use_container_width=True)

with chart_col1:
    bar_fig = px.bar(
        status_df,
        x="Loan Status",
        y="Customers",
        title="Application Outcome Distribution",
        color="Loan Status",
        color_discrete_map={"Non-Default": "#087F8C", "Default": "#DC3545"},
    )
    st.plotly_chart(bar_fig, use_container_width=True)

with chart_col2:
    if "AMT_CREDIT" in valid_target.columns:
        credit = valid_target["AMT_CREDIT"].dropna()
        credit = credit[credit >= 0]

        if not credit.empty:
            upper_limit = credit.quantile(0.99)
            credit_filtered = credit[credit <= upper_limit]

            hist_fig = px.histogram(
                x=credit_filtered,
                nbins=30,
                title="Loan Amount Distribution",
                labels={"x": "AMT_CREDIT", "y": "Number of Applications"},
            )
            st.plotly_chart(hist_fig, use_container_width=True)
        else:
            st.info("No valid loan amount data available.")
    else:
        st.info("AMT_CREDIT column is missing.")

st.divider()
st.subheader("Income and Credit Relationship")

if all(column in df.columns for column in ["AMT_INCOME_TOTAL", "AMT_CREDIT", "TARGET"]):
    scatter_df = df[["AMT_INCOME_TOTAL", "AMT_CREDIT", "TARGET"]].dropna().copy()
    scatter_df = scatter_df[
        (scatter_df["AMT_INCOME_TOTAL"] > 0)
        & (scatter_df["AMT_CREDIT"] > 0)
        & (scatter_df["TARGET"].isin([0, 1]))
    ]

    if not scatter_df.empty:
        if len(scatter_df) > 5000:
            scatter_df = scatter_df.sample(5000, random_state=42)

        scatter_df["Loan Status"] = scatter_df["TARGET"].map({0: "Non-Default", 1: "Default"})

        scatter_fig = px.scatter(
            scatter_df,
            x="AMT_INCOME_TOTAL",
            y="AMT_CREDIT",
            color="Loan Status",
            title="Customer Income vs Credit Amount",
            labels={"AMT_INCOME_TOTAL": "Annual Income", "AMT_CREDIT": "Credit Amount"},
            color_discrete_map={"Non-Default": "#087F8C", "Default": "#DC3545"},
            opacity=0.6,
        )
        st.plotly_chart(scatter_fig, use_container_width=True)
    else:
        st.info("No valid income and credit records available.")
else:
    st.info("Required columns for this chart are missing.")

st.divider()
st.subheader("Default Rate by Loan Type")

if "NAME_CONTRACT_TYPE" in df.columns:
    contract_df = valid_target[["NAME_CONTRACT_TYPE", "TARGET"]].dropna()
    contract_summary = (
        contract_df.groupby("NAME_CONTRACT_TYPE")
        .agg(Applications=("TARGET", "count"), Default_Rate=("TARGET", "mean"))
        .reset_index()
    )
    contract_summary["Default_Rate"] *= 100

    contract_fig = px.bar(
        contract_summary,
        x="NAME_CONTRACT_TYPE",
        y="Default_Rate",
        text="Default_Rate",
        title="Default Rate by Contract Type",
        labels={"NAME_CONTRACT_TYPE": "Contract Type", "Default_Rate": "Default Rate (%)"},
    )
    contract_fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    st.plotly_chart(contract_fig, use_container_width=True)
else:
    st.info("NAME_CONTRACT_TYPE column is missing.")


#==========================================
# Table of Contents
#==========================================
st.subheader("Sample Data Application Records")
st.dataframe(df.filter(["SK_ID_CURR", "TARGET", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "DAYS_BIRTH"]).head(5), use_container_width=True)  