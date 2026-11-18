import streamlit as st


st.set_page_config(
    page_title="Home Credit Default Risk Analytics",
    layout="wide",
)

pages = [
    st.Page("pages/Executive Overview.py", title="Executive Overview"),
    st.Page("Loan Application Analysis.py", title="Loan Application"),
    st.Page("pages/Customer Demographics.py", title="Customer Demographics"),
    st.Page("Default Risk Analysis.py", title="Default Risk"),
    st.Page("Income & Employment.py", title="Income & Employment"),
    st.Page("Credit Bureau Analysis.py", title="Credit Bureau"),
]

navigation = st.navigation(pages, position="sidebar")
navigation.run()
