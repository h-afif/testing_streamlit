
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(
    page_title="Professional Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main {
    background-color: #f8f9fa;
}

div[data-testid="metric-container"] {
    background-color: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}

h1 {
    color: #1f77b4;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    return pd.read_csv("data/sales.csv")


st.title("📊 Professional Sales Dashboard")
st.write("Interactive Business Intelligence Dashboard")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

df = load_data(uploaded_file)

df["date"] = pd.to_datetime(df["date"])

st.sidebar.header("Filters")

products = sorted(df["product"].unique())

selected_products = st.sidebar.multiselect(
    "Select Products",
    products,
    default=products
)

start_date = st.sidebar.date_input(
    "Start Date",
    df["date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    df["date"].max()
)

filtered_df = df[
    (df["product"].isin(selected_products))
    &
    (df["date"] >= pd.to_datetime(start_date))
    &
    (df["date"] <= pd.to_datetime(end_date))
]

# ==========================
# KPIs
# ==========================

total_revenue = filtered_df["revenue"].sum()
total_sales = filtered_df["quantity"].sum()
total_orders = len(filtered_df)
average_revenue = filtered_df["revenue"].mean()

best_product = (
    filtered_df.groupby("product")["revenue"]
    .sum()
    .idxmax()
    if not filtered_df.empty else "N/A"
)

st.markdown("## 📌 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "💰 Revenue",
    f"${total_revenue:,.2f}"
)

col2.metric(
    "🛒 Sales",
    f"{total_sales:,}"
)

col3.metric(
    "📦 Orders",
    f"{total_orders:,}"
)

col4.metric(
    "📈 Avg Revenue",
    f"${average_revenue:,.2f}"
)

col5.metric(
    "🏆 Best Product",
    best_product
)

st.divider()

# ==========================
# Analytics
# ==========================

product_revenue = (
    filtered_df.groupby("product")["revenue"]
    .sum()
    .reset_index()
)

daily_revenue = (
    filtered_df.groupby("date")["revenue"]
    .sum()
    .reset_index()
)

left, right = st.columns(2)

with left:

    fig_bar = px.bar(
        product_revenue,
        x="product",
        y="revenue",
        color="revenue",
        text_auto=".2s",
        title="Revenue by Product"
    )

    fig_bar.update_layout(
        xaxis_title="Product",
        yaxis_title="Revenue",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

with right:

    fig_line = px.line(
        daily_revenue,
        x="date",
        y="revenue",
        markers=True,
        title="Daily Revenue Trend"
    )

    fig_line.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig_line,
        use_container_width=True
    )

st.divider()

# ==========================
# Pie Chart
# ==========================

pie = px.pie(
    product_revenue,
    names="product",
    values="revenue",
    hole=0.45,
    title="Revenue Distribution"
)

st.plotly_chart(
    pie,
    use_container_width=True
)

# ==========================
# Monthly Revenue Analysis
# ==========================

monthly_df = filtered_df.copy()

monthly_df["Month"] = monthly_df["date"].dt.strftime("%Y-%m")

monthly_revenue = (
    monthly_df
    .groupby("Month")["revenue"]
    .sum()
    .reset_index()
)

st.subheader("📅 Monthly Revenue")

fig_month = px.area(
    monthly_revenue,
    x="Month",
    y="revenue",
    color_discrete_sequence=["#1f77b4"]
)

fig_month.update_layout(
    template="plotly_white",
    xaxis_title="Month",
    yaxis_title="Revenue"
)

st.plotly_chart(
    fig_month,
    use_container_width=True
)

# ==========================
# Top Products
# ==========================

st.subheader("🏆 Top Products")

top_products = (
    filtered_df
    .groupby("product")["revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_top = px.bar(
    top_products,
    x="revenue",
    y="product",
    orientation="h",
    color="revenue",
    text_auto=".2s"
)

fig_top.update_layout(
    template="plotly_white",
    yaxis=dict(categoryorder="total ascending")
)

st.plotly_chart(
    fig_top,
    use_container_width=True
)

# ==========================
# Revenue by Quantity
# ==========================

st.subheader("📦 Quantity vs Revenue")

fig_scatter = px.scatter(
    filtered_df,
    x="quantity",
    y="revenue",
    color="product",
    size="revenue",
    hover_data=["date"]
)

fig_scatter.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)

# ==========================
# Data Preview
# ==========================

st.subheader("📄 Filtered Data")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# ==========================
# Statistics
# ==========================

st.subheader("📈 Summary Statistics")

col1, col2 = st.columns(2)

with col1:
    st.write(filtered_df.describe())

with col2:

    st.write("### Revenue Statistics")

    st.metric(
        "Maximum Revenue",
        f"${filtered_df['revenue'].max():,.2f}"
    )

    st.metric(
        "Minimum Revenue",
        f"${filtered_df['revenue'].min():,.2f}"
    )

    st.metric(
        "Average Revenue",
        f"${filtered_df['revenue'].mean():,.2f}"
    )

# ==========================
# Download CSV
# ==========================

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="filtered_sales.csv",
    mime="text/csv"
)

# ==========================
# Download Excel
# ==========================

output = BytesIO()

with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    filtered_df.to_excel(
        writer,
        index=False,
        sheet_name="Sales"
    )

excel_data = output.getvalue()

st.download_button(
    label="📥 Download Excel",
    data=excel_data,
    file_name="filtered_sales.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ==========================
# Footer
# ==========================

st.divider()

st.markdown(
    """
    <center>
        <h4>📊 Professional Sales Dashboard</h4>
        <p>Built with ❤️ using Streamlit, Pandas and Plotly</p>
    </center>
    """,
    unsafe_allow_html=True
)

st.sidebar.info("""
Professional Sales Dashboard

Version 1.0
Built with:
- Streamlit
- Pandas
- Plotly
""")
