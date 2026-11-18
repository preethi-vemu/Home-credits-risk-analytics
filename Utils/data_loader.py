import pandas as pd


def load_dataset(path, columns=None):
    """Load a CSV dataset, optionally selecting a subset of columns."""
    return pd.read_csv(path, usecols=columns)
