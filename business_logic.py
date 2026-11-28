"""
business_logic.py
Modul Aturan Bisnis & Prioritas Urgensi Layanan Pelanggan Aplikasi Shopee

Catatan Asumsi Metodologi:
- Target SLA (< 15 Menit, < 2 Jam, < 24 Jam) dan daftar kata pemicu ditetapkan
  sebagai asumsi operasional berdasarkan matriks dampak risiko bisnis:
  1. Tinggi   (< 15 Menit) : Risiko kerugian finansial langsung, peretasan akun, penipuan, & paket hilang.
  2. Menengah (< 2 Jam)    : Hambatan transaksi/pengiriman/akses akun, produk bermasalah, & aplikasi tidak bisa dipakai.
  3. Rendah   (< 24 Jam)   : Keluhan umum/informasi/performa ringan tanpa dampak finansial mendesak.
- Kategori Akun dan Pembayaran tidak pernah di bawah Menengah, karena menyangkut akses dan uang pelanggan.
"""
import re


def _cocok_kata(daftar: list, teks: str) -> list:
    """Cocokkan kata atau frasa utuh (bukan potongan kata), agar 'lag' tidak cocok dengan 'lagi'."""
    return [k for k in daftar if re.search(rf'(?<![a-z0-9]){re.escape(k)}(?![a-z0-9])', teks)]


def urgensi(kategori: str, sentimen: str = None, text_clean: str = "", rating: int = None) -> dict:
    """
    Menentukan tingkat urgensi tiket layanan pelanggan.

    Parameter:
    - kategori   : Label kategori hasil klasifikasi model.
    - sentimen   : Label sentimen hasil prediksi model (opsional).
    - text_clean : Teks keluhan bersih berimbuhan (hindari hasil stemming agar kata berimbuhan tetap terbaca).
    - rating     : Skor bintang ulasan 1-5 sebagai cadangan jika sentimen kosong (opsional).
    """
    teks = str(text_clean).lower().strip()
    kategori_norm = str(kategori).strip().replace(" ", "_") if kategori else ""

    # 1. Pemicu TINGGI (Finansial, Keamanan Akun, Penipuan, Barang Hilang, Eskalasi Hukum)
    pemicu_tinggi = [
        'saldo hilang', 'uang hilang', 'uang tidak masuk', 'dana belum kembali',
        'saldo terpotong', 'terpotong dua kali', 'double bayar',
        'kena hack', 'dihack', 'di hack', 'diretas', 'retas', 'akun hilang',
        'diblokir', 'dibekukan', 'banned', 'dibanned',
        'penipuan', 'tipu', 'palsu',
        'paket hilang', 'kurir kabur',
        'lapor polisi', 'ojk', 'ylki'
    ]

    # 2. Pemicu MENENGAH (Hambatan operasional, produk bermasalah, aplikasi tidak bisa dipakai)
    pemicu_menengah = [
        'tertahan', 'nyangkut', 'tidak bergerak',
        'rusak', 'pecah', 'cacat', 'salah kirim', 'salah warna', 'salah ukuran', 'tidak sesuai',
        'refund', 'pengembalian',
        'gagal bayar', 'gagal checkout', 'gagal top up', 'topup gagal',
        'otp tidak masuk', 'otp tidak muncul', 'tidak bisa login', 'gagal login',
        'force close', 'error', 'crash', 'bug', 'blank', 'layar putih', 'layar hitam',
        'tidak bisa dibuka', 'keluar sendiri', 'loading terus'
    ]

    # 3. Pemicu RENDAH (Keluhan umum, performa ringan, pertanyaan informasi)
    pemicu_rendah = [
        'voucher', 'promo', 'diskon', 'cashback', 'gratis ongkir', 'klaim',
        'lambat', 'lemot', 'berat', 'lag', 'notifikasi', 'tampilan',
        'cara', 'kenapa', 'kapan', 'info', 'pertanyaan', 'syarat'
    ]

    # 4. Indikator emosi negatif berat (cadangan jika label sentimen model kurang tajam)
    indikator_emosi_berat = ['parah', 'kecewa banget', 'sangat kecewa', 'kapok', 'rugi besar', 'tolong segera']

    temuan_tinggi = _cocok_kata(pemicu_tinggi, teks)
    temuan_menengah = _cocok_kata(pemicu_menengah, teks)
    temuan_rendah = _cocok_kata(pemicu_rendah, teks)

    sentimen_norm = str(sentimen).lower().strip() if sentimen else ""
    is_negatif_berat = (
        sentimen_norm in ['negatif berat', 'sangat negatif', 'very negative', 'negative_high']
        or (rating == 1 and not sentimen_norm)
        or any(kata in teks for kata in indikator_emosi_berat)
    )

    divisi_tujuan = {
        "Pembayaran": "Tim Keuangan & Rekonsiliasi",
        "Akun": "Tim Keamanan Akun & Fraud",
        "Pengiriman": "Tim Operasional Logistik",
        "Produk_dan_Promo": "Tim Resolusi Komplain & Retur",
        "Teknis_Aplikasi": "Tim Dukungan Teknis (IT)"
    }

    # Penentuan prioritas
    if temuan_tinggi or (kategori_norm in ['Akun', 'Pembayaran'] and is_negatif_berat):
        level, badge, sla = "Tinggi", "Tinggi", "< 15 Menit"
        pemicu = temuan_tinggi if temuan_tinggi else [f"Kategori kritis ({kategori}) + Indikasi emosi berat"]
    elif (
        temuan_menengah
        or kategori_norm in ['Akun', 'Pembayaran']
        or (kategori_norm == 'Pengiriman' and not temuan_rendah)
    ):
        level, badge, sla = "Menengah", "Menengah", "< 2 Jam"
        pemicu = temuan_menengah if temuan_menengah else [f"Kendala operasional ({kategori})"]
    else:
        level, badge, sla = "Rendah", "Rendah", "< 24 Jam"
        pemicu = temuan_rendah if temuan_rendah else [f"Keluhan umum / informasi ({kategori})"]

    return {
        "level": level,
        "badge": badge,
        "sla_target": sla,
        "kata_pemicu": pemicu,
        "divisi": divisi_tujuan.get(kategori_norm, "Tim Layanan Pelanggan Umum")
    }