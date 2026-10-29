import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

# ---------------------------------
# Sidebar Navigation
# ---------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Upload Data", "Charts", "Custom Logic"])

# ---------------------------------
# Home Page
# ---------------------------------
if page == "Home":
    st.title("🚀 Streamlit Starter App")
    st.subheader("Main Features Showcased:")
    st.markdown("""
    - 📑 **Navigation** with sidebar
    - 📂 **Upload CSV/Excel files**
    - 📊 **Charts with Matplotlib, Altair, and Plotly**
    - ⚙️ **Custom logic (interactive forms, calculators, etc.)**
    - ⚡ **Caching for performance**
    """)
    st.info("Use the sidebar to explore each feature.")

# ---------------------------------
# Upload Data Page
# ---------------------------------
elif page == "Upload Data":
    st.title("📂 Upload Your Data")
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

    @st.cache_data
    def load_data(file):
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)

    if uploaded_file:
        df = load_data(uploaded_file)
        st.success("File uploaded successfully!")
        st.dataframe(df.head())  # Show preview

# ---------------------------------
# Charts Page
# ---------------------------------
elif page == "Charts":
    st.title("📊 Data Visualization Showcase")

    # Example data
    df = pd.DataFrame({
        "Category": ["A", "B", "C", "D"],
        "Value": [23, 45, 12, 67]
    })

    st.subheader("Matplotlib Chart")
    fig, ax = plt.subplots()
    ax.bar(df["Category"], df["Value"], color="skyblue")
    ax.set_title("Matplotlib Bar Chart")
    st.pyplot(fig)

    st.subheader("Altair Chart")
    chart = alt.Chart(df).mark_bar().encode(
        x="Category",
        y="Value",
        tooltip=["Category", "Value"]
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Plotly Chart")
    fig2 = px.line(df, x="Category", y="Value", title="Plotly Line Chart")
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------
# Custom Logic Page
# ---------------------------------
elif page == "Custom Logic":
    st.title("⚙️ Custom Logic Example")

    st.subheader("Simple Calculator")
    num1 = st.number_input("Enter first number:", value=0.0)
    num2 = st.number_input("Enter second number:", value=0.0)
    operation = st.selectbox("Choose operation:", ["Add", "Subtract", "Multiply", "Divide"])

    if st.button("Calculate"):
        if operation == "Add":
            result = num1 + num2
        elif operation == "Subtract":
            result = num1 - num2
        elif operation == "Multiply":
            result = num1 * num2
        elif operation == "Divide":
            result = num1 / num2 if num2 != 0 else "Error: Division by zero"
        st.success(f"Result: {result}")

    st.subheader("Conditional UI Example")
    choice = st.radio("Do you like Streamlit?", ["Yes", "No"])
    if choice == "Yes":
        st.balloons()
        st.success("Awesome! 🎉 Streamlit is great for rapid prototyping.")
    else:
        st.warning("No worries, maybe give it another try!")

