import os
import sqlite3
import certifi
import pandas as pd
import streamlit as st
import plotly.express as px
from pymongo import MongoClient
from dotenv import load_dotenv

# Set Konfig Halaman
st.set_page_config(page_title="Superstore Multi-DBMS Dashboard", layout="wide")
load_dotenv()

@st.cache_data
def load_data():
    # 1. Fetch dari MongoDB Atlas (Cloud NoSQL)
    mongo_uri = os.getenv('MONGO_URI')
    # tlsCAFile=certifi.where() digunakan untuk mencegah error SSL Handshake di Streamlit Cloud
    client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
    db = client['superstore_db']
    collection = db['sales_transactions']
    
    mongo_data = list(collection.find({}, {'_id': 0}))
    df_trans = pd.DataFrame(mongo_data)

    # 2. Fetch dari SQLite (Local Relational)
    db_path = os.getenv('SQLITE_DB_PATH', 'superstore_master.db')
    conn = sqlite3.connect(db_path)
    df_master = pd.read_sql_query("SELECT * FROM customers_products", conn)
    conn.close()

    # Rename kolom SQLite agar pas saat di-merge
    df_master.rename(columns={'Row_ID': 'Row ID', 'Order_ID': 'Order ID'}, inplace=True)

    # 3. Join / Federation di tingkat aplikasi via Pandas
    df_merged = pd.merge(df_trans, df_master, on=['Row ID', 'Order ID'], how='inner')
    df_merged['Order Date'] = pd.to_datetime(df_merged['Order Date'], format='mixed', dayfirst=True)
    return df_merged

# UI Dashboard
st.title("📊 Superstore Multi-DBMS Analytics Dashboard")
st.markdown("Visualisasi data hasil integrasi **MongoDB Atlas** (Data Transaksi) & **SQLite** (Data Pelanggan & Produk).")

try:
    df = load_data()

    # Filter Sidebar
    st.sidebar.header("Filter Data")
    selected_region = st.sidebar.multiselect("Pilih Region", options=df['Region'].unique(), default=df['Region'].unique())
    selected_category = st.sidebar.multiselect("Pilih Kategori", options=df['Category'].unique(), default=df['Category'].unique())

    filtered_df = df[(df['Region'].isin(selected_region)) & (df['Category'].isin(selected_category))]

    # Metric Cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${filtered_df['Sales'].sum():,.2f}")
    col2.metric("Total Orders", f"{filtered_df['Order ID'].nunique():,}")
    col3.metric("Total Customers", f"{filtered_df['Customer_Name'].nunique():,}")

    st.markdown("---")

    # Visualisasi Charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Sales Berdasarkan Kategori")
        fig_cat = px.bar(filtered_df.groupby('Category')['Sales'].sum().reset_index(), 
                         x='Category', y='Sales', color='Category', title="Total Penjualan per Kategori")
        st.plotly_chart(fig_cat, use_container_width=True)

    with chart_col2:
        st.subheader("Tren Sales Bulanan")
        df_trend = filtered_df.set_index('Order Date').resample('ME')['Sales'].sum().reset_index()
        fig_line = px.line(df_trend, x='Order Date', y='Sales', title="Tren Penjualan Bulanan")
        st.plotly_chart(fig_line, use_container_width=True)

    # Data Table Preview
    st.subheader("Preview Data Hasil Join Multi-DBMS")
    st.dataframe(filtered_df.head(50))

except Exception as e:
    st.error(f"Gagal memuat data. Error: {e}")