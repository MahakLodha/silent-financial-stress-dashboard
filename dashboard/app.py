from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"


# ================================
# PAGE CONFIG
# ================================
st.set_page_config(
    page_title="Silent Financial Stress Dashboard",
    layout="wide"
)

# ================================
# DATA LOADING WITH CACHING
# ================================
@st.cache_data
def load_data():
    monthly = pd.read_csv(DATA_DIR / "monthly_metrics_trimmed.csv")
    stress_dist = pd.read_csv(DATA_DIR / "stress_distribution.csv")
    stress_trend = pd.read_csv(DATA_DIR / "stress_trend.csv")
    stress_drivers = pd.read_csv(DATA_DIR / "stress_drivers.csv")
    top_customers = pd.read_csv(DATA_DIR / "top_risk_customers.csv")

    return monthly, stress_dist, stress_trend, stress_drivers, top_customers



monthly, stress_dist, stress_trend, stress_drivers, customer_summary = load_data()


# ================================
# SIDEBAR NAVIGATION
# ================================
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Customer Analysis", "Stress Drivers & Churn"]
)

# ================================
# HEADER
# ================================
st.title("Silent Financial Stress Detection Dashboard")
st.markdown("Analytics-driven monitoring of customer financial health")

# ================================
# PAGE 1: OVERVIEW
# ================================
if page == "Overview":

    st.subheader("Portfolio Overview")

    total_customers = customer_summary.shape[0]
    stressed_pct = (customer_summary['stressed_months'] > 0).mean() * 100
    severe_pct = (customer_summary['max_stress'] >= 6).mean() * 100
    avg_stress = customer_summary['avg_stress'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", total_customers)
    col2.metric("Stressed Customers (%)", f"{stressed_pct:.1f}%")
    col3.metric("Severe Stress (%)", f"{severe_pct:.1f}%")
    col4.metric("Avg Stress Score", f"{avg_stress:.2f}")
    st.subheader("Top High-Risk Customers")

    top_risk_customers = (
        customer_summary
        .sort_values(
            by=['max_stress', 'stressed_months', 'avg_stress'],
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_risk_customers.rename(columns={
            'nameOrig': 'Customer ID',
            'avg_stress': 'Avg Stress Score',
            'max_stress': 'Max Stress Score',
            'stressed_months': 'Stressed Months'
        })
    )
    top_n = st.slider(
        "Number of high-risk customers to display",
        min_value=5,
        max_value=50,
        value=10
    )

    top_risk_customers = (
        customer_summary
        .sort_values(
            by=['max_stress', 'stressed_months', 'avg_stress'],
            ascending=False
        )
        .head(top_n)
    )

    st.dataframe(top_risk_customers)

    # Stress Category Distribution
    st.subheader("Stress Category Distribution")
    fig, ax = plt.subplots()
    ax.bar(stress_dist['stress_category'], stress_dist['count'])
    ax.set_xlabel("Stress Category")
    ax.set_ylabel("Customer Count")
    st.pyplot(fig)

    # Stress Trend
    st.subheader("Stress Trend Over Time")
    fig, ax = plt.subplots()
    ax.plot(stress_trend['month'], stress_trend['stress_score'], marker='o')
    ax.set_xlabel("Month")
    ax.set_ylabel("Average Stress Score")
    st.pyplot(fig)

# ================================
# PAGE 2: CUSTOMER ANALYSIS
# ================================
elif page == "Customer Analysis":

  

    st.subheader("Customer-Level Stress Analysis")

    customer_id = st.text_input(
        "Enter Customer ID (e.g., C1000000639)"
    )
    if customer_id:
        if customer_id not in customer_summary['nameOrig'].values:
            st.error("Customer ID not found. Please enter a valid ID.")
            st.stop()

    cust_data = monthly[
        monthly['nameOrig'] == customer_id
    ].sort_values('month')

    # Stress Timeline
    st.subheader("Monthly Stress Timeline")
    fig, ax = plt.subplots()
    ax.plot(cust_data['month'], cust_data['stress_score'], marker='o')
    ax.set_xlabel("Month")
    ax.set_ylabel("Stress Score")
    st.pyplot(fig)

    # Financial Summary
    st.subheader("Monthly Financial Summary")
    st.dataframe(
        cust_data[
            ['month', 'monthly_income', 'monthly_expense',
             'savings', 'transfer_ratio', 'stress_category']
        ]
    )

    # Stress Indicators
    st.subheader("Stress Indicators")
    if cust_data.empty:
        st.warning("No recent monthly data available for this customer.")
        st.stop()

    latest = cust_data.iloc[-1]
    indicators = []
    if latest['monthly_income'] == 0:
        indicators.append("❌ No Income")
    if latest['expense_income_ratio'] > 1:
        indicators.append("⚠️ Overspending")
    if latest['savings_rate'] < 0.1:
        indicators.append("⚠️ Low Savings")
    if latest['transfer_ratio'] > 0.5:
        indicators.append("⚠️ High Fixed Obligations")

    st.write(", ".join(indicators) if indicators else "No major stress indicators")

# ================================
# PAGE 3: STRESS DRIVERS & CHURN
# ================================
else:

    st.subheader("Top Stress Drivers")

    fig, ax = plt.subplots()
    ax.bar(stress_drivers['driver'], stress_drivers['percentage'])
    ax.set_ylabel("Percentage of Customers")
    st.pyplot(fig)

    st.subheader("Business Insights (Churn Validation)")

    st.markdown("""
    • Customers with high credit utilization and long inactivity periods are more likely to churn  
    • Stress-like financial behavior often precedes disengagement  
    • Early stress detection enables proactive intervention and improves retention  
    """)

# ================================
# FOOTER
# ================================
st.markdown("---")
st.caption("Silent Financial Stress Detection | Data Analytics Project")
