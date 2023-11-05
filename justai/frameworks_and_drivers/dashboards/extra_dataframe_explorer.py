import pandas as pd
import streamlit as st
from pandas.api.types import is_object_dtype, is_numeric_dtype, is_categorical_dtype, is_datetime64_any_dtype
from typing import Any, Dict


def dataframe_explorer(df: pd.DataFrame, case: bool = True) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe
        case (bool, optional): If True, text inputs will be case sensitive. Defaults to True.

    Returns:
        pd.DataFrame: Filtered dataframe
    """

    df = df.copy()

    # Try to convert datetimes into standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    # Generate a random key base for Streamlit components
    random_key_base = str(pd.util.hash_pandas_object(df.select_dtypes(exclude='object')).sum())

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect(
            "Filter dataframe on",
            df.columns,
            key=f"{random_key_base}_multiselect",
        )
        filters: Dict[str, Any] = dict()
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Check if the column contains list-type data
            if df[column].apply(lambda x: isinstance(x, list)).any():
                # Skip nunique and unique checks for list-type columns
                continue
            # Continue with the rest of the checks for other data types
            elif is_categorical_dtype(df[column]) or len(pd.unique(df[column])) < 10:
                left.write("↳")
                filters[column] = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                    key=f"{random_key_base}_{column}",
                )
                df = df[df[column].isin(filters[column])]
            elif is_numeric_dtype(df[column]):
                left.write("↳")
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                filters[column] = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                    key=f"{random_key_base}_{column}",
                )
                df = df[df[column].between(*filters[column])]
            elif is_datetime64_any_dtype(df[column]):
                left.write("↳")
                filters[column] = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                    key=f"{random_key_base}_{column}",
                )
                if len(filters[column]) == 2:
                    filters[column] = tuple(map(pd.to_datetime, filters[column]))
                    start_date, end_date = filters[column]
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                left.write("↳")
                filters[column] = right.text_input(
                    f"Pattern in {column}",
                    key=f"{random_key_base}_{column}",
                )
                if filters[column]:
                    df = df[df[column].str.contains(filters[column], case=case)]

# Identify columns that contain lists
    list_cols = [col for col in df.columns if df[col].apply(lambda x: isinstance(x, list)).any()]

    # Generate a random key base for Streamlit components
    # Exclude list columns from hashing to prevent TypeError
    random_key_base = str(pd.util.hash_pandas_object(df.drop(columns=list_cols)).sum())
    # Now handle filtering for list-type columns after other filters
    for column in list_cols:
        if column in to_filter_columns:
            # Flatten all the lists to find unique elements
            unique_elements = set(x for sublist in df[column].dropna() for x in sublist)
            selected_elements = st.multiselect(
                f"Select tags for {column}",
                options=list(unique_elements),
                key=f"{random_key_base}_{column}_list"
            )
            if selected_elements:
                # Filter rows where column list intersects with selected elements
                df = df[df[column].apply(lambda x: bool(set(x) & set(selected_elements)))]

    return df
