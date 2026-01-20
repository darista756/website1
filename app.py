import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Enterprise Data Insight",
    layout="wide"
)

st.title("📊 Enterprise Data Insight")
st.subheader("Step 1 — Upload Data Perusahaan")

uploaded_file = st.file_uploader(
    "Upload file CSV atau Excel",
    type=["csv", "xlsx"]
)

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")


    st.success("✅ Data berhasil diupload")

    st.markdown("### 🔍 Preview Data")
    st.dataframe(df.head())

    st.markdown("### 📌 Informasi Data")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Jumlah Baris", df.shape[0])
    with col2:
        st.metric("Jumlah Kolom", df.shape[1])
    with col3:
        st.metric("Missing Values", df.isnull().sum().sum())

    st.markdown("### 🧠 Struktur Kolom")
    info_df = pd.DataFrame({
        "Kolom": df.columns,
        "Tipe Data": df.dtypes.astype(str),
        "Missing": df.isnull().sum().values
    })
    st.dataframe(info_df)

    st.markdown("### 🚦 Status Data")
    if info_df["Missing"].sum() > 0:
        st.warning("⚠️ Data memiliki missing value — perlu cleaning")
    else:
        st.success("✅ Data bersih dan siap dianalisis")
        st.divider()
        st.divider()
    st.subheader("Step 2 — Data Cleaning Otomatis (Aman untuk Perusahaan)")

    df_clean = df.copy()
    cleaning_log = []

    # 1️⃣ Normalisasi nama kolom
    df_clean.columns = (
        df_clean.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    cleaning_log.append("Nama kolom dinormalisasi")

    # 2️⃣ Hapus duplikasi (wajar)
    before_rows = df_clean.shape[0]
    df_clean = df_clean.drop_duplicates()
    after_rows = df_clean.shape[0]
    if before_rows != after_rows:
        cleaning_log.append(f"{before_rows - after_rows} data duplikat dihapus")

    # 3️⃣ Imputasi missing value (AMAN)
    for col in df_clean.columns:
        missing = df_clean[col].isnull().sum()
        if missing > 0:
            if df_clean[col].dtype in ["int64", "float64"]:
                df_clean[col].fillna(df_clean[col].median(), inplace=True)
                cleaning_log.append(
                    f"Kolom '{col}' (numerik): {missing} missing → median"
                )
            else:
                mode = df_clean[col].mode()
                fill_value = mode[0] if not mode.empty else "Tidak diketahui"
                df_clean[col].fillna(fill_value, inplace=True)
                cleaning_log.append(
                    f"Kolom '{col}' (kategori): {missing} missing → modus"
                )

    # 📊 Ringkasan hasil
    st.success("✅ Data dibersihkan tanpa mengurangi struktur utama")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Baris Awal", df.shape[0])
    with col2:
        st.metric("Baris Setelah Cleaning", df_clean.shape[0])
    
    # =========================
    # LOG CLEANING (TETAP ADA)
    # =========================
    st.markdown("### 🧾 Log Cleaning")
    for log in cleaning_log:
        st.write("•", log)
    
    # =========================
    # HEADER PREVIEW + DOWNLOAD
    # =========================
    header_left, header_right = st.columns([4, 1])
    
    with header_left:
        st.markdown("### 🔍 Preview Data Setelah Cleaning")
    
    with header_right:
        csv = df_clean.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Clean Data",
            data=csv,
            file_name="clean_data_full.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # =========================
    # DATAFRAME (FULL DATA)
    # =========================
    st.dataframe(
        df_clean,
        use_container_width=True,
        height=450
    )
    
    # =========================
    # SIMPAN KE SESSION
    # =========================
    st.session_state["clean_data"] = df_clean
    
    st.subheader("Step 3 — “Data Readiness & Quality Analysis” (Enterprise Ready)")

    df_analysis = df_clean.copy()
    
    # ======================================================
    # 1️⃣ DETEKSI PERAN KOLOM
    # ======================================================
    date_cols, numeric_cols, categorical_cols = [], [], []
    
    for col in df_analysis.columns:
        if pd.api.types.is_datetime64_any_dtype(df_analysis[col]):
            date_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df_analysis[col]) and not pd.api.types.is_bool_dtype(df_analysis[col]):
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)
    
    st.markdown("### 🧠 Deteksi Peran Kolom")
    st.write("📅 Kolom Tanggal:", date_cols if date_cols else "-")
    st.write("🔢 Kolom Numerik (KPI):", numeric_cols)
    st.write("🏷 Kolom Kategori:", categorical_cols)
    
    # ======================================================
    # 2️⃣ DATA QUALITY ANALYSIS + GRAFIK
    # ======================================================
    st.markdown("### ⚠️ Analisis Kualitas Data")
    
    quality_report = []
    total_rows = len(df_analysis)
    
    for col in df_analysis.columns:
        missing_rate = df_analysis[col].isnull().mean()
        unique_ratio = df_analysis[col].nunique(dropna=True) / total_rows
    
        status = "Aman"
        if missing_rate > 0.30:
            status = "Missing Tinggi"
        elif unique_ratio < 0.05:
            status = "Variasi Rendah"
    
        quality_report.append({
            "Kolom": col,
            "Missing (%)": round(missing_rate * 100, 2),
            "Unique Ratio": round(unique_ratio, 3),
            "Status": status
        })
    
    quality_df = pd.DataFrame(quality_report)
    st.dataframe(quality_df, use_container_width=True)
    
    st.markdown("#### 📊 Visual Missing Value")
    st.bar_chart(
        quality_df.set_index("Kolom")[["Missing (%)"]],
        use_container_width=True
    )
    
    # ======================================================
    # 3️⃣ OUTLIER DETECTION + DISTRIBUSI
    # ======================================================
    st.markdown("### 🚨 Deteksi Outlier & Distribusi KPI")
    
    outlier_summary = []
    
    for col in numeric_cols:
        series = pd.to_numeric(df_analysis[col], errors="coerce").dropna()
        if len(series) < 10:
            continue
    
        Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            continue
    
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        outliers = series[(series < lower) | (series > upper)]
    
        outlier_summary.append({
            "Kolom": col,
            "Jumlah Outlier": len(outliers),
            "Persentase (%)": round(len(outliers) / len(series) * 100, 2)
        })
    
    if outlier_summary:
        outlier_df = pd.DataFrame(outlier_summary)
        st.dataframe(outlier_df, use_container_width=True)
    else:
        st.info("Tidak ditemukan outlier signifikan.")
    
    if numeric_cols:
        selected_num = st.selectbox("📈 Lihat distribusi KPI", numeric_cols)
        st.bar_chart(
            df_analysis[selected_num].value_counts().sort_index(),
            use_container_width=True
        )
    
    # ======================================================
    # 4️⃣ KONSENTRASI KATEGORI + GRAFIK
    # ======================================================
    st.markdown("### 📊 Analisis Konsentrasi Kategori")
    
    concentration_flag = False
    
    if categorical_cols:
        selected_cat = st.selectbox("Pilih kolom kategori", categorical_cols)
    
        top_values = (
            df_analysis[selected_cat]
            .value_counts(normalize=True)
            .head(5)
        )
    
        st.bar_chart(top_values, use_container_width=True)
    
        if top_values.iloc[0] > 0.5:
            concentration_flag = True
            st.warning(
                f"⚠️ {round(top_values.iloc[0]*100,1)}% data terkonsentrasi pada satu kategori"
            )
    
    # ======================================================
    # 5️⃣ ANALISIS TREN WAKTU (OPSIONAL)
    # ======================================================
    if date_cols and numeric_cols:
        st.markdown("### ⏳ Analisis Tren Waktu")
    
        date_col = st.selectbox("Kolom tanggal", date_cols)
        value_col = st.selectbox("KPI", numeric_cols)
    
        df_trend = (
            df_analysis[[date_col, value_col]]
            .dropna()
            .sort_values(date_col)
        )
    
        st.line_chart(
            df_trend.set_index(date_col)[value_col],
            use_container_width=True
        )
    
    # ======================================================
    # 6️⃣ BUSINESS READINESS SCORE
    # ======================================================
    st.markdown("### ⭐ Business Readiness Score")
    
    score = 100
    score -= (quality_df["Missing (%)"] > 30).sum() * 5
    score -= (quality_df["Status"] == "Variasi Rendah").sum() * 3
    score -= sum(1 for o in outlier_summary if o["Persentase (%)"] > 10) * 4
    
    score = max(score, 55)
    
    st.metric(
        "Kesiapan Data untuk Keputusan Bisnis",
        f"{score} / 100"
    )
    
    # ======================================================
    # 7️⃣ RINGKASAN EKSEKUTIF (AUTO)
    # ======================================================
    st.markdown("### 🧾 Ringkasan Eksekutif")
    
    summary = []
    
    if (quality_df["Missing (%)"] > 30).any():
        summary.append("Terdapat kolom dengan missing value tinggi yang perlu perhatian.")
    if (quality_df["Status"] == "Variasi Rendah").any():
        summary.append("Beberapa kolom memiliki variasi rendah dan mungkin kurang relevan.")
    if concentration_flag:
        summary.append("Data menunjukkan ketergantungan tinggi pada satu kategori utama.")
    if not summary:
        summary.append("Struktur dan kualitas data cukup baik untuk analisis lanjutan.")
    
    for s in summary:
        st.write("•", s)
    
    

    st.subheader("Step 4 — Analisis Performa & Tren KPI")

    df_analysis = df_clean.copy()
    
    # =========================
    # 1️⃣ DETEKSI PERAN KOLOM
    # =========================
    date_cols, numeric_cols, categorical_cols = [], [], []
    
    for col in df_analysis.columns:
        # coba convert ke datetime jika object
        if pd.api.types.is_datetime64_any_dtype(df_analysis[col]):
            date_cols.append(col)
        elif pd.api.types.is_object_dtype(df_analysis[col]):
            try:
                df_analysis[col] = pd.to_datetime(df_analysis[col])
                date_cols.append(col)
            except:
                categorical_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df_analysis[col]) and not pd.api.types.is_bool_dtype(df_analysis[col]):
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)
    
    st.markdown("### 🧠 Deteksi Peran Kolom")
    st.write("📅 Kolom Tanggal:", date_cols if date_cols else "-")
    st.write("🔢 Kolom Numerik (KPI):", numeric_cols)
    st.write("🏷 Kolom Kategori:", categorical_cols)
    
    # =========================
    # 2️⃣ DATA QUALITY + TREND
    # =========================
    st.markdown("### 📊 Analisis Performa KPI Otomatis")
    
    insights = []
    recommendations = []
    
    if date_cols and numeric_cols:
        for date_col in date_cols:
            for kpi_col in numeric_cols:
                df_trend = df_analysis[[date_col, kpi_col]].dropna().sort_values(date_col)
                if len(df_trend) < 2:
                    continue
    
                # Hitung persentase perubahan
                df_trend['pct_change'] = df_trend[kpi_col].pct_change() * 100
    
                # Penurunan signifikan
                drop_threshold = -10  # bisa disesuaikan
                drops = df_trend[df_trend['pct_change'] <= drop_threshold]
                if not drops.empty:
                    insights.append(
                        f"📉 KPI '{kpi_col}' mengalami penurunan signifikan "
                        f"pada tanggal: {drops[date_col].dt.date.tolist()}."
                    )
                    recommendations.append(
                        f"Tinjau faktor yang menyebabkan penurunan '{kpi_col}' "
                        "dan ambil tindakan mitigasi."
                    )
    
                # Kenaikan signifikan
                rise_threshold = 10
                rises = df_trend[df_trend['pct_change'] >= rise_threshold]
                if not rises.empty:
                    insights.append(
                        f"📈 KPI '{kpi_col}' menunjukkan kenaikan signifikan "
                        f"pada tanggal: {rises[date_col].dt.date.tolist()}."
                    )
                    recommendations.append(
                        f"Pertimbangkan strategi untuk memanfaatkan peningkatan '{kpi_col}'."
                    )
    
                # Tampilkan chart tren KPI
                st.markdown(f"#### KPI: {kpi_col} vs Waktu ({date_col})")
                st.line_chart(df_trend.set_index(date_col)[kpi_col], use_container_width=True)
    
    # =========================
    # 3️⃣ Analisis KPI per Kategori
    # =========================
    st.markdown("### 📊 Analisis KPI Berdasarkan Kategori")
    
    if categorical_cols and numeric_cols and date_cols:
        cat_col = st.selectbox("Pilih kolom kategori untuk analisis tren", categorical_cols)
        kpi_col = st.selectbox("Pilih KPI numerik", numeric_cols)
        date_col = date_cols[0]
    
        pivot = df_analysis.pivot_table(
            index=date_col,
            columns=cat_col,
            values=kpi_col,
            aggfunc='sum'
        ).sort_index()
    
        st.line_chart(pivot, use_container_width=True)
    
        # Cek penurunan >10% per kategori
        pct_change_cat = pivot.pct_change() * 100
        drops_cat = pct_change_cat[pct_change_cat < -10].stack()
        if not drops_cat.empty:
            for (d, c), v in drops_cat.items():
                insights.append(
                    f"📉 KPI '{kpi_col}' untuk kategori '{c}' turun {round(abs(v),2)}% pada {d.date()}."
                )
            recommendations.append(
                f"Periksa faktor yang mempengaruhi penurunan KPI per kategori di kolom '{cat_col}'."
            )
    
    # =========================
    # 4️⃣ Ringkasan Insight & Rekomendasi Bisnis
    # =========================
    st.subheader("Step 5 — Insight & Rekomendasi Bisnis Otomatis")
    
    if not insights:
        insights.append("📌 Tidak ditemukan penurunan/kenaikan signifikan KPI. Performa stabil.")
    
    st.markdown("### 🧠 Insight Utama")
    for i, text in enumerate(insights, 1):
        st.write(f"{i}. {text}")
    
    st.markdown("### 🎯 Rekomendasi Bisnis")
    for i, text in enumerate(recommendations, 1):
        st.write(f"{i}. {text}")
    