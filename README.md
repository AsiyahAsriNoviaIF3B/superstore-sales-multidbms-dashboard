# 📊 Sales Dashboard Analytics (Multi-DBMS Architecture)

Aplikasi web interaktif ini mencontohkan konsep *Data Federation* dengan mengintegrasikan dua *engine* basis data yang berbeda secara terpusat untuk kebutuhan analitik bisnis.

## 🏗 Arsitektur Sistem
Sistem ini menggunakan arsitektur **Polyglot Persistence**:
- **MongoDB Atlas (Document/NoSQL):** Menyimpan data transaksi operasional (`sales_transactions`) yang bersifat dinamis dan memiliki volume tinggi.
- **SQLite (Relational/Local Embedded):** Menyimpan data master referensi (`customers_products`) yang terstruktur dan jarang berubah secara ekstrem.
- **Pandas:** Bertindak sebagai *federation layer* yang melakukan operasi JOIN/Merge dari kedua sumber data berbeda di level aplikasi.

## 🚀 Cara Menjalankan Aplikasi di Lokal
1. *Clone* repositori ini: `git clone [URL_REPO_ANDA]`
2. Instal dependensi: `pip install -r requirements.txt`
3. Buat file `.env` dan masukkan kredensial MongoDB Anda:
   MONGO_URI=mongodb+srv://:@cluster.mongodb.net/
4. Jalankan skrip *seeding* untuk inisialisasi database: `python seed_data.py`
5. Jalankan aplikasi Streamlit: `streamlit run app.py`

## 🔗 Live Deployment
Aplikasi ini dapat diakses secara langsung melalui: [Masukkan Tautan Streamlit Community Cloud Anda]

## 📚 Sitasi & Referensi Dataset
- Dataset transaksi bersumber dari: [Tautkan sumber/Kaggle]
- Referensi arsitektur Streamlit-MongoDB: [Tautkan dokumentasi]
