import os
import sqlite3
import certifi
import pandas as pd
import streamlit as st
import plotly.express as px
from pymongo import MongoClient
from dotenv import load_dotenv

# Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="Superstore Multi-DBMS Dashboard", layout="wide")
load_dotenv()

@st.cache_data
def load_data():
    # 1. Fetch dari MongoDB Atlas (Cloud NoSQL)
    mongo_uri = os.getenv('MONGO_URI')
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

    # Data Pipeline Federation via Pandas
    df_master.rename(columns={'Row_ID': 'Row ID', 'Order_ID': 'Order ID'}, inplace=True)
    df_merged = pd.merge(df_trans, df_master, on=['Row ID', 'Order ID'], how='inner')
    df_merged['Order Date'] = pd.to_datetime(df_merged['Order Date'], format='mixed', dayfirst=True)
    return df_merged

# Judul Dashboard
st.title("📊 Superstore Multi-DBMS Analytics Dashboard")
st.markdown("Visualisasi data hasil integrasi **MongoDB Atlas** (Data Transaksi) & **SQLite** (Data Pelanggan & Produk).")

try:
    df = load_data()

    # Sidebar Filter Interaktif
    st.sidebar.header("Filter Data Interaktif")
    selected_region = st.sidebar.multiselect("Pilih Region", options=df['Region'].unique(), default=df['Region'].unique())
    selected_category = st.sidebar.multiselect("Pilih Kategori", options=df['Category'].unique(), default=df['Category'].unique())

    filtered_df = df[(df['Region'].isin(selected_region)) & (df['Category'].isin(selected_category))]

    # Metric Cards Utama (Format Angka Biasa Tanpa Simbol $)
    col1, col2, col3 = st.columns(3)
    total_sales = filtered_df['Sales'].sum()
    col1.metric("Total Sales", f"{total_sales:,.2f}")
    col2.metric("Total Orders", f"{filtered_df['Order ID'].nunique():,}")
    col3.metric("Total Customers", f"{filtered_df['Customer_Name'].nunique():,}")

    st.markdown("---")

    # BARIS GRAPH 1: Bar Chart Kategori & Line Chart Tren Bulanan
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Sales Berdasarkan Kategori")
        fig_cat = px.bar(
            filtered_df.groupby('Category')['Sales'].sum().reset_index(), 
            x='Category', y='Sales', color='Category', 
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="Total Penjualan per Kategori"
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with chart_col2:
        st.subheader("Tren Sales Bulanan")
        df_trend = filtered_df.set_index('Order Date').resample('ME')['Sales'].sum().reset_index()
        fig_line = px.line(
            df_trend, x='Order Date', y='Sales', 
            markers=True, title="Tren Penjualan Bulanan"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    # BARIS GRAPH 2: Diagram Lingkaran (Pie Chart & Donut Chart)
    pie_col1, pie_col2 = st.columns(2)

    with pie_col1:
        st.subheader("🍕 Proporsi Sales per Segment Pelanggan (Pie Chart)")
        df_segment = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
        fig_pie = px.pie(
            df_segment, values='Sales', names='Segment', 
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0, # Pie chart penuh / lingkaran sempurna
            title="Distribusi Segment Pelanggan"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with pie_col2:
        st.subheader("🍩 Distribusi Sales per Region (Donut Chart)")
        df_region = filtered_df.groupby('Region')['Sales'].sum().reset_index()
        fig_donut = px.pie(
            df_region, values='Sales', names='Region', 
            color_discrete_sequence=px.colors.qualitative.Bold,
            hole=0.4, # Donut chart (lingkaran berlubang di tengah)
            title="Persentase Penjualan per Region"
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # BARIS GRAPH 3: Top 10 Produk Terlaris
    st.subheader("🏆 Top 10 Produk Terlaris berdasarkan Sales")
    top_products = filtered_df.groupby('Product_Name')['Sales'].sum().nlargest(10).reset_index()
    fig_top = px.bar(
        top_products, x='Sales', y='Product_Name', orientation='h',
        color='Sales', color_continuous_scale='Viridis',
        title="10 Produk dengan Penjualan Tertinggi"
    )
    fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("---")

    # Preview Tabel Data Join Multi-DBMS
    st.subheader("Preview Data Hasil Join Multi-DBMS")
    st.dataframe(filtered_df.head(50))

except Exception as e:
    st.error(f"Gagal memuat data. Error: {e}")