import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load datasets
data1_path = 'Detailed Cases (Registered) sexual Assault 2001-2008.csv'
data2_path = 'State wise Sexual Assault (Detailed) 1999 - 2013.csv'

data1 = pd.read_csv(data1_path)
data2 = pd.read_csv(data2_path)

# Function to calculate KPIs
def calculate_kpis(data):
    total_cases = data["rape_cases_(total)___no._of_cases_reported"].sum()
    high_risk_age_cases = data["rape_cases_(total)_no._of_victims___(18_30)years"].sum()
    under_18_cases = (
        data[
            [
                "rape_cases_(total)_no._of_victims___upto_10_years",
                "rape_cases_(total)_no._of_victims___(10_14)_years",
                "rape_cases_(total)_no._of_victims___(14_18)_years",
            ]
        ].sum().sum()
    )
    known_offender_cases = data["no._of_cases_in_which_offenders_were_known_to_the_victims"].sum()
    mp_up_cases = data[data["state_ut"].isin(["Madhya Pradesh", "Uttar Pradesh"])]["rape_cases_(total)___no._of_cases_reported"].sum()
    mp_up_years = data.groupby("year")["state_ut"].apply(lambda x: "Madhya Pradesh" in x.values or "Uttar Pradesh" in x.values).sum()
    
    # Calculate percentages
    high_risk_percentage = (high_risk_age_cases / total_cases) * 100 if total_cases else 0
    under_18_percentage = (under_18_cases / total_cases) * 100 if total_cases else 0
    mp_up_percentage = (mp_up_cases / total_cases) * 100 if total_cases else 0
    mp_up_frequency = (mp_up_years / len(data["year"].unique())) * 100 if len(data["year"].unique()) else 0
    
    return {
        "total_cases": total_cases,
        "high_risk_percentage": high_risk_percentage,
        "under_18_percentage": under_18_percentage,
        "mp_up_percentage": mp_up_percentage,
        "mp_up_frequency": mp_up_frequency,
        "known_offender_cases": known_offender_cases,
    }


# Preprocessing
data1_cleaned = data1.fillna(0)
data1_cleaned.columns = [col.strip().replace(" ", "_").replace("-", "_").lower() for col in data1_cleaned.columns]

data2_cleaned = data2.copy()
data2_cleaned.columns = [col.strip().replace(" ", "_").replace("/", "_").lower() for col in data2_cleaned.columns]
numeric_columns = [
    "no._of_cases_in_which_offenders_were_known_to_the_victims",
    "no._of_cases_in_which_offenders_were_parents___close_family_members",
    "no._of_cases_in_which_offenders_were_relatives",
    "no._of_cases_in_which_offenders_were_neighbours",
    "no._of_cases_in_which_offenders_were_other_known_persons",
]
for col in numeric_columns:
    data2_cleaned[col] = pd.to_numeric(data2_cleaned[col], errors='coerce')
data2_cleaned.fillna(0, inplace=True)

# Merging datasets
data1_cleaned.rename(columns={'states/_uts/cities': 'state_ut'}, inplace=True)
merged_data = pd.merge(data1_cleaned, data2_cleaned, on=['state_ut', 'year'], how='inner')

# Filters
st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Select Year", ['All'] + sorted(merged_data['year'].unique()))
selected_state = st.sidebar.selectbox("Select State", ['All'] + sorted(merged_data['state_ut'].unique()))

filtered_data = merged_data.copy()
if selected_year != 'All':
    filtered_data = filtered_data[filtered_data['year'] == selected_year]
if selected_state != 'All':
    filtered_data = filtered_data[filtered_data['state_ut'] == selected_state]

# Streamlit App
st.title("Sexual Assault Data Analysis (2001-2013)")



# Calculate KPIs
kpis = calculate_kpis(filtered_data)

# Display KPIs at the top
st.header("Key Performance Indicators (KPIs)")
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Cases", f"{kpis['total_cases']:,}")
#col2.metric("High-Risk Age Group (%)", f"{kpis['high_risk_percentage']:.2f}%")
col2.metric("High-Risk Group (%)", f"{kpis['high_risk_percentage']:.2f}%")

col3.metric("Victims Below 18 (%)", f"{kpis['under_18_percentage']:.2f}%")
col4.metric("MP & UP Cases (%)", f"{kpis['mp_up_percentage']:.2f}%")


# Add additional KPIs as needed
st.metric("Known Offender Cases", f"{kpis['known_offender_cases']:,}")

st.header("Insights with Visualizations")
# List of insights and charts
insights = [
    {
        "title": "High-Risk Victim Age Groups",
        "insight": "Victims aged **18-30 years** account for the majority of reported cases across all years and states.",
        "plot": lambda ax: filtered_data[
            [
                "rape_cases_(total)_no._of_victims___upto_10_years",
                "rape_cases_(total)_no._of_victims___(10_14)_years",
                "rape_cases_(total)_no._of_victims___(14_18)_years",
                "rape_cases_(total)_no._of_victims___(18_30)years",
                "rape_cases_(total)_no._of_victims___(30_50)_years",
                "rape_cases_(total)_no._of_victims___above_50_years",
            ]
        ]
        .sum()
        .plot(kind="bar", color="coral", ax=ax),
    },
    {
        "title": "State-Level Severity",
        "insight": "States like Uttar Pradesh, Madhya Pradesh, and Maharashtra consistently report the highest number of cases.",
        "plot": lambda ax: filtered_data.groupby("state_ut")[
            "rape_cases_(total)___no._of_cases_reported"
        ].sum().plot(kind="bar", figsize=(8, 6), ax=ax),
    },
    {
        "title": "Temporal Trends",
        "insight": "The total number of cases shows an upward trend over the years, with spikes in certain periods.",
        "plot": lambda ax: filtered_data.groupby("year")[
            "rape_cases_(total)___no._of_cases_reported"
        ].sum().plot(kind="line", marker="o", ax=ax),
    },
    {
        "title": "Urban vs. Rural Insights",
        "insight": "Urbanized states like Delhi report higher cases involving neighbors and other known persons.",
        "plot": lambda ax: filtered_data.groupby("state_ut")[
            "no._of_cases_in_which_offenders_were_neighbours"
        ].sum().plot(kind="bar", color="skyblue", ax=ax),
    },
    {
        "title": "Victims Below 18 Years",
        "insight": "Approximately **35%** of the total victims belong to the under-18 category.",
        "plot": lambda ax: filtered_data[
            [
                "rape_cases_(total)_no._of_victims___upto_10_years",
                "rape_cases_(total)_no._of_victims___(10_14)_years",
                "rape_cases_(total)_no._of_victims___(14_18)_years",
            ]
        ]
        .sum()
        .plot(kind="bar", color="green", ax=ax),
    },
    {
        "title": "Repeat Offending States",
        "insight": "States like Madhya Pradesh and Uttar Pradesh frequently appear at the top for total cases and offenders known to the victim.",
        "plot": lambda ax: filtered_data.groupby("state_ut")[
            "no._of_cases_in_which_offenders_were_known_to_the_victims"
        ].sum().plot(kind="bar", color="orange", ax=ax),
    },
]

# Display insights and charts
for insight in insights:
    st.subheader(insight["title"])
    st.markdown(insight["insight"])
    fig, ax = plt.subplots(figsize=(10, 6))
    insight["plot"](ax)
    st.pyplot(fig)
