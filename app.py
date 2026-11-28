import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta
from collections import Counter
import re

from business_logic import urgensi

# ==========================================
# STATE UNTUK BUKA/TUTUP SIDEBAR
# ==========================================
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

st.set_page_config(
    page_title="Shopee 12.12 CS Triage — Admin Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS UTAMA (TANPA F-STRING AGAR AMAN DARI ERROR)
# ==========================================
st.markdown("""
    <style>
        /* Impor Font Poppins dari Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        /* Terapkan Poppins ke seluruh teks, tombol, input, sidebar, dan tabel */
        html, body, .stApp, [class*="css"],
        h1, h2, h3, h4, h5, h6, p, span, div, label, input, textarea, button,
        .admin-topbar, .admin-table, .admin-table th, .admin-table td {
            font-family: 'Poppins', sans-serif !important;
        }
    
        /* 1. Sembunyikan header & tombol bawaan Streamlit */
        [data-testid="stHeader"],
        [data-testid="stHeaderActionElements"],
        [data-testid="stToolbar"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        [data-testid="stIconMaterial"],
        .material-symbols-rounded,
        [class*="material-icons"],
        span[translate="no"] {
            font-family: 'Material Symbols Rounded', sans-serif !important;
        }

        .block-container {
            padding-top: 4.2rem !important;
            padding-left: 1.8rem !important;
            padding-right: 1.8rem !important;
            padding-bottom: 2rem !important;
            max-width: 100% !important;
        }
        .stApp, [data-testid="stAppViewContainer"] {
            background-color: #ECF0F5 !important;
            color: #333333 !important;
        }

        /* 2. Top Navbar Fixed di Atas (Warna Oranye Shopee) */
        .admin-topbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 80px;
            background-color: #EE4D2D;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 28px 0 68px;
            z-index: 999990;
            box-shadow: 0 2px 4px rgba(0,0,0,0.12);
            font-family: 'Source Sans Pro', sans-serif;
        }
        .admin-topbar .brand {
            font-size: 1.05rem;
            font-weight: 600;
            letter-spacing: 0.2px;
            padding: 14px 16px 14px 24px;
        }
        .admin-topbar .right-info {
            font-size: 13px;
            display: flex;
            gap: 20px;
            align-items: center;
            color: #FFFFFF !important;
        }

        /* 3. Tombol Hamburger (☰) di Pojok Kiri Topbar */
        div.st-key-toggle_sidebar_btn {
            position: fixed !important;
            top: 25px !important;
            left: 25px !important;
            z-index: 999999 !important;
            width: auto !important;
            
        }
        div.st-key-toggle_sidebar_btn button {
            background-color: rgba(0, 0, 0, 0.22) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.35) !important;
            border-radius: 4px !important;
            padding: 2px 10px !important;
            min-height: 36px !important;
            height: 36px !important;
        }
        div.st-key-toggle_sidebar_btn button:hover {
            background-color: rgba(0, 0, 0, 0.4) !important;
        }
        div.st-key-toggle_sidebar_btn button p {
            color: #FFFFFF !important;
            font-size: 18px !important;
            margin: 0 !important;
        }

        /* 4. Sidebar Gelap Khas AdminLTE (#222D32) */
        [data-testid="stSidebar"] {
            background-color: #222D32 !important;
            padding-top: 3.2rem !important;
            border-right: none !important;
        }
        [data-testid="stSidebar"] * {
            color: #B8C7CE !important;
        }
        .sidebar-profile {
            text-align: center;
            padding: 10px 10px 18px 10px;
            border-bottom: 1px solid #1A2226;
            margin-bottom: 10px;
        }
        .sidebar-profile h4 {
            color: #FFFFFF !important;
            margin: 6px 0 2px 0;
            font-size: 15px;
        }

        .sidebar-profile p,[data-testid="stSidebar"] .sidebar-profile p {
            color: #FFFFFF !important;
            font-size: 12px;
            margin: 0;
        }
        .nav-section-title {
            background-color: #1A2226;
            color: #FFFFFF !important;
            font-size: 11px;
            font-weight: 700;
            padding: 8px 14px;
            letter-spacing: 0.8px;
            margin-bottom: 8px;
            border-radius: 3px;
        }

        /* 5. Menu Navigasi Sidebar - Rata Kiri Penuh */
        [data-testid="stSidebar"] div[class*="st-key-menu_sidebar_"] {
            width: 100% !important;
            margin-bottom: 4px !important;
        }

        [data-testid="stSidebar"] div[class*="st-key-menu_sidebar_"] button {
            width: 100% !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            text-align: left !important;
            background-color: transparent !important;
            color: #FFFFFF !important;
            border: 1px solid transparent !important;
            border-left: 3px solid transparent !important;
            border-radius: 4px !important;
            box-shadow: none !important;
            padding: 10px 14px !important;
            transition: background-color 0.2s ease, border-color 0.2s ease;
        }

        /* Paksa pembungkus teks internal tombol Streamlit ikut rata kiri */
        [data-testid="stSidebar"] div[class*="st-key-menu_sidebar_"] button > div,
        [data-testid="stSidebar"] div[class*="st-key-menu_sidebar_"] [data-testid="stMarkdownContainer"] {
            width: 100% !important;
            display: flex !important;
            justify-content: flex-start !important;
            text-align: left !important;
        }

        [data-testid="stSidebar"] div[class*="st-key-menu_sidebar_"] button p {
            width: 100% !important;
            color: #FFFFFF !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            text-align: left !important;
            margin: 0 !important;
        }

        [data-testid="stSidebar"] div[class*="st-key-menu_sidebar_"] button:hover {
            background-color: #1E282C !important;
            border-left: 3px solid #EE4D2D !important;
        }

        /* Menu aktif */
        [data-testid="stSidebar"] div[class*="st-key-menu_sidebar_"] button[kind="primary"] {
            background-color: #1E282C !important;
            border-left: 3px solid #EE4D2D !important;
            border-top-color: transparent !important;
            border-right-color: transparent !important;
            border-bottom-color: transparent !important;
        }

        /* 6. Header Panel Kartu Putih & Jarak Ke Konten */
        .box-header-bar {
            background-color: #EE4D2D;
            color: #FFFFFF !important;
            padding: 12px 18px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 15px;
            margin-bottom: 18px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border: 1px solid #D2D6DE !important;
            border-radius: 6px !important;
            padding: 20px 18px 18px 18px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
        }

        /* 7. Warna Teks, Input, & Tombol di Area Konten Putih */
        .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label,
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
            color: #1F2937 !important;
        }
        textarea, input, [data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            color: #1F2937 !important;
            border: 1px solid #D2D6DE !important;
        }
        [data-baseweb="select"] span, [data-baseweb="select"] div {
            color: #1F2937 !important;
        }
        ul[role="listbox"] {
            background-color: #FFFFFF !important;
        }
        ul[role="listbox"] li {
            color: #1F2937 !important;
        }
        [data-testid="stFileUploaderDropzone"] {
            background-color: #F9FAFB !important;
            border: 1px dashed #B8C7CE !important;
        }
        .stButton > button, [data-testid="stDownloadButton"] > button {
            background-color: #F4F4F4 !important;
            color: #1F2937 !important;
            border: 1px solid #DDDDDD !important;
            border-radius: 4px !important;
        }
        .stButton > button[kind="primary"], [data-testid="stDownloadButton"] > button[kind="primary"] {
            background-color: #00A65A !important;
            color: #FFFFFF !important;
            border: none !important;
        }
        .stButton > button[kind="primary"] p, [data-testid="stDownloadButton"] > button[kind="primary"] p {
            color: #FFFFFF !important;
        }

        /* 8. Tabel HTML Rapi (Teks Keluhan Wrap ke Bawah) */
        .admin-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
            margin-top: 8px;
            margin-bottom: 10px;
            background-color: #FFFFFF;
        }
        .admin-table th {
            background-color: #F8FAFC;
            color: #334155 !important;
            font-weight: 600;
            text-align: left;
            padding: 10px 12px;
            border-bottom: 2px solid #E2E8F0;
            border-top: 1px solid #E2E8F0;
            white-space: nowrap;
        }
        .admin-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #E2E8F0;
            color: #1F2937 !important;
            vertical-align: top;
        }
        .admin-table tr:hover {
            background-color: #F9FAFB;
        }
        .col-keluhan {
            min-width: 280px;
            max-width: 420px;
            white-space: normal !important;
            word-wrap: break-word !important;
            line-height: 1.5;
        }
        .nowrap-cell {
            white-space: nowrap;
        }
        /* Animasi notifikasi otomatis hilang setelah 20 detik */
        @keyframes fadeOut5s {
            0%, 80% {
                opacity: 1;
                max-height: 100px;
                margin-bottom: 16px;
                padding: 14px 16px;
            }
            100% {
                opacity: 0;
                max-height: 0px;
                margin-bottom: 0px;
                padding: 0px;
                overflow: hidden;
                display: none;
            }
        }

        .auto-hide-alert {
            background-color: #EDFDF3;
            color: #166534 !important;
            border: 1px solid #BBF7D0;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            animation: fadeOut5s 5s forwards;
        }
    </style>
""", unsafe_allow_html=True)

# CSS dinamis buka/tutup sidebar
if st.session_state.sidebar_open:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: flex !important;
                visibility: visible !important;
                transform: translateX(0px) !important;
                width: 265px !important;
                min-width: 265px !important;
                max-width: 265px !important;
                position: relative !important;
                z-index: 999 !important;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none !important;
                width: 0px !important;
                min-width: 0px !important;
            }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# TOMBOL HAMBURGER (☰) BUKA/TUTUP SIDEBAR + TOPBAR
# ==========================================
if st.button("☰", key="toggle_sidebar_btn", help="Buka / Tutup Menu Navigasi"):
    st.session_state.sidebar_open = not st.session_state.sidebar_open
    st.rerun()

tanggal_hari_ini = datetime.now().strftime("%d-%B-%Y")
st.markdown(f"""
    <div class="admin-topbar">
        <div class="brand">🛍️ Sistem Triase Keluhan & Analitik Layanan Pelanggan Aplikasi Shopee</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# FUNGSI PREDIKSI SEMENTARA (DUMMY)
# ==========================================
def predict_tiket(teks: str, rating: int = None) -> dict:
    t = str(teks).lower()

    if any(k in t for k in ['resi', 'paket', 'kurir', 'spx', 'j&t', 'ongkir', 'kirim', 'nyangkut', 'tertahan']):
        kategori, conf = "Pengiriman", round(random.uniform(0.89, 0.98), 4)
    elif any(k in t for k in ['saldo', 'uang', 'transfer', 'bayar', 'shopeepay', 'refund', 'dana', 'terpotong', 'double']):
        kategori, conf = "Pembayaran", round(random.uniform(0.88, 0.97), 4)
    elif any(k in t for k in ['akun', 'hack', 'diretas', 'blokir', 'dibekukan', 'login', 'otp', 'sandi', 'password']):
        kategori, conf = "Akun", round(random.uniform(0.87, 0.96), 4)
    elif any(k in t for k in ['voucher', 'promo', 'diskon', 'cashback', 'rusak', 'pecah', 'palsu', 'barang', 'salah kirim']):
        kategori, conf = "Produk_dan_Promo", round(random.uniform(0.85, 0.95), 4)
    else:
        kategori, conf = "Teknis_Aplikasi", round(random.uniform(0.84, 0.94), 4)

    if rating == 1 or any(w in t for w in ['hilang', 'hack', 'diretas', 'tipu', 'parah', 'kecewa banget', 'diblokir']):
        sentimen = "Negatif Berat"
    else:
        sentimen = "Negatif"

    hasil_bisnis = urgensi(kategori=kategori, sentimen=sentimen, text_clean=teks, rating=rating)
    hasil_bisnis["badge"] = hasil_bisnis["level"]

    return {
        "kategori": kategori,
        "confidence": conf,
        "sentimen": sentimen,
        **hasil_bisnis
    }

# ==========================================
# DATA SIMULASI TIKET CS
# ==========================================
@st.cache_data
def load_sample_tickets():
    data = [
        # Oktober 2026 (Promo 10.10)
        {"id_tiket": "TKT-0995", "waktu": datetime(2026, 10, 10, 9, 15), "rating": 2,
         "teks": "Kurir lama mengantar paket padahal sudah lewat estimasi pengiriman 10.10."},
        {"id_tiket": "TKT-0996", "waktu": datetime(2026, 10, 10, 14, 30), "rating": 1,
         "teks": "Gagal bayar menggunakan ShopeePay saat checkout flash sale, saldo terpotong."},
        {"id_tiket": "TKT-0997", "waktu": datetime(2026, 10, 22, 11, 0), "rating": 2,
         "teks": "Aplikasi error dan lambat setelah update versi baru semalam."},
        # November 2026 (Promo 11.11)
        {"id_tiket": "TKT-0998", "waktu": datetime(2026, 11, 11, 10, 10), "rating": 1,
         "teks": "Resi SPX nyangkut di gudang sortir Jakarta selama 5 hari tidak bergerak."},
        {"id_tiket": "TKT-0999", "waktu": datetime(2026, 11, 11, 16, 45), "rating": 2,
         "teks": "Voucher gratis ongkir dan cashback 11.11 gagal digunakan di keranjang."},
        {"id_tiket": "TKT-1000", "waktu": datetime(2026, 11, 25, 13, 20), "rating": 1,
         "teks": "Akun saya tiba-tiba logout sendiri dan kode OTP tidak masuk."},
        # Desember 2026 (Puncak Promo 12.12)
        {"id_tiket": "TKT-1001", "waktu": datetime(2026, 12, 12, 9, 0), "rating": 1,
         "teks": "Saldo ShopeePay saya hilang Rp 1.500.000 padahal tidak ada transaksi, akun diduga kena hack! Tolong segera dibantu."},
        {"id_tiket": "TKT-1002", "waktu": datetime(2026, 12, 12, 10, 0), "rating": 1,
         "teks": "Paket dengan nomor resi SPXID04928172 statusnya paket hilang di gudang transit padahal barang elektronik mahal."},
        {"id_tiket": "TKT-1003", "waktu": datetime(2026, 12, 12, 11, 0), "rating": 2,
         "teks": "Pengiriman resi JP88271625 SPX nyangkut di hub Jakarta sudah 5 hari tidak bergerak sama sekali."},
        {"id_tiket": "TKT-1004", "waktu": datetime(2026, 12, 12, 12, 0), "rating": 1,
         "teks": "Pembayaran virtual account gagal bayar dan terpotong dua kali untuk pesanan 12.12, dana belum kembali."},
        {"id_tiket": "TKT-1005", "waktu": datetime(2026, 12, 12, 13, 0), "rating": 2,
         "teks": "Aplikasi selalu force close setelah update versi baru setiap kali mau klik checkout promo 12.12."},
        {"id_tiket": "TKT-1006", "waktu": datetime(2026, 12, 12, 14, 0), "rating": 2,
         "teks": "Barang sampai dalam kondisi pecah karena tidak pakai bubble wrap, saya sudah ajukan refund tapi belum direspon."},
        {"id_tiket": "TKT-1007", "waktu": datetime(2026, 12, 12, 16, 0), "rating": 1,
         "teks": "Akun saya tiba-tiba dibekukan permanen tanpa alasan jelas padahal masih ada saldo penjual."},
        {"id_tiket": "TKT-1008", "waktu": datetime(2026, 12, 12, 18, 0), "rating": 2,
         "teks": "Voucher gratis ongkir dan promo diskon 12.12 tidak bisa dipakai padahal syarat belanja sudah terpenuhi."},
    ]
    rows = []
    for item in data:
        pred = predict_tiket(item["teks"], rating=item["rating"])
        rows.append({**item, **pred})
    return pd.DataFrame(rows)

df_simulasi = load_sample_tickets()

# ==========================================
# SIDEBAR KIRI (PROFIL + MAIN NAVIGATION)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-profile">
            <div style="font-size: 48px;">🧑‍💻</div>
            <h4>Divisi Customer Care</h4>
            <p>Operasional Shopee</p>
        </div>
        <div class="nav-section-title">MAIN NAVIGATION</div>
    """, unsafe_allow_html=True)

    
    # Menu navigasi sidebar tanpa radio button
    daftar_menu = [
        "Data Tiket Masuk (Inbox)",
        "Cek Tiket Satuan",
        "Triase Massal (CSV)",
        "Dasbor Analitik Bisnis"
    ]

    if "menu_aktif" not in st.session_state:
        st.session_state.menu_aktif = daftar_menu[0]

    for i, nama_menu in enumerate(daftar_menu):
        aktif = st.session_state.menu_aktif == nama_menu

        if st.button(
            nama_menu,
            key=f"menu_sidebar_{i}",
            use_container_width=True,
            type="primary" if aktif else "secondary"
        ):
            st.session_state.menu_aktif = nama_menu
            st.rerun()

    menu = st.session_state.menu_aktif
    st.markdown("<hr style='border-color:#1A2226;'>", unsafe_allow_html=True)
    st.markdown("""
        <div style="font-size:12px; padding: 0 8px;">
            <b style="color:#FFF;">Panduan SLA:</b><br>
            🔴 Tinggi: &lt; 15 Menit<br>
            🟡 Menengah: &lt; 2 Jam<br>
            🟢 Rendah: &lt; 24 Jam
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# MENU 1: DATA TIKET MASUK (INBOX)
# ==========================================
if menu == "Data Tiket Masuk (Inbox)":
    st.markdown('<div class="box-header-bar">📥 Data Tiket Keluhan Masuk </div>', unsafe_allow_html=True)
    with st.container(border=True):
        c_urg, c_kat, c_btn, c_space, c_search = st.columns([1.5, 1.7, 1.3, 1.2, 2.3])

        with c_urg:
            filter_urg = st.selectbox(
                "Filter Urgensi:",
                ["Semua Urgensi", "Tinggi", "Menengah", "Rendah"],
                label_visibility="collapsed"
            )
        with c_kat:
            daftar_kategori = ["Semua Kategori"] + sorted(df_simulasi["kategori"].unique().tolist())
            filter_kat = st.selectbox(
                "Filter Kategori:",
                daftar_kategori,
                label_visibility="collapsed"
            )
        with c_btn:
            csv_inbox = df_simulasi.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "🖨️ Export CSV",
                data=csv_inbox,
                file_name="data_tiket_masuk.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_search:
            kata_cari = st.text_input(
                "Cari tiket:",
                placeholder="🔍 Search keluhan / ID tiket...",
                label_visibility="collapsed"
            )

        urutan_bobot = {"Tinggi": 1, "Menengah": 2, "Rendah": 3}
        df_tampil = df_simulasi.copy()
        df_tampil["bobot"] = df_tampil["level"].map(urutan_bobot)
        df_tampil = df_tampil.sort_values(by=["bobot", "waktu"], ascending=[True, True])

        if filter_urg != "Semua Urgensi":
            df_tampil = df_tampil[df_tampil["level"] == filter_urg]
        if filter_kat != "Semua Kategori":
            df_tampil = df_tampil[df_tampil["kategori"] == filter_kat]
        if kata_cari.strip() != "":
            df_tampil = df_tampil[
                df_tampil["teks"].str.contains(kata_cari, case=False, na=False) |
                df_tampil["id_tiket"].str.contains(kata_cari, case=False, na=False)
            ]

        rows_html = ""
        for idx, (_, row) in enumerate(df_tampil.iterrows(), start=1):
            kata_pemicu_str = ", ".join(row["kata_pemicu"]) if isinstance(row["kata_pemicu"], list) and len(row["kata_pemicu"]) > 0 else "-"
            conf_str = f"{row['confidence']*100:.1f}%"
            waktu_str = row["waktu"].strftime("%d-%m-%Y %H:%M")

            rows_html += (
                f'<tr>'
                f'<td class="nowrap-cell">{idx}</td>'
                f'<td class="nowrap-cell"><b>{row["id_tiket"]}</b></td>'
                f'<td class="nowrap-cell">{row["kategori"]}</td>'
                f'<td class="col-keluhan">{row["teks"]}</td>'
                f'<td>{kata_pemicu_str}</td>'
                f'<td class="nowrap-cell">{conf_str}</td>'
                f'<td class="nowrap-cell">{waktu_str}</td>'
                f'<td class="nowrap-cell">{row["level"]}</td>'
                f'<td class="nowrap-cell">{row["sla_target"]}</td>'
                f'<td class="nowrap-cell">{row["divisi"]}</td>'
                f'</tr>'
            )

        tabel_html = (
            '<div style="overflow-x: auto;">'
            '<table class="admin-table">'
            '<thead>'
            '<tr>'
            '<th>No</th>'
            '<th>No. Tiket</th>'
            '<th>Kategori</th>'
            '<th>Isi Keluhan Pelanggan</th>'
            '<th>Kata Pemicu</th>'
            '<th>Confidence</th>'
            '<th>Waktu Masuk</th>'
            '<th>Tingkat Urgensi</th>'
            '<th>Target SLA</th>'
            '<th>Divisi Eskalasi</th>'
            '</tr>'
            '</thead>'
            f'<tbody>{rows_html}</tbody>'
            '</table>'
            '</div>'
        )

        st.markdown(tabel_html, unsafe_allow_html=True)
        st.caption(f"Showing 1 to {len(df_tampil)} of {len(df_tampil)} entries")

# ==========================================
# MENU 2: CEK TIKET SATUAN
# ==========================================
elif menu == "Cek Tiket Satuan":
    st.markdown('<div class="box-header-bar">🔍 Klasifikasi Tiket Tunggal</div>', unsafe_allow_html=True)
    with st.container(border=True):
        teks_user = st.text_area(
            "Masukkan teks keluhan pelanggan:",
            height=120,
            placeholder="Ketik atau tempel isi keluhan pelanggan di sini..."
        )

        if st.button("➕ Klasifikasikan Tiket", type="primary"):
            if teks_user.strip() == "":
                st.warning("Silakan masukkan teks keluhan terlebih dahulu.")
            else:
                hasil = predict_tiket(teks_user)
                st.divider()
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Kategori Keluhan", hasil["kategori"])
                c2.metric("Tingkat Urgensi", hasil["badge"])
                c3.metric("Target SLA", hasil["sla_target"])
                c4.metric("Confidence Score", f"{hasil['confidence']*100:.1f}%")

                st.markdown(f"**Divisi Tujuan Eskalasi:** `{hasil['divisi']}`")
                st.markdown(f"**Kata Pemicu Terdeteksi:** {', '.join([f'`{k}`' for k in hasil['kata_pemicu']])}")

# ==========================================
# MENU 3: TRIASE MASSAL (CSV)
# ==========================================
elif menu == "Triase Massal (CSV)":
    st.markdown('<div class="box-header-bar">📂 Triase Massal File CSV</div>', unsafe_allow_html=True)
    with st.container(border=True):
        contoh_df = pd.DataFrame({
            "id_tiket": ["TKT-01", "TKT-02", "TKT-03"],
            "text_clean": [
                "Saldo saya hilang setelah transaksi gagal di aplikasi",
                "Paket dengan resi SPXID123456 tertahan sudah sem seminggu",
                "Aplikasi sering force close saat buka halaman live"
            ],
            "rating": [1, 2, 2]
        })
        st.download_button(
            label="📥 Unduh Template CSV",
            data=contoh_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="template_upload_cs.csv",
            mime="text/csv",
            key="btn_download_template_csv"
        )

        uploaded_file = st.file_uploader(
            "Unggah file CSV keluhan pelanggan sesuai template di atas (pastikan terdapat kolom `text_clean` atau `content`; kolom `id_tiket` dan `rating` bersifat opsional)",
            type=["csv"]
        )

        if uploaded_file is not None:
            try:
                df_upload = pd.read_csv(uploaded_file)
            except Exception as e:
                st.error(f"Gagal membaca file CSV: {e}")
                st.stop()

            kolom_teks = (
                "text_clean" if "text_clean" in df_upload.columns
                else ("content" if "content" in df_upload.columns else None)
            )

            if kolom_teks is None:
                st.error("⚠️ File CSV tidak sesuai format! Pastikan memiliki kolom `text_clean` atau `content`.")
            elif df_upload.empty:
                st.warning("⚠️ File CSV yang diunggah kosong (tidak ada baris data).")
            else:
                # Hapus kolom hasil prediksi lama jika pengguna mengunggah file hasil export sebelumnya
                kolom_prediksi = ["kategori", "confidence", "sentimen", "level", "badge", "sla_target", "kata_pemicu", "divisi"]
                df_bersih = df_upload.drop(columns=[c for c in kolom_prediksi if c in df_upload.columns])

                hasil_list = []
                for _, r in df_bersih.iterrows():
                    teks_input = "" if pd.isna(r[kolom_teks]) else str(r[kolom_teks])
                    rating_val = r["rating"] if "rating" in df_bersih.columns and pd.notna(r["rating"]) else None
                    hasil_list.append(predict_tiket(teks_input, rating=rating_val))

                df_final_batch = pd.concat([df_bersih.reset_index(drop=True), pd.DataFrame(hasil_list)], axis=1)
                # Pastikan kolom badge & level konsisten tanpa emoji
                df_final_batch["badge"] = df_final_batch["level"]

                st.markdown(
                    f'<div class="auto-hide-alert">Berhasil memproses {len(df_final_batch)} tiket keluhan!</div>',
                    unsafe_allow_html=True
                )

                # Render tabel HTML rapi agar teks panjang otomatis wrap ke bawah
                rows_batch_html = ""
                for idx, (_, row) in enumerate(df_final_batch.iterrows(), start=1):
                    id_tiket_str = row["id_tiket"] if "id_tiket" in df_final_batch.columns and pd.notna(row["id_tiket"]) else f"ROW-{idx}"
                    rating_str = row["rating"] if "rating" in df_final_batch.columns and pd.notna(row["rating"]) else "-"
                    kata_pemicu_str = ", ".join(row["kata_pemicu"]) if isinstance(row["kata_pemicu"], list) and len(row["kata_pemicu"]) > 0 else "-"
                    conf_str = f"{float(row['confidence'])*100:.1f}%"

                    rows_batch_html += (
                        f'<tr>'
                        f'<td class="nowrap-cell">{idx}</td>'
                        f'<td class="nowrap-cell"><b>{id_tiket_str}</b></td>'
                        f'<td class="col-keluhan">{row[kolom_teks]}</td>'
                        f'<td class="nowrap-cell">{rating_str}</td>'
                        f'<td class="nowrap-cell">{row["kategori"]}</td>'
                        f'<td class="nowrap-cell">{conf_str}</td>'
                        f'<td class="nowrap-cell">{row["sentimen"]}</td>'
                        f'<td class="nowrap-cell">{row["level"]}</td>'
                        f'<td class="nowrap-cell">{row["sla_target"]}</td>'
                        f'<td class="col-keluhan">{kata_pemicu_str}</td>'
                        f'<td class="nowrap-cell">{row["divisi"]}</td>'
                        f'</tr>'
                    )

                tabel_batch_html = (
                    '<div style="overflow-x: auto; max-height: 480px; border: 1px solid #E2E8F0; border-radius: 6px; margin-bottom: 14px;">'
                    '<table class="admin-table" style="margin-top: 0; margin-bottom: 0;">'
                    '<thead style="position: sticky; top: 0; z-index: 2;">'
                    '<tr>'
                    '<th>No</th>'
                    '<th>ID Tiket</th>'
                    '<th>Isi Keluhan Pelanggan</th>'
                    '<th>Rating</th>'
                    '<th>Kategori</th>'
                    '<th>Confidence</th>'
                    '<th>Sentimen</th>'
                    '<th>Tingkat Urgensi</th>'
                    '<th>Target SLA</th>'
                    '<th>Kata Pemicu</th>'
                    '<th>Divisi Eskalasi</th>'
                    '</tr>'
                    '</thead>'
                    f'<tbody>{rows_batch_html}</tbody>'
                    '</table>'
                    '</div>'
                )

                st.markdown(tabel_batch_html, unsafe_allow_html=True)

                st.download_button(
                    label="📤 Unduh Hasil Triase (.csv)",
                    data=df_final_batch.to_csv(index=False).encode("utf-8-sig"),
                    file_name="hasil_triase_cs.csv",
                    mime="text/csv",
                    type="primary",
                    key="btn_download_hasil_triase"
                )

# ==========================================
# MENU 4: DASBOR ANALITIK BISNIS
# ==========================================
# 2. Ganti MENU 4: DASBOR ANALITIK BISNIS
elif menu == "Dasbor Analitik Bisnis":
    st.markdown('<div class="box-header-bar">📊 Dasbor Analitik & Pemantauan Lonjakan Keluhan</div>', unsafe_allow_html=True)
    with st.container(border=True):
        # Baris Filter Kategori & Agregasi Waktu
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            opsi_kat = ["Semua Kategori"] + sorted(df_simulasi["kategori"].unique().tolist())
            pilih_kat = st.selectbox("Filter Kategori Keluhan:", opsi_kat, key="dasbor_kat")
        with f_col2:
            pilih_granularity = st.selectbox(
                "Tampilan Grafik Tren Waktu:",
                ["Per Bulan", "Per Hari", "Per Jam"],
                index=0,  # Default langsung Per Bulan
                key="dasbor_waktu"
            )
        with f_col3:
            opsi_urg = ["Semua Urgensi", "Tinggi", "Menengah", "Rendah"]
            pilih_urg = st.selectbox("Filter Tingkat Urgensi:", opsi_urg, key="dasbor_urg")

        df_dasbor = df_simulasi.copy()
        if pilih_kat != "Semua Kategori":
            df_dasbor = df_dasbor[df_dasbor["kategori"] == pilih_kat]
        if pilih_urg != "Semua Urgensi":
            df_dasbor = df_dasbor[df_dasbor["level"] == pilih_urg]

        st.divider()

        if df_dasbor.empty:
            st.warning("Tidak ada data tiket yang sesuai dengan filter yang dipilih.")
        else:
            # Ringkasan Kinerja Penanganan Tiket (KPI)
            total_tiket = len(df_dasbor)
            tiket_urgent = len(df_dasbor[df_dasbor["level"] == "Tinggi"])
            rasio_urgent = (tiket_urgent / total_tiket) * 100
            kategori_top = str(df_dasbor["kategori"].mode()[0]).replace("_", " ")

            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-around; align-items: center; gap: 16px; padding: 8px 0;">
                    <div style="flex: 1; text-align: center;">
                        <div style="font-size: 0.85rem; color: #4B5563; margin-bottom: 4px;">Total Keluhan Terpantau</div>
                        <div style="font-size: 1.85rem; font-weight: 700; color: #1F2937;">{total_tiket} Tiket</div>
                    </div>
                    <div style="flex: 1; text-align: center; border-left: 1px solid #E5E7EB; border-right: 1px solid #E5E7EB; padding: 0 12px;">
                        <div style="font-size: 0.85rem; color: #4B5563; margin-bottom: 4px;">Rasio Urgensi Tinggi (🔴)</div>
                        <div style="font-size: 1.85rem; font-weight: 700; color: #1F2937;">{tiket_urgent} Tiket ({rasio_urgent:.1f}%)</div>
                    </div>
                    <div style="flex: 1; text-align: center;">
                        <div style="font-size: 0.85rem; color: #4B5563; margin-bottom: 4px;">Kategori Keluhan Terbanyak</div>
                        <div style="font-size: 1.85rem; font-weight: 700; color: #1F2937;">{kategori_top}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.divider()

            # Baris 1 Grafik: Tren Lonjakan Waktu + Distribusi Kategori Keseluruhan
            col_c1, col_c2 = st.columns([1.4, 1])
            with col_c1:
                # 1. Urutkan DataFrame berdasarkan kolom waktu asli sebelum diformat menjadi string
                df_dasbor = df_dasbor.sort_values("waktu")

                if pilih_granularity == "Per Bulan":
                    df_dasbor["periode"] = df_dasbor["waktu"].dt.strftime("%Y-%m")
                    label_x = "Bulan"
                elif pilih_granularity == "Per Hari":
                    df_dasbor["periode"] = df_dasbor["waktu"].dt.strftime("%d %b %Y")
                    label_x = "Tanggal"
                else:
                    df_dasbor["periode"] = df_dasbor["waktu"].dt.strftime("%d %b %H:00")
                    label_x = "Jam"

                # 2. Simpan daftar urutan periode yang sudah kronologis
                urutan_periode = df_dasbor["periode"].drop_duplicates().tolist()

                tren_df = df_dasbor.groupby(["periode", "kategori"], sort=False).size().reset_index(name="jumlah")
                fig_line = px.line(
                    tren_df, x="periode", y="jumlah", color="kategori", markers=True,
                    title=f"Tren Lonjakan Keluhan ({pilih_granularity})",
                    labels={"periode": label_x, "jumlah": "Jumlah Tiket", "kategori": "Kategori"},
                    template="plotly_white"
                )

                # 3. Kunci urutan sumbu X sesuai array kronologis
                fig_line.update_xaxes(
                    type="category",
                    categoryorder="array",
                    categoryarray=urutan_periode
                )
                fig_line.update_layout(paper_bgcolor="white", plot_bgcolor="white", font_color="#1F2937")
                st.plotly_chart(fig_line, use_container_width=True)

            with col_c2:
                dist_df = df_dasbor["kategori"].value_counts().reset_index()
                dist_df.columns = ["Kategori", "Jumlah"]
                fig_pie = px.pie(
                    dist_df, values="Jumlah", names="Kategori", hole=0.45,
                    title="Distribusi Kategori Keluhan",
                    template="plotly_white"
                )
                fig_pie.update_layout(paper_bgcolor="white", plot_bgcolor="white", font_color="#1F2937")
                st.plotly_chart(fig_pie, use_container_width=True)

            # Baris 2 Grafik: Peta Isu Utama (Top Complaint Keywords)
            stopwords_id = {'saya', 'yang', 'di', 'ke', 'dari', 'dan', 'tidak', 'sudah', 'untuk', 'dengan', 'ini', 'itu', 'pada', 'saat', 'karena', 'ada', 'padahal', 'masih', 'bisa'}
            semua_kata = [
                k for teks in df_dasbor["teks"]
                for k in re.findall(r'\b[a-z]{3,}\b', teks.lower()) if k not in stopwords_id
            ]
            top_words = pd.DataFrame(Counter(semua_kata).most_common(10), columns=["Kata Kunci", "Frekuensi"])
            fig_words = px.bar(
                top_words.sort_values("Frekuensi", ascending=True),
                x="Frekuensi", y="Kata Kunci", orientation="h",
                title="Peta Isu Utama (Top 10 Kata Kunci Keluhan)",
                template="plotly_white",
                color_discrete_sequence=["#EE4D2D"]
            )
            fig_words.update_layout(paper_bgcolor="white", plot_bgcolor="white", font_color="#1F2937")
            st.plotly_chart(fig_words, use_container_width=True)