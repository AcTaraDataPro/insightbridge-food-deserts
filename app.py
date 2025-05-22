import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("usda_food_access_sample.csv")

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Options")
states = df["State"].unique()
selected_state = st.sidebar.selectbox("Select State", sorted(states))

counties = df[df["State"] == selected_state]["County"].unique()
selected_county = st.sidebar.selectbox("Select County", sorted(counties))

income_min = int(df["MedianFamilyIncome"].min())
income_max = int(df["MedianFamilyIncome"].max())
selected_income = st.sidebar.slider("Select Income Range", income_min, income_max, (income_min, income_max))

# Apply filters
filtered_df = df[
    (df["State"] == selected_state) &
    (df["County"] == selected_county) &
    (df["MedianFamilyIncome"] >= selected_income[0]) &
    (df["MedianFamilyIncome"] <= selected_income[1])
]

# Main app
st.title("🍎 InsightBridge: Food Desert Analysis")
st.subheader(f"{selected_county} County, {selected_state}")

# Pie chart
if not filtered_df.empty:
    sizes = filtered_df["LILATracts_1And10"].value_counts().sort_index()
    labels = ["Not Food Desert", "Food Desert"] if 0 in sizes.index else ["Food Desert"]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # Summary
    num_tracts = len(filtered_df)
    num_food_deserts = filtered_df["LILATracts_1And10"].sum()
    snap_avg = filtered_df["TractSNAP"].mean() * 100
    vehicle_access = filtered_df["TractHUNVFlag"].sum()

    st.markdown("### 🧠 Insight")
    st.success(
        f"In {selected_county} County, {selected_state}, {num_food_deserts} out of {num_tracts} census tracts "
        f"are identified as food deserts (low-income and low-access). The average SNAP participation rate is "
        f"{snap_avg:.1f}%, and {vehicle_access} tracts have limited vehicle access, indicating potential mobility "
        f"challenges for food-insecure populations."
    )
else:
    st.warning("No data available for selected filters.")
