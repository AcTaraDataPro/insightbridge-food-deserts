import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai

@st.cache_data
def load_data():
    return pd.read_csv("usda_food_access_full.csv")

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

# Filter data
filtered_df = df[
    (df["State"] == selected_state) &
    (df["County"] == selected_county) &
    (df["MedianFamilyIncome"] >= selected_income[0]) &
    (df["MedianFamilyIncome"] <= selected_income[1])
]

# Layout
col1, col2 = st.columns([3, 2])

with col1:
    st.title("🍎 InsightBridge: Food Desert Explorer")
    st.subheader(f"{selected_county} County, {selected_state}")

    if not filtered_df.empty:
        sizes = filtered_df["LILATracts_1And10"].value_counts().sort_index()
        labels = ["Not Food Desert", "Food Desert"] if 0 in sizes.index else ["Food Desert"]
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

        num_tracts = len(filtered_df)
        num_food_deserts = filtered_df["LILATracts_1And10"].sum()
        snap_avg = filtered_df["TractSNAP"].mean() * 100
        vehicle_access = filtered_df["TractHUNVFlag"].sum()

        st.markdown("### 🧠 Insight")
        st.success(
            f"In {selected_county} County, {selected_state}, {num_food_deserts} out of {num_tracts} census tracts "
            f"are identified as food deserts. The average SNAP participation rate is {snap_avg:.1f}%, and "
            f"{vehicle_access} tracts have limited vehicle access, indicating food access mobility challenges."
        )
    else:
        st.warning("No data available for selected filters.")

with col2:
    st.header("💬 Ask InsightBridge")
    openai_key = st.text_input("Enter your OpenAI API Key", type="password")
    user_question = st.text_area("Ask a question about the data:")

    if st.button("Get Answer") and openai_key and user_question:
        openai.api_key = openai_key
        context_summary = filtered_df.describe(include='all').to_string()
        prompt = f"Data context:
{context_summary}

User question: {user_question}"

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant helping explain public health data related to food access."},
                    {"role": "user", "content": prompt}
                ]
            )
            st.success(response.choices[0].message["content"])
        except Exception as e:
            st.error(f"Error: {str(e)}")
