import os
import sqlite3
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# 1. Baca data mentah train.csv
df = pd.read_csv('../train.csv')

# 2. Inisialisasi DBMS 1: MongoDB Atlas (Data Transaksi)
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['superstore_db']
collection = db['sales_transactions']

collection.delete_many({}) # Bersihkan koleksi lama

trans_cols = ['Row ID', 'Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 'Sales']
trans_df = df[trans_cols].copy()
collection.insert_many(trans_df.to_dict('records'))
print(" Data Transaksi berhasil dipompa ke MongoDB Atlas!")

# 3. Inisialisasi DBMS 2: SQLite (Data Master Pelanggan & Produk)
db_path = os.path.join('..', os.getenv('SQLITE_DB_PATH', 'superstore_master.db'))
conn = sqlite3.connect(db_path)

master_cols = ['Row ID', 'Order ID', 'Customer ID', 'Customer Name', 'Segment', 
               'Country', 'City', 'State', 'Postal Code', 'Region', 
               'Product ID', 'Category', 'Sub-Category', 'Product Name']
master_df = df[master_cols].copy()
master_df.columns = [c.replace(' ', '_').replace('-', '_') for c in master_df.columns]
master_df.to_sql('customers_products', conn, if_exists='replace', index=False)
conn.close()
print(" Data Master Pelanggan & Produk berhasil dipompa ke SQLite!")