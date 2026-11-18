
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

import config
from Utils.data_loader import load_dataset


st.title("Income & Employment")

st.caption(
    "Analyze customer income levels, employment profile, "
    "and their relationship with loan default risk."
)


# ==========================================
# LOAD DATASET
# ==========================================

try:
    df = load_dataset(
        config.DATASET_FILES["application"]
    )

except FileNotFoundError:
    st.error("application_train.csv was not found.")
    st.stop()


# ==========================================
# DATA VALIDATION
# ==========================================

required_columns = [
    "SK_ID_CURR",
    "NAME_CONTRACT_TYPE",
    "OCCUPATION_TYPE",
    "NAME_INCOME_TYPE",
    "AMT_INCOME_TOTAL",
    "DAYS_EMPLOYED",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "TARGET"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.stop()


# ==========================================
# DATA PREPARATION
# ==========================================

numeric_columns = [
    "AMT_INCOME_TOTAL",
    "DAYS_EMPLOYED",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "TARGET"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df = df[
    df["TARGET"].isin([0, 1])
].copy()



categorical_columns = [
    "NAME_CONTRACT_TYPE",
    "OCCUPATION_TYPE",
    "NAME_INCOME_TYPE"
]

for col in categorical_columns:
    df[col] = df[col].fillna("Unknown")


# ------------------------------------------
# EMPLOYMENT STATUS
# ------------------------------------------

# In Home Credit, 365243 is a special value
# representing missing/unemployed employment data.

df["EMPLOYMENT_STATUS"] = np.where(
    df["DAYS_EMPLOYED"] == 365243,
    "Unemployed",
    "Employed"
)


# ------------------------------------------
# EMPLOYMENT DURATION IN YEARS
# ------------------------------------------

df["EMPLOYMENT_YEARS"] = np.where(
    (df["DAYS_EMPLOYED"] < 0) &
    (df["DAYS_EMPLOYED"] != 365243),
    -df["DAYS_EMPLOYED"] / 365.25,
    np.nan
)


# ------------------------------------------
# EMPLOYMENT DURATION GROUPS
# ------------------------------------------

employment_bins = [
    0, 1, 3, 5, 10, 15, 20, np.inf
]

employment_labels = [
    "0–1",
    "1–3",
    "3–5",
    "5–10",
    "10–15",
    "15–20",
    "20+"
]

df["EMPLOYMENT_GROUP"] = pd.cut(
    df["EMPLOYMENT_YEARS"],
    bins=employment_bins,
    labels=employment_labels,
    right=False
)


# ==========================================
# FILTER SECTION
# ==========================================

st.subheader(" Filters")

# Reset all filters
if st.button(" Reset Filters"):

    filter_keys = [
        "contract_filter",
        "occupation_filter",
        "income_type_filter",
        "target_filter"
    ]

    for key in filter_keys:
        st.session_state[key] = "All"

    st.rerun()


filter1, filter2, filter3, filter4 = st.columns(4)



with filter1:

    contract_options = [
        "All"
    ] + sorted(
        df["NAME_CONTRACT_TYPE"].unique().tolist()
    )

    contract_filter = st.selectbox(
        "Contract Type",
        contract_options,
        key="contract_filter"
    )


# Occupation Type Filter
with filter2:

    occupation_options = [
        "All"
    ] + sorted(
        df["OCCUPATION_TYPE"].unique().tolist()
    )

    occupation_filter = st.selectbox(
        "Occupation Type",
        occupation_options,
        key="occupation_filter"
    )


# Income Type Filter
with filter3:

    income_type_options = [
        "All"
    ] + sorted(
        df["NAME_INCOME_TYPE"].unique().tolist()
    )

    income_type_filter = st.selectbox(
        "Income Type",
        income_type_options,
        key="income_type_filter"
    )


# Target Filter
with filter4:

    target_filter = st.selectbox(
        "Target (Default)",
        [
            "All",
            "Non-default",
            "Default"
        ],
        key="target_filter"
    )


# ==========================================
# APPLY FILTERS
# ==========================================

filtered_df = df.copy()


# Contract Type
if contract_filter != "All":

    filtered_df = filtered_df[
        filtered_df["NAME_CONTRACT_TYPE"]
        == contract_filter
    ]


# Occupation Type
if occupation_filter != "All":

    filtered_df = filtered_df[
        filtered_df["OCCUPATION_TYPE"]
        == occupation_filter
    ]


# Income Type
if income_type_filter != "All":

    filtered_df = filtered_df[
        filtered_df["NAME_INCOME_TYPE"]
        == income_type_filter
    ]


# Target
if target_filter == "Non-default":

    filtered_df = filtered_df[
        filtered_df["TARGET"] == 0
    ]

elif target_filter == "Default":

    filtered_df = filtered_df[
        filtered_df["TARGET"] == 1
    ]


st.divider()


# ==========================================
# CHECK FILTERED DATA
# ==========================================

if filtered_df.empty:

    st.warning(
        "No customer records found for the selected filters."
    )
    st.stop()


# ==========================================
# KPI METRICS
# ==========================================

st.subheader("Income & Employment Overview")


total_customers = len(filtered_df)

average_income = (
    filtered_df["AMT_INCOME_TOTAL"].mean()
)

median_income = (
    filtered_df["AMT_INCOME_TOTAL"].median()
)


# Employment counts
employed_customers = (
    filtered_df["EMPLOYMENT_STATUS"] == "Employed"
).sum()

unemployed_customers = (
    filtered_df["EMPLOYMENT_STATUS"] == "Unemployed"
).sum()


employed_percentage = (
    employed_customers / total_customers
) * 100

unemployed_percentage = (
    unemployed_customers / total_customers
) * 100


# Average employment duration
average_employment_days = (
    filtered_df["EMPLOYMENT_YEARS"].mean()
    * 365.25
)

average_employment_years = (
    filtered_df["EMPLOYMENT_YEARS"].mean()
)


# Default rate among employed customers
employed_df = filtered_df[
    filtered_df["EMPLOYMENT_STATUS"] == "Employed"
]

if not employed_df.empty:

    employed_default_rate = (
        employed_df["TARGET"].mean() * 100
    )

else:
    employed_default_rate = np.nan


# ==========================================
# DISPLAY SIX KPI CARDS
# ==========================================

k1, k2, k3, k4, k5, k6 = st.columns(6)


with k1:

    st.metric(
        "Average Income",
        f"{average_income:,.0f}"
    )


with k2:

    st.metric(
        "Median Income",
        f"{median_income:,.0f}"
    )


with k3:

    st.metric(
        "Avg. Employment Duration",
        (
            f"{average_employment_years:.2f} years"
            if pd.notna(average_employment_years)
            else "N/A"
        ),
        (
            f"{average_employment_days:,.0f} days"
            if pd.notna(average_employment_days)
            else None
        )
    )


with k4:

    st.metric(
        "Employed Customers",
        f"{employed_percentage:.2f}%",
        f"{employed_customers:,} of {total_customers:,}"
    )


with k5:

    st.metric(
        "Unemployed Customers",
        f"{unemployed_percentage:.2f}%",
        f"{unemployed_customers:,} of {total_customers:,}"
    )


with k6:

    st.metric(
        "Default Rate (Employed)",
        (
            f"{employed_default_rate:.2f}%"
            if pd.notna(employed_default_rate)
            else "N/A"
        )
    )


st.caption(
    f"Total Applications: {total_customers:,}"
)

st.divider()


# ==========================================
# CHART 1: INCOME DISTRIBUTION
# ==========================================

st.subheader("Income Distribution")

chart1, chart2, chart3 = st.columns(3)


with chart1:

    income_data = filtered_df[
        "AMT_INCOME_TOTAL"
    ].dropna()

    income_data = income_data[
        income_data >= 0
    ]

    if not income_data.empty:

        fig1 = px.histogram(
            income_data,
            x="AMT_INCOME_TOTAL",
            nbins=40,
            title="Income Distribution",
            labels={
                "AMT_INCOME_TOTAL": "Total Income",
                "count": "Number of Customers"
            },
            color_discrete_sequence=[
                "#047857"
            ]
        )

        fig1.update_layout(
            template="plotly_white",
            bargap=0.05
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    else:

        st.info("Income data is unavailable.")


# ==========================================
# CHART 2: AVERAGE INCOME BY OCCUPATION
# ==========================================

with chart2:

    occupation_summary = (
        filtered_df[
            filtered_df["OCCUPATION_TYPE"] != "Unknown"
        ]
        .groupby("OCCUPATION_TYPE")
        .agg(
            Customers=("TARGET", "count"),
            Average_Income=("AMT_INCOME_TOTAL", "mean")
        )
        .reset_index()
        .sort_values(
            "Average_Income",
            ascending=False
        )
        .head(8)
    )

    if not occupation_summary.empty:

        fig2 = px.bar(
            occupation_summary,
            x="Average_Income",
            y="OCCUPATION_TYPE",
            orientation="h",
            text="Average_Income",
            title="Average Income by Occupation (Top 8)",
            labels={
                "Average_Income": "Average Income",
                "OCCUPATION_TYPE": "Occupation"
            },
            color_discrete_sequence=[
                "#047857"
            ]
        )

        fig2.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside"
        )

        fig2.update_layout(
            template="plotly_white",
            yaxis={
                "categoryorder": "total ascending"
            }
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:

        st.info("Occupation data is unavailable.")


# ==========================================
# CHART 3: EMPLOYMENT DURATION DISTRIBUTION
# ==========================================

with chart3:

    employment_summary = (
        filtered_df[
            filtered_df["EMPLOYMENT_GROUP"].notna()
        ]
        ["EMPLOYMENT_GROUP"]
        .value_counts(sort=False)
        .reset_index()
    )

    employment_summary.columns = [
        "Employment Duration",
        "Customers"
    ]

    if not employment_summary.empty:

        fig3 = px.bar(
            employment_summary,
            x="Employment Duration",
            y="Customers",
            title="Employment Duration Distribution",
            color_discrete_sequence=[
                "#D4A017"
            ]
        )

        fig3.update_layout(
            template="plotly_white",
            xaxis_title="Employment Duration (Years)",
            yaxis_title="Number of Customers"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    else:

        st.info("Employment duration data is unavailable.")


st.divider()


# ==========================================
# CHART 4: DEFAULT RATE BY OCCUPATION
# ==========================================

chart4, chart5 = st.columns(2)


with chart4:

    occupation_risk = (
        filtered_df[
            filtered_df["OCCUPATION_TYPE"] != "Unknown"
        ]
        .groupby("OCCUPATION_TYPE")
        .agg(
            Customers=("TARGET", "count"),
            Default_Rate=("TARGET", "mean")
        )
        .reset_index()
    )

    occupation_risk = (
        occupation_risk
        .sort_values(
            "Default_Rate",
            ascending=False
        )
        .head(8)
    )

    occupation_risk["Default_Rate"] *= 100

    if not occupation_risk.empty:

        fig4 = px.bar(
            occupation_risk,
            x="OCCUPATION_TYPE",
            y="Default_Rate",
            text="Default_Rate",
            title="Default Rate by Occupation",
            color_discrete_sequence=[
                "#D4A017"
            ]
        )

        fig4.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        fig4.update_layout(
            template="plotly_white",
            xaxis_title="Occupation",
            yaxis_title="Default Rate (%)"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

    else:

        st.info("Occupation default data unavailable.")


# ==========================================
# CHART 5: INCOME VS CREDIT AMOUNT
# ==========================================

with chart5:

    scatter_df = filtered_df[
        [
            "AMT_INCOME_TOTAL",
            "AMT_CREDIT"
        ]
    ].dropna()

    scatter_df = scatter_df[
        (scatter_df["AMT_INCOME_TOTAL"] >= 0) &
        (scatter_df["AMT_CREDIT"] >= 0)
    ]

    if len(scatter_df) > 5000:

        scatter_df = scatter_df.sample(
            n=5000,
            random_state=42
        )

    correlation_df = filtered_df[
        [
            "AMT_INCOME_TOTAL",
            "AMT_CREDIT"
        ]
    ].dropna()

    correlation = correlation_df[
        "AMT_INCOME_TOTAL"
    ].corr(
        correlation_df["AMT_CREDIT"]
    )

    if not scatter_df.empty:

        fig5 = px.scatter(
            scatter_df,
            x="AMT_INCOME_TOTAL",
            y="AMT_CREDIT",
            title="Income vs. Credit Amount",
            labels={
                "AMT_INCOME_TOTAL": "Total Income",
                "AMT_CREDIT": "Credit Amount"
            },
            color_discrete_sequence=[
                "#047857"
            ],
            opacity=0.6
        )

        fig5.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig5,
            use_container_width=True
        )

        st.metric(
            "Correlation (Income, Credit)",
            (
                f"r = {correlation:.2f}"
                if pd.notna(correlation)
                else "N/A"
            )
        )

    else:

        st.info("Income and credit data unavailable.")


st.divider()


# ==========================================
# CUSTOMER INCOME & EMPLOYMENT DETAILS
# ==========================================

st.subheader(" Customer Income & Employment Details")


table_columns = [
    "SK_ID_CURR",
    "AMT_INCOME_TOTAL",
    "NAME_INCOME_TYPE",
    "OCCUPATION_TYPE",
    "DAYS_EMPLOYED",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "TARGET"
]


table_columns = [
    col for col in table_columns
    if col in filtered_df.columns
]


display_df = filtered_df[
    table_columns
].head(10)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# DOWNLOAD CSV
# ==========================================

# csv_data = filtered_df[
#     table_columns
# ].to_csv(index=False).encode("utf-8")


# st.download_button(
#     label="⬇️ Download Data (CSV)",
#     data=csv_data,
#     file_name="income_employment_analysis.csv",
#     mime="text/csv"
# )


# st.caption(
#     f"Showing {min(100, len(filtered_df)):,} "
#     f"of {len(filtered_df):,} customers."
# )