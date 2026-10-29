# Streamlit Basics

Streamlit is an open-source app framework for Machine Learning and Data Science projects. It allows you to create beautiful web apps for your machine learning projects with minimal effort.

## Installation

To install Streamlit, run the following command in your terminal:

```bash
pip install streamlit
```

## Creating Your First Streamlit App

1. Create a new Python file called `app.py`.
2. Add the following code to `app.py`:

```python
import streamlit as st

st.title("My First Streamlit App")
st.write("Hello, world!")
```

3. Run the app with the following command:

```bash
streamlit run app.py
```

4. Open your web browser and go to `http://localhost:8501` to see your app.

## Streamlit Components

Streamlit provides a variety of components to build your app, including:

- **Text**: Display text with `st.write()`, `st.title()`, and other text functions.
- **Widgets**: Add interactivity with widgets like sliders, buttons, and text inputs.
- **Charts**: Visualize data with built-in charting functions.

## Example: Building a Simple Data Explorer

Here's a simple example of a data explorer app using Streamlit:

```python
import streamlit as st
import pandas as pd

# Load data
df = pd.read_csv("data.csv")

# Sidebar filters
st.sidebar.header("Filters")
selected_column = st.sidebar.selectbox("Select a column", df.columns)

# Display data
st.write("## Data Preview")
st.write(df[selected_column])
```

This app allows users to select a column from a DataFrame and displays the data for that column.

## Conclusion

Streamlit is a powerful tool for building interactive web apps for your data science projects. With just a few lines of code, you can create beautiful visualizations and user interfaces.
