import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Enterprise Data Insight",
    layout="wide"
)

st.title("📊 Enterprise Data Insight")
st.subheader("Step 1 — Upload & Data Ingestion (Enterprise-Grade)")

uploaded_file = st.file_uploader(
    "Upload file CSV atau Excel perusahaan",
    type=["csv", "xlsx"]
)

df = None
read_error = None

if uploaded_file:
    try:
        # ===============================
        # CSV HANDLING (ROBUST)
        # ===============================
        if uploaded_file.name.lower().endswith(".csv"):
            try:
                df = pd.read_csv(
                    uploaded_file,
                    encoding="utf-8",
                    sep=",",
                    quotechar='"',
                    skipinitialspace=True
                )
            except UnicodeDecodeError:
                df = pd.read_csv(
                    uploaded_file,
                    encoding="latin1",
                    sep=",",
                    quotechar='"',
                    skipinitialspace=True,
                    engine="python"
                )

        # ===============================
        # EXCEL HANDLING (SAFE)
        # ===============================
        else:
            df = pd.read_excel(
                uploaded_file,
                engine="openpyxl"
            )

    except Exception as e:
        read_error = str(e)

# ===============================
# FEEDBACK KE USER
# ===============================
if read_error:
    st.error("❌ File gagal dibaca")
    st.code(read_error)

elif df is not None:
    st.success("✅ Data berhasil diupload & dibaca dengan aman")

    # ===============================
    # PREVIEW DATA (EXCEL-LIKE)
    # ===============================
    st.markdown("### Preview Data")
    st.dataframe(df.head(20), use_container_width=True)

    # ===============================
    # INFORMASI DATA
    # ===============================
    st.markdown("### Ringkasan Data")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Jumlah Baris", df.shape[0])
    with c2:
        st.metric("Jumlah Kolom", df.shape[1])
    with c3:
        st.metric("Total Missing", df.isnull().sum().sum())
    with c4:
        st.metric("Ukuran File (KB)", round(uploaded_file.size / 1024, 2))

    # ===============================
    # STRUKTUR KOLOM
    # ===============================
    st.markdown("### Struktur Kolom")

    info_df = pd.DataFrame({
        "Kolom": df.columns,
        "Tipe Data": df.dtypes.astype(str),
        "Missing": df.isnull().sum().values,
        "Unique": df.nunique().values
    })

    st.dataframe(info_df, use_container_width=True)

    # ===============================
    # STATUS DATA (GATE)
    # ===============================
    st.markdown("### Status Awal Data")

    if info_df["Missing"].sum() > 0:
        st.warning("⚠️ Data memiliki missing value — akan diproses di Step 2")
    else:
        st.success("✅ Data tidak memiliki missing value besar")

    # ===============================
    # SIMPAN KE SESSION
    # ===============================
    st.session_state["raw_data"] = df



    st.subheader("Step 2 — Financial-Grade Data Cleaning & Normalization")

    df_clean = df.copy()
    cleaning_log = []
    
    # ======================================================
    # 1️⃣ NORMALISASI NAMA KOLOM
    # ======================================================
    original_columns = df_clean.columns.tolist()
    
    df_clean.columns = (
        df_clean.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w\s]", "", regex=True)
        .str.replace(r"\s+", "_", regex=True)
    )
    
    if original_columns != df_clean.columns.tolist():
        cleaning_log.append(
            "Nama kolom dinormalisasi (lowercase, underscore, tanpa simbol)"
        )
    
    # ======================================================
    # 2️⃣ HAPUS DUPLIKASI BARIS (AMAN)
    # ======================================================
    before_rows = df_clean.shape[0]
    df_clean = df_clean.drop_duplicates()
    after_rows = df_clean.shape[0]
    
    if before_rows != after_rows:
        cleaning_log.append(
            f"{before_rows - after_rows} baris duplikat dihapus"
        )
    
    # ======================================================
    # 3️⃣ NORMALISASI ISI DATA (FINANCE-AWARE)
    # ======================================================
    for col in df_clean.columns:
    
        # =========================
        # A. OBJECT / STRING
        # =========================
        if df_clean[col].dtype == "object":
    
            original_non_null = df_clean[col].notna().sum()
    
            # string dasar (AMAN)
            series = (
                df_clean[col]
                .astype(str)
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
            )
    
            # -------------------------
            # Coba konversi DATETIME
            # -------------------------
            converted_date = pd.to_datetime(series, errors="coerce")
            if converted_date.notna().mean() > 0.8:
                df_clean[col] = converted_date
                cleaning_log.append(
                    f"Kolom '{col}' dikonversi ke datetime"
                )
                continue
    
            # -------------------------
            # Normalisasi ANGKA KEUANGAN
            # -------------------------
            numeric_candidate = (
                series
                .str.replace(r"[^\d\-,.]", "", regex=True)  # hapus currency symbol
                .str.replace(",", "", regex=False)          # hapus ribuan
                .replace({"": None, "-": None})
            )
    
            numeric_converted = pd.to_numeric(
                numeric_candidate, errors="coerce"
            )
    
            # konversi hanya jika mayoritas valid
            if numeric_converted.notna().mean() > 0.6:
                df_clean[col] = numeric_converted
                cleaning_log.append(
                    f"Kolom '{col}' dinormalisasi sebagai numerik (financial)"
                )
                continue
    
            # fallback → tetap string
            df_clean[col] = series
    
        # =========================
        # B. IMPUTASI MISSING VALUE
        # =========================
        missing = df_clean[col].isnull().sum()
    
        if missing > 0:
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                median = df_clean[col].median()
                df_clean[col] = df_clean[col].fillna(median)
                cleaning_log.append(
                    f"Kolom '{col}' (numerik): {missing} missing → median"
                )
            else:
                mode = df_clean[col].mode()
                fill_value = mode[0] if not mode.empty else "Unknown"
                df_clean[col] = df_clean[col].fillna(fill_value)
                cleaning_log.append(
                    f"Kolom '{col}' (kategori): {missing} missing → '{fill_value}'"
                )
    
    # ======================================================
    # 4️⃣ RINGKASAN HASIL
    # ======================================================
    st.success(
        "✅ Data keuangan dibersihkan & dinormalisasi tanpa merusak struktur bisnis"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Baris Awal", df.shape[0])
    with col2:
        st.metric("Baris Setelah Cleaning", df_clean.shape[0])
    
    # ======================================================
    # LOG CLEANING
    # ======================================================
    st.markdown("### Data Cleaning Log")
    for log in cleaning_log:
        st.write("•", log)
    
    # ======================================================
    # PREVIEW + DOWNLOAD
    # ======================================================
    header_left, header_right = st.columns([4, 1])
    
    with header_left:
        st.markdown("### Preview Data Setelah Cleaning")
    
    with header_right:
        csv = df_clean.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Clean Financial Data",
            data=csv,
            file_name="clean_financial_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.dataframe(
        df_clean,
        use_container_width=True,
        height=450
    )
    
    # ======================================================
    # SIMPAN KE SESSION
    # ======================================================
    st.session_state["clean_data"] = df_clean
    
        
            
    st.subheader("Step 3 — Data Readiness & Quality Gate (Enterprise Standard)")
    
    df_analysis = st.session_state.get("clean_data", df_clean).copy()
    total_rows = len(df_analysis)
    
    # ======================================================
    # 1️⃣ DETEKSI PERAN KOLOM (POST-CLEAN)
    # ======================================================
    date_cols, numeric_cols, categorical_cols = [], [], []
    
    for col in df_analysis.columns:
        if pd.api.types.is_datetime64_any_dtype(df_analysis[col]):
            date_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df_analysis[col]) and not pd.api.types.is_bool_dtype(df_analysis[col]):
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)
    
    st.markdown("### Struktur Data Setelah Cleaning")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("📅 Kolom Tanggal", len(date_cols))
    with c2:
        st.metric("🔢 Kolom Numerik", len(numeric_cols))
    with c3:
        st.metric("🏷 Kolom Kategori", len(categorical_cols))
    
    with st.expander("Detail kolom terdeteksi"):
        st.write("📅 Tanggal:", date_cols or "-")
        st.write("🔢 Numerik:", numeric_cols)
        st.write("🏷 Kategori:", categorical_cols)
    
    # ======================================================
    # 2️⃣ DATA QUALITY ASSESSMENT (BUSINESS-ORIENTED)
    # ======================================================
    quality_table = []
    
    for col in df_analysis.columns:
        missing_rate = df_analysis[col].isnull().mean()
        unique_ratio = df_analysis[col].nunique(dropna=True) / total_rows
    
        status = "Aman"
    
        if missing_rate > 0.30:
            status = "Missing Tinggi"
        elif unique_ratio < 0.05 and col in categorical_cols:
            status = "Variasi Rendah"
    
        quality_table.append({
            "Kolom": col,
            "Missing (%)": round(missing_rate * 100, 2),
            "Unique Ratio": round(unique_ratio, 3),
            "Status": status
        })
    
    quality_df = pd.DataFrame(quality_table)
    
    st.markdown("### Indikator Kualitas Data")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric(
            "Kolom Missing Tinggi",
            (quality_df["Status"] == "Missing Tinggi").sum()
        )
    with c2:
        st.metric(
            "Kolom Variasi Rendah (Kategori)",
            (quality_df["Status"] == "Variasi Rendah").sum()
        )
    
    with st.expander("Detail kualitas per kolom"):
        st.dataframe(quality_df, use_container_width=True)
    
    # ======================================================
    # 3️⃣ BUSINESS READINESS SCORE (TRANSPARAN)
    # ======================================================
    score = 100
    
    missing_penalty = (quality_df["Status"] == "Missing Tinggi").sum() * 5
    low_variance_penalty = (quality_df["Status"] == "Variasi Rendah").sum() * 3
    
    score -= missing_penalty
    score -= low_variance_penalty
    score = max(score, 60)
    
    st.markdown("### ⭐ Business Readiness Score")
    
    st.metric("Skor Kesiapan Data", f"{score} / 100")
    
    if score >= 85:
        st.success("Data sangat siap untuk analisis performa keuangan dan keputusan bisnis.")
    elif score >= 70:
        st.warning("Data cukup siap, namun perlu perhatian pada beberapa kolom.")
    else:
        st.error("Data belum layak untuk analisis bisnis kritikal.")
    
    # ======================================================
    # 4️⃣ RINGKASAN EKSEKUTIF (DECISION-READY)
    # ======================================================
    st.markdown("### 🧾 Ringkasan Kesiapan Data")
    
    summary = []
    
    if (quality_df["Status"] == "Missing Tinggi").any():
        summary.append(
            "Terdapat kolom dengan tingkat missing value tinggi yang dapat mempengaruhi akurasi analisis."
        )
    
    if (quality_df["Status"] == "Variasi Rendah").any():
        summary.append(
            "Beberapa kolom kategori memiliki variasi rendah dan mungkin kurang informatif."
        )
    
    if not summary:
        summary.append(
            "Struktur, konsistensi, dan kualitas data secara umum sudah memadai untuk analisis bisnis."
        )
    
    for s in summary[:3]:
        st.write("•", s)
        
    
    st.subheader("Step 4 — Financial Performance Overview")

    df_analysis = st.session_state.get("clean_data", df_clean).copy()
    
    # ===============================
    # 1️⃣ DETEKSI STRUKTUR DATA
    # ===============================
    date_cols = [c for c in df_analysis.columns if pd.api.types.is_datetime64_any_dtype(df_analysis[c])]
    numeric_cols = [c for c in df_analysis.columns if pd.api.types.is_numeric_dtype(df_analysis[c])]
    
    if not date_cols or not numeric_cols:
        st.warning("Data belum memiliki kolom waktu dan numerik yang cukup.")
        st.stop()
    
    # ===============================
    # 2️⃣ PILIH KPI UTAMA
    # ===============================
    c1, c2 = st.columns(2)
    
    with c1:
        date_col = st.selectbox("📅 Periode Waktu", date_cols)
    
    with c2:
        kpi_col = st.selectbox("💰 KPI Finansial", numeric_cols)
    
    # ===============================
    # 3️⃣ AGREGASI DATA (RAMAH AWAM)
    # ===============================
    df_trend = (
        df_analysis[[date_col, kpi_col]]
        .dropna()
        .assign(period=lambda x: x[date_col].dt.to_period("M").dt.to_timestamp())
        .groupby("period")[kpi_col]
        .sum()
        .reset_index()
    )
    
    if len(df_trend) < 2:
        st.warning("Data belum cukup untuk analisis tren.")
        st.stop()
    
    # ===============================
    # 4️⃣ KPI RINGKAS (EXECUTIVE METRIC)
    # ===============================
    total_value = df_trend[kpi_col].sum()
    avg_value = df_trend[kpi_col].mean()
    last_value = df_trend[kpi_col].iloc[-1]
    prev_value = df_trend[kpi_col].iloc[-2]
    
    change_pct = ((last_value - prev_value) / abs(prev_value)) * 100 if prev_value != 0 else 0
    
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Total", f"{total_value:,.0f}")
    c2.metric("Rata-rata / Bulan", f"{avg_value:,.0f}")
    c3.metric("Perubahan Terakhir", f"{change_pct:.1f}%")
    
    # ===============================
    # 5️⃣ VISUALISASI SEDERHANA
    # ===============================
    st.markdown("### 📈 Pergerakan KPI dari Waktu ke Waktu")
    
    st.line_chart(
        df_trend.set_index("period")[kpi_col],
        use_container_width=True
    )
    
    st.subheader("Step 5 — Executive Financial Insight")
    
    insights = []
    recommendations = []
    
    # ===============================
    # INTERPRETASI SEDERHANA
    # ===============================
    first_val = df_trend[kpi_col].iloc[0]
    last_val = df_trend[kpi_col].iloc[-1]
    
    total_change = ((last_val - first_val) / abs(first_val)) * 100 if first_val != 0 else 0
    
    if total_change > 5:
        insights.append(
            f"Kinerja {kpi_col} menunjukkan pertumbuhan yang positif sepanjang periode analisis."
        )
        recommendations.append(
            "Pertahankan strategi bisnis yang saat ini berjalan karena memberikan hasil yang baik."
        )
    
    elif total_change < -5:
        insights.append(
            f"Terdapat penurunan {kpi_col} secara keseluruhan selama periode analisis."
        )
        recommendations.append(
            "Perlu dilakukan evaluasi terhadap biaya, harga, atau strategi penjualan."
        )
    
    else:
        insights.append(
            f"{kpi_col} relatif stabil tanpa perubahan besar."
        )
        recommendations.append(
            "Fokuskan strategi pada efisiensi dan optimasi operasional."
        )
    
    # ===============================
    # TAMPILKAN DALAM BAHASA EKSEKUTIF
    # ===============================
    st.markdown("### Ringkasan Utama")
    
    for i, text in enumerate(insights, 1):
        st.write(f"{i}. {text}")
    
    st.markdown("### Rekomendasi Bisnis")
    
    for i, text in enumerate(recommendations, 1):
        st.write(f"{i}. {text}")
    
    st.caption(
        "Insight ini disusun otomatis dari data historis dan bertujuan membantu "
        "manajemen memahami kondisi keuangan secara cepat dan sederhana."
    )
    
        
    st.subheader("Step 6 — Financial Health Snapshot (Executive Decision View)")

    # ===============================
    # VALIDASI DATA
    # ===============================
    if len(df_trend) < 2:
        st.warning("Data tidak cukup untuk penilaian kesehatan finansial.")
        st.stop()
    
    # ===============================
    # HITUNG INDIKATOR UTAMA
    # ===============================
    avg_value = df_trend[kpi_col].mean()
    volatility = df_trend[kpi_col].std()
    volatility_ratio = volatility / avg_value if avg_value != 0 else 0
    
    first_val = df_trend[kpi_col].iloc[0]
    last_val = df_trend[kpi_col].iloc[-1]
    growth_pct = ((last_val - first_val) / abs(first_val)) * 100 if first_val != 0 else 0
    
    # ===============================
    # KLASIFIKASI STABILITAS (BAHASA BISNIS)
    # ===============================
    if volatility_ratio < 0.25:
        stability_label = "Stabil"
    elif volatility_ratio < 0.4:
        stability_label = "Fluktuatif"
    else:
        stability_label = "Tidak Stabil"
    
    # ===============================
    # HITUNG FINANCIAL HEALTH SCORE
    # ===============================
    health_score = 100
    
    # penalti tren
    if growth_pct < -5:
        health_score -= 25
    elif growth_pct < 0:
        health_score -= 15
    
    # penalti stabilitas
    if volatility_ratio > 0.4:
        health_score -= 30
    elif volatility_ratio > 0.25:
        health_score -= 15
    
    health_score = max(40, health_score)
    
    # ===============================
    # STATUS EKSEKUTIF
    # ===============================
    if health_score >= 80:
        status = "🟢 Sehat"
        tone = st.success
    elif health_score >= 65:
        status = "🟡 Perlu Perhatian"
        tone = st.warning
    else:
        status = "🔴 Berisiko"
        tone = st.error
    
    # ===============================
    # TAMPILKAN SNAPSHOT UTAMA
    # ===============================
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Financial Health Score", f"{health_score} / 100")
    c2.metric("Status Keuangan", status)
    c3.metric("Stabilitas Pendapatan", stability_label)
    
    tone(
        f"Kondisi keuangan perusahaan saat ini dikategorikan sebagai **{status}**, "
        f"dengan tingkat stabilitas pendapatan **{stability_label.lower()}**."
    )
    
    # ===============================
    # INTERPRETASI EKSEKUTIF (NARATIF)
    # ===============================
    st.markdown("### Kesimpulan Eksekutif")
    
    summary = []
    
    if growth_pct > 5:
        summary.append("Kinerja pendapatan menunjukkan tren pertumbuhan yang sehat.")
    elif growth_pct < -5:
        summary.append("Pendapatan mengalami penurunan yang perlu segera dievaluasi.")
    else:
        summary.append("Pendapatan relatif stabil tanpa pertumbuhan signifikan.")
    
    if stability_label == "Tidak Stabil":
        summary.append("Fluktuasi pendapatan tinggi, berpotensi meningkatkan risiko operasional.")
    elif stability_label == "Fluktuatif":
        summary.append("Terdapat fluktuasi moderat yang masih perlu dipantau.")
    else:
        summary.append("Pendapatan menunjukkan kestabilan yang baik.")
    
    for s in summary:
        st.write("•", s)
    
    st.caption(
        "Kesimpulan eksekutif disusun berdasarkan kombinasi "
        "tren pertumbuhan (growth) dan tingkat stabilitas (volatilitas) pendapatan"
    )

    st.subheader("Step 7 — Financial Risk Early Warning")
    
    risk_alerts = []
    
    # ===============================
    # 1️⃣ RISIKO TREN MENURUN BERTURUT
    # ===============================
    recent_changes = df_trend[kpi_col].pct_change().tail(3)
    
    if (recent_changes < 0).sum() >= 2:
        risk_alerts.append(
            "Pendapatan mengalami penurunan pada beberapa periode terakhir. "
            "Jika tren ini berlanjut, dapat berdampak pada arus kas operasional."
        )
    
    # ===============================
    # 2️⃣ RISIKO VOLATILITAS TINGGI
    # ===============================
    if volatility_ratio > 0.4:
        risk_alerts.append(
            "Fluktuasi pendapatan tergolong tinggi. "
            "Kondisi ini meningkatkan risiko ketidakstabilan keuangan."
        )
    
    # ===============================
    # 3️⃣ RISIKO PERTUMBUHAN NEGATIF
    # ===============================
    if growth_pct < -5:
        risk_alerts.append(
            "Secara keseluruhan, pendapatan menunjukkan tren penurunan. "
            "Hal ini berpotensi menekan profitabilitas jika tidak segera ditangani."
        )
    
    # ===============================
    # 4️⃣ OUTPUT KE EKSEKUTIF
    # ===============================
    if not risk_alerts:
        st.success(
            "Tidak terdeteksi risiko finansial utama dalam jangka pendek. "
            "Kinerja keuangan berada dalam batas yang terkendali."
        )
    else:
        st.warning("⚠️ Risiko Finansial yang Perlu Perhatian Manajemen")
        for r in risk_alerts:
            st.write("•", r)
    
    st.caption(
        "Early warning ini bersifat indikatif dan bertujuan membantu manajemen "
        "mengenali potensi risiko sebelum berdampak lebih besar."
    )
    
    st.subheader("Step 8 — Executive Action Recommendation")
    
    actions = []
    
    # ===============================
    # STRATEGI BERDASARKAN KONDISI
    # ===============================
    if growth_pct < -5:
        actions.append(
            "Lakukan evaluasi menyeluruh terhadap struktur biaya dan strategi harga "
            "untuk menahan penurunan pendapatan."
        )
    
    if volatility_ratio > 0.4:
        actions.append(
            "Pertimbangkan diversifikasi sumber pendapatan guna mengurangi ketergantungan "
            "pada fluktuasi jangka pendek."
        )
    
    if growth_pct > 5 and volatility_ratio < 0.25:
        actions.append(
            "Kondisi keuangan cukup sehat untuk mendorong ekspansi atau peningkatan kapasitas bisnis."
        )
    
    if not actions:
        actions.append(
            "Fokuskan strategi pada efisiensi operasional dan penguatan fundamental bisnis."
        )
    
    # ===============================
    # OUTPUT KE EKSEKUTIF
    # ===============================
    st.markdown("### Rekomendasi Strategis")
    
    for i, act in enumerate(actions, 1):
        st.write(f"{i}. {act}")
    
    st.caption(
        "Rekomendasi ini disusun berdasarkan pola kinerja historis "
        "dan ditujukan sebagai panduan awal dalam pengambilan keputusan manajerial."
    )
    
