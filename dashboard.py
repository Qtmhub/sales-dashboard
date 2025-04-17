import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Sales Performance Dashboard", layout="wide")
sns.set_palette("Set2")

@st.cache_data
def load_data():
    sales = pd.read_csv("structured_sales_data.csv")
    summary = pd.read_csv("sku_summary_report.csv")
    revenue = pd.read_csv("sku_revenue_summary.csv")
    salesperson = pd.read_csv("salesperson_performance.csv").drop(columns=["Unnamed: 0"], errors="ignore")
    low_margin = pd.read_csv("low_margin_skus.csv")
    if "NormalizedSKU" not in low_margin.columns:
        low_margin.reset_index(inplace=True)
        low_margin.rename(columns={"index": "NormalizedSKU"}, inplace=True)
    low_margin["NormalizedSKU"] = low_margin["NormalizedSKU"].astype(str)
    return sales, summary, revenue, salesperson, low_margin

sales_df, sku_summary, sku_revenue, salesperson_perf, low_margin_df = load_data()

sku_summary = sku_summary.reset_index()
sku_summary["NormalizedSKU"] = sku_summary["NormalizedSKU"].astype(str)

st.title("📊 Sales Performance Dashboard")
st.markdown("Analyze top-performing SKUs, revenue distribution, and profitability insights")

# --- KPI Summary ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Sales (₦)", f"{sales_df['Amount'].sum():,.0f}")
kpi2.metric("Total Units Sold", f"{sales_df['Qty'].sum():,.0f}")
kpi3.metric("Avg. Cart Value", f"{sales_df.groupby('Receipt')['Amount'].sum().mean():,.0f}")
kpi4.metric("Best Seller", sku_summary.head(1)["NormalizedSKU"].values[0])

st.divider()

# --- Top-Selling SKUs ---
st.subheader("🛍️ Top 10 Best-Selling SKUs")
top_skus = sku_summary.head(10)
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(data=top_skus, y="NormalizedSKU", x="TotalUnitsSold", ax=ax1, palette=sns.color_palette("Set2", n_colors=10))
ax1.set_title("Top 10 by Volume")
st.pyplot(fig1)

# --- Revenue Pie ---
st.subheader("💰 Revenue Distribution")
rev = sku_revenue.head(10)
fig2, ax2 = plt.subplots()
ax2.pie(rev['Amount'], labels=rev['NormalizedSKU'], autopct='%1.1f%%', startangle=140)
ax2.axis("equal")
st.pyplot(fig2)

# --- Price Variability ---
st.subheader("🎯 Price Variability for Top 15 SKUs")
top_price_skus = sales_df["NormalizedSKU"].value_counts().head(15).index
filtered = sales_df[sales_df["NormalizedSKU"].isin(top_price_skus)]
fig3, ax3 = plt.subplots(figsize=(14, 6))
sns.boxplot(data=filtered, x="NormalizedSKU", y="UnitPrice", ax=ax3)
plt.xticks(rotation=45)
st.pyplot(fig3)

# --- High Profit SKUs ---
st.subheader("🧠 Most Profitable SKUs")
high_profit = sku_summary.sort_values(by="AvgProfitPerUnit", ascending=False).head(10)
fig4, ax4 = plt.subplots(figsize=(10, 5))
sns.barplot(data=high_profit, x="NormalizedSKU", y="AvgProfitPerUnit", ax=ax4, palette=sns.color_palette("Set2", n_colors=10))
ax4.set_title("Top 10 by Profit per Unit")
plt.xticks(rotation=45)
st.pyplot(fig4)

# --- Low Profit Top Sellers ---
st.subheader("⚠️ Top-Selling but Low-Margin SKUs (<₦250 Profit)")
top_sellers = sku_summary.head(10)[["NormalizedSKU"]].copy()
low_margin_df = low_margin_df[["NormalizedSKU", "AvgProfitPerUnit"]].copy()
low_overlap = pd.merge(low_margin_df, top_sellers, on="NormalizedSKU", how="inner")
fig5, ax5 = plt.subplots(figsize=(10, 5))
if not low_overlap.empty and "AvgProfitPerUnit" in low_overlap.columns:
    sns.barplot(data=low_overlap, x="NormalizedSKU", y="AvgProfitPerUnit", ax=ax5, palette=sns.color_palette("Set2", n_colors=len(low_overlap)))
    ax5.set_title("Top-Selling SKUs with Low Profit")
    plt.xticks(rotation=45)
    st.pyplot(fig5)
else:
    st.info("No overlap found or AvgProfitPerUnit missing from low-margin + top-selling SKUs.")

# --- Salesperson Performance ---
st.subheader("🙋 Salesperson Performance")
fig6, ax6 = plt.subplots(figsize=(10, 5))
sns.barplot(data=salesperson_perf, y="SalesPerson", x="TotalRevenue", ax=ax6, palette=sns.color_palette("Set2", n_colors=len(salesperson_perf)))
ax6.set_title("Revenue by Salesperson")
st.pyplot(fig6)

st.caption("Built with ❤️ using Streamlit | @DTechNurse")

