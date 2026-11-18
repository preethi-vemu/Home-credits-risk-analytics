import numpy as np
import pandas as pd


def calculate_default_rate(df):
    targets = pd.to_numeric(df["TARGET"], errors="coerce")
    valid_targets = targets[targets.isin([0, 1])]
    if valid_targets.empty:
        return 0.0
    return float(valid_targets.mean() * 100)


def get_average_income(series):
    values = pd.to_numeric(series, errors="coerce").dropna()
    return float(values.mean()) if not values.empty else 0.0


def calculate_age(df):
    days_birth = pd.to_numeric(df["DAYS_BIRTH"], errors="coerce")
    return -days_birth / 365.25


def create_age_groups(age):
    bins = [-np.inf, 25, 35, 45, 55, np.inf]
    labels = ["<= 25", "26-35", "36-45", "46-55", "56+"]
    return pd.cut(age, bins=bins, labels=labels, include_lowest=True)


def create_income_groups(income):
    bins = [-np.inf, 100000, 200000, 500000, np.inf]
    labels = ["Below 100K", "100K-200K", "200K-500K", "Above 500K"]
    return pd.cut(income, bins=bins, labels=labels, include_lowest=True)
