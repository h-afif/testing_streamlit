import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# 1. إعدادات الصفحة
st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")

st.title("📊 Enterprise Sales Analytics Dashboard")
st.write(
    "Upload your sales dataset to explore dynamic KPIs, charts, and data"
    " tables."
)

# 2. رفع ملف البيانات (CSV Uploader)
uploaded_file = st.sidebar.file_uploader(
    "Upload Sales CSV File", type=["csv"]
)

if uploaded_file is not None:
  # قراءة الملف بـ Pandas
  df = pd.read_csv(uploaded_file)

  st.sidebar.success("File uploaded successfully!")

  # 3. فلاتر تفاعلية في الـ Sidebar (تصفية البيانات)
  st.sidebar.header("Filter Options")

  # التأكد من وجود الأعمدة المطلوبة
  if "Region" in df.columns and "Category" in df.columns:
    # فلتر المنطقة
    regions = df["Region"].unique()
    selected_region = st.sidebar.selectbox(
        "Select Region", ["All"] + list(regions)
    )

    # فلتر الفئة
    categories = df["Category"].unique()
    selected_category = st.sidebar.selectbox(
        "Select Category", ["All"] + list(categories)
    )

    # تطبيق الفلاتر على DataFrame
    filtered_df = df.copy()
    if selected_region != "All":
      filtered_df = filtered_df[filtered_df["Region"] == selected_region]

    if selected_category != "All":
      filtered_df = filtered_df[filtered_df["Category"] == selected_category]
  else:
    filtered_df = df
    st.warning("Columns 'Region' or 'Category' not found in CSV. Showing all data.")

  # 4. حساب وعرض مؤشرات الأداء KPIs
  st.subheader("Key Performance Indicators (KPIs)")

  # حساب القيم بناءً على البيانات المصفاة (نفترض وجود عمود 'Sales' و 'Profit')
  total_sales = (
      filtered_df["Sales"].sum() if "Sales" in filtered_df.columns else 0
  )
  total_orders = len(filtered_df)
  avg_sales = (
      filtered_df["Sales"].mean() if "Sales" in filtered_df.columns else 0
  )

  col1, col2, col3 = st.columns(3)
  col1.metric("Total Sales", f"${total_sales:,.2f}")
  col2.metric("Total Orders", f"{total_orders:,}")
  col3.metric("Average Sale", f"${avg_sales:,.2f}")

  st.markdown("---")

  # 5. عرض الرسوم البيانية في أعمدة وتبويبات
  tab1, tab2 = st.tabs(["Visual Charts", "Filtered Dataset"])

  with tab1:
    st.subheader("Sales Visualization")

    if (
        "Date" in filtered_df.columns
        and "Sales" in filtered_df.columns
        and not filtered_df.empty
    ):
      c1, c2 = st.columns(2)

      with c1:
        st.write("Sales Trend Over Time")
        # رسم خطي للمبيعات
        fig, ax = plt.subplots(figsize=(6, 4))
        sales_by_date = filtered_df.groupby("Date")["Sales"].sum()
        ax.plot(
            sales_by_date.index,
            sales_by_date.values,
            marker="o",
            color="dodgerblue",
        )
        ax.set_ylabel("Sales")
        plt.xticks(rotation=90)
        st.pyplot(fig)

      with c2:
        st.write("Sales by Category")
        # رسم أعمدة للفئات
        if "Category" in filtered_df.columns:
          fig2, ax2 = plt.subplots(figsize=(6, 4))
          sales_by_cat = filtered_df.groupby("Category")["Sales"].sum()
          ax2.bar(
              sales_by_cat.index, sales_by_cat.values, color=["teal", "coral"]
          )
          ax2.set_ylabel("Sales")
          st.pyplot(fig2)
    else:
      st.info(
          "Please ensure your CSV contains 'Date', 'Sales', and 'Category'"
          " columns to display charts."
      )

  with tab2:
    st.subheader("Dataset View")
    st.write(f"Showing {len(filtered_df)} rows after applying filters.")
    st.dataframe(filtered_df)

else:
  st.info("👈 Please upload a CSV file from the sidebar to start the analysis.")
