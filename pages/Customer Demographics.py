
import streamlit as st
import config
import pandas as pd
import plotly.express as px

from Utils.data_loader import load_dataset
from Utils.helper import calculate_age, create_age_groups, create_income_groups


st.title(" Customer Demographics")
st.caption(
    "Analysis of customer age, gender, family status, "
    "education and default risk."
)

st.divider()


# ==========================================
# LOAD DATASET
# ==========================================

try:
    df = load_dataset(config.DATASET_FILES["application"])

except FileNotFoundError:
    st.error("application_train.csv was not found in the Data folder.")
    st.info("Please check your dataset path.")
    st.stop()


# ==========================================
# DATA VALIDATION
# ==========================================

required_columns = ["TARGET"]

for column in required_columns:
    if column not in df.columns:
        st.error(f"{column} column is missing from the dataset.")
        st.stop()


# Convert TARGET into numeric format
df["TARGET"] = pd.to_numeric(
    df["TARGET"],
    errors="coerce"
)


# ==========================================
# DATA PREPARATION
# ==========================================

# Calculate customer age
df["AGE"] = calculate_age(df)

# Create age groups
df["AGE_GROUP"] = create_age_groups(df["AGE"])


# Create income groups
if "AMT_INCOME_TOTAL" in df.columns:

    df["AMT_INCOME_TOTAL"] = pd.to_numeric(
        df["AMT_INCOME_TOTAL"],
        errors="coerce"
    )

    df["INCOME_GROUP"] = create_income_groups(
        df["AMT_INCOME_TOTAL"]
    )

# ==========================================
# KPI METRICS - CUSTOMER DEMOGRAPHICS
# ==========================================

st.subheader("Customer Overview")

# Calculate KPI values

total_customers = len(df)

male_customers = (df["CODE_GENDER"] == "M").sum()
female_customers = (df["CODE_GENDER"] == "F").sum()

male_percentage = (male_customers / total_customers) * 100
female_percentage = (female_customers / total_customers) * 100

average_age = df["AGE"].mean()

married_customers = (
    df["NAME_FAMILY_STATUS"] == "Married"
).sum()

married_percentage = (
    married_customers / total_customers
) * 100

average_family_size = df["CNT_FAM_MEMBERS"].mean()

customers_with_children = (
    df["CNT_CHILDREN"] > 0
).sum()

children_percentage = (
    customers_with_children / total_customers
) * 100


# Display KPI Metrics

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        label=" Male Customers",
        value=f"{male_customers:,}",
        delta=f"{male_percentage:.2f}%"
    )

with col2:
    st.metric(
        label=" Female Customers",
        value=f"{female_customers:,}",
        delta=f"{female_percentage:.2f}%"
    )

with col3:
    st.metric(
        label="Average Age",
        value=f"{average_age:.2f} Years"
    )

with col4:
    st.metric(
        label=" Married Customers",
        value=f"{married_percentage:.2f}%",
        delta=f"{married_customers:,} Customers"
    )

with col5:
    st.metric(
        label=" Average Family Size",
        value=f"{average_family_size:.2f}"
    )

with col6:
    st.metric(
        label=" Customers with Children",
        value=f"{children_percentage:.2f}%",
        delta=f"{customers_with_children:,} Customers"
    )

st.divider()

# ==========================================
# AGE DISTRIBUTION ANALYSIS
# ==========================================

st.subheader(" Age Distribution Analysis")

age_data = df["AGE"].dropna()

if not age_data.empty:

    fig_age = px.histogram(
        age_data,
        x="AGE",
        nbins=30,
        title="Distribution of Customers by Age",
        labels={
            "AGE": "Age (Years)",
            "count": "Number of Customers"
        },
        color_discrete_sequence=[config.CHART_COLORS[0]]
    )

    fig_age.update_layout(
        bargap=0.1,
        template="plotly_white",
        xaxis_title="Age (Years)",
        yaxis_title="Number of Customers"
    )

    st.plotly_chart(
        fig_age,
        use_container_width=True
    )

else:
    st.info("No valid age data available.")

st.divider()


# ==========================================
# GENDER DISTRIBUTION ANALYSIS
# ==========================================

st.subheader(" Gender Distribution Analysis")

if "CODE_GENDER" in df.columns:

    gender_df = (
        df["CODE_GENDER"]
        .value_counts()
        .reset_index()
    )

    gender_df.columns = ["Gender", "Customers"]

    # Replace gender codes with readable names
    gender_df["Gender"] = gender_df["Gender"].replace({
        "M": "Male",
        "F": "Female"
    })

    fig_gender = px.pie(
        gender_df,
        names="Gender",
        values="Customers",
        hole=0.5,
        title="Distribution of Customers by Gender",
        color_discrete_sequence=[
            config.CHART_COLORS[1],
            config.CHART_COLORS[2]
        ]
    )

    fig_gender.update_traces(
        textinfo="percent+label"
    )

    fig_gender.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_gender,
        use_container_width=True
    )

else:
    st.info("CODE_GENDER column is missing.")

st.divider()


# ==========================================
# FAMILY STATUS DISTRIBUTION
# ==========================================

st.subheader("Family Status Distribution")

if "NAME_FAMILY_STATUS" in df.columns:

    family_df = (
        df["NAME_FAMILY_STATUS"]
        .value_counts()
        .reset_index()
    )

    family_df.columns = [
        "Family Status",
        "Customers"
    ]

    fig_family = px.bar(
        family_df,
        x="Family Status",
        y="Customers",
        title="Customers by Family Status",
        text="Customers",
        color="Family Status",
        color_discrete_sequence=config.CHART_COLORS
    )

    fig_family.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_family.update_layout(
        template="plotly_white",
        showlegend=False,
        xaxis_title="Family Status",
        yaxis_title="Number of Customers"
    )

    st.plotly_chart(
        fig_family,
        use_container_width=True
    )

else:
    st.info("NAME_FAMILY_STATUS column is missing.")

st.divider()


# ==========================================
# DEFAULT RATE BY EDUCATION
# ==========================================

st.subheader("Default Rate by Education")

if "NAME_EDUCATION_TYPE" in df.columns:

    edu_df = df[
        ["NAME_EDUCATION_TYPE", "TARGET"]
    ].dropna()

    if not edu_df.empty:

        edu_summary = (
            edu_df.groupby(
                "NAME_EDUCATION_TYPE",
                observed=False
            )
            .agg(
                Customers=("TARGET", "count"),
                Default_Rate=("TARGET", "mean")
            )
            .reset_index()
        )

      
        edu_summary["Default_Rate"] *= 100

        # Horizontal bar chart
        fig_edu = px.bar(
            edu_summary,
            x="Default_Rate",
            y="NAME_EDUCATION_TYPE",
            orientation="h",
            text="Default_Rate",
            title="Default Rate by Education",
            labels={
                "Default_Rate": "Default Rate (%)",
                "NAME_EDUCATION_TYPE": "Education Type"
            },
            color_discrete_sequence=[
                config.CHART_COLORS[3]
            ]
        )

        fig_edu.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        fig_edu.update_layout(
            template="plotly_white",
            xaxis_title="Default Rate (%)",
            yaxis_title="Education Type"
        )

        st.plotly_chart(
            fig_edu,
            use_container_width=True
        )

    else:
        st.info("Education data is not available.")

else:
    st.info("NAME_EDUCATION_TYPE column is missing.")

st.divider()


# ==========================================
# DEFAULT RATE BY AGE GROUP
# ==========================================

st.subheader("📈 Default Rate by Age Group")

age_risk_df = df[
    ["AGE_GROUP", "TARGET"]
].dropna()

if not age_risk_df.empty:

    age_summary = (
        age_risk_df.groupby(
            "AGE_GROUP",
            observed=False
        )
        .agg(
            Customers=("TARGET", "count"),
            Default_Rate=("TARGET", "mean")
        )
        .reset_index()
    )

    # Convert into percentage
    age_summary["Default_Rate"] *= 100

    fig_age_risk = px.line(
        age_summary,
        x="AGE_GROUP",
        y="Default_Rate",
        markers=True,
        text="Default_Rate",
        title="Default Rate Across Age Groups",
        labels={
            "AGE_GROUP": "Age Group",
            "Default_Rate": "Default Rate (%)"
        },
        color_discrete_sequence=[
            config.CHART_COLORS[4]
        ]
    )

    fig_age_risk.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="top center",
        fill="tozeroy"
    )

    fig_age_risk.update_layout(
        template="plotly_white",
        xaxis_title="Age Group",
        yaxis_title="Default Rate (%)"
    )

    st.plotly_chart(
        fig_age_risk,
        use_container_width=True
    )

else:
    st.info("Age group data is unavailable.")

st.divider()


# ==========================================
# CUSTOMER DATA PREVIEW
# ==========================================

st.subheader("Customer Data Preview")

with st.expander("View Customer Demographics Data"):

    columns_to_show = [
        "SK_ID_CURR",
        "CODE_GENDER",
        "DAYS_BIRTH",
        "NAME_FAMILY_STATUS",
        "NAME_EDUCATION_TYPE",
        "CNT_CHILDREN",
        "CNT_FAM_MEMBERS",
        "TARGET"
    ]

  
    columns_to_show = [
        column
        for column in columns_to_show
        if column in df.columns
    ]

    st.dataframe(
        df[columns_to_show].head(10),
        use_container_width=True,
        hide_index=True
    )

st.caption(
    f"Showing 20 of {len(df):,} customer records."
)