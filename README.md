📊 Enterprise Data Insight

Enterprise Data Insight adalah aplikasi Streamlit interaktif yang dirancang untuk membantu perusahaan melakukan analisis data finansial secara cepat dan akurat.  
Aplikasi ini memungkinkan pengguna untuk mengunggah data perusahaan, membersihkan data, menilai kualitas, memvisualisasikan tren KPI, menilai kesehatan finansial, hingga memberikan rekomendasi eksekutif** secara otomatis.

Tujuan dari Enterprise Data Insight adalah membantu perusahaan untuk mengubah data mentah menjadi informasi yang siap digunakan dalam pengambilan keputusan manajerial. 
Aplikasi ini dibuat agar manajemen dapat dengan cepat memahami kondisi keuangan perusahaan, termasuk tren pendapatan, kesehatan finansial, dan potensi risiko, tanpa harus menganalisis data secara manual.
🔹 Fitur Utama

1. Upload File CSV/Excel
   - Pengguna dapat mengunggah file `.csv` atau `.xlsx` perusahaan.  
   - Aplikasi mendeteksi encoding secara otomatis dan memberikan preview data agar pengguna dapat memverifikasi data awal sebelum proses analisis.  

2. Data Cleaning & Normalization
   - Nama kolom dinormalisasi (diubah menjadi huruf kecil, simbol dihapus, spasi diganti underscore).  
   - Baris duplikat dihapus secara otomatis.  
   - Data dikonversi ke tipe yang sesuai: numerik, tanggal, atau kategori.  
   - Missing value diisi dengan strategi yang sesuai: median untuk numerik dan modus untuk kategori.  
   - Semua perubahan dicatat dalam log untuk transparansi.

3. Data Readiness & Quality Gate
   - Aplikasi mendeteksi peran tiap kolom: tanggal, numerik, atau kategori.  
   - Menghitung tingkat missing value dan variasi data kategori.  
   - Menyusun Business Readiness Score untuk menilai apakah data siap digunakan untuk analisis dan pengambilan keputusan.  
   - Memberikan ringkasan eksekutif jika ada kolom dengan missing tinggi atau variasi rendah.

4. Financial Performance Overview
   - Pengguna dapat memilih kolom tanggal dan KPI finansial untuk dianalisis.  
   - Data diaggregasi per periode (misalnya bulanan) untuk memudahkan pemahaman tren.  
   - Menampilkan total, rata-rata, dan perubahan terakhir KPI.  
   - Visualisasi KPI menggunakan line chart untuk memudahkan interpretasi.

5. Executive Financial Insight
   - Sistem menafsirkan tren KPI dalam bahasa bisnis yang mudah dipahami.  
   - Memberikan insight apakah performa meningkat, menurun, atau stabil.  
   - Menyediakan rekomendasi strategi yang relevan berdasarkan data historis.

6. Financial Health Snapshot
   - Menilai kesehatan finansial perusahaan menggunakan dua indikator utama: pertumbuhan KPI dan volatilitas 
   - Memberikan skor kesehatan finansial dan status eksekutif:  
     - 🟢 Sehat  
     - 🟡 Perlu Perhatian  
     - 🔴 Berisiko  
   - Menyampaikan interpretasi naratif mengenai stabilitas pendapatan.
7. Financial Risk Early Warning
   - Mendeteksi risiko keuangan jangka pendek seperti:  
     - Penurunan pendapatan berturut-turut  
     - Fluktuasi pendapatan tinggi  
     - Pertumbuhan negatif KPI  
   - Memberikan peringatan dini agar manajemen dapat mengambil tindakan preventif.
8. Executive Action Recommendation
   - Memberikan rekomendasi strategi yang spesifik berdasarkan kondisi keuangan saat ini.  
   - Contoh rekomendasi: evaluasi struktur biaya, diversifikasi sumber pendapatan, fokus pada efisiensi operasional, atau mendorong ekspansi bisnis.
