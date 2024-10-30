import pandas as pd


def create_table(data: pd.DataFrame):
    """
    This function creates an HTML table from a pandas DataFrame.
    """
    return data.to_html()
