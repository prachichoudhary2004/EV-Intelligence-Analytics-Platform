import streamlit as st
import pandas as pd

def show_dataframe(df: pd.DataFrame, height: int = 400):
    """Render a standard interactive dataframe."""
    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True
    )
