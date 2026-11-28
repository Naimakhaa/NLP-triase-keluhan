"""Logika model untuk aplikasi triase keluhan.

FERRY: ganti isi muat_model() dan _prediksi_model() dengan model asli (IndoBERT / baseline),
lalu set DUMMY = False. Praproses harus sama persis dengan saat training (import dari praproses.py).

Alur predict():  teks -> praproses (clean_text) -> model/dummy -> kategori + sentimen
                 -> business_logic.urgensi() -> level, SLA, kata pemicu, divisi
"""
import re

from business_logic import urgensi as hitung_urgensi

try:
    from praproses import clean_text_func   # praproses yang sama dengan saat training
except Exception:                           # cadangan jika Sastrawi belum terpasang
    def clean_text_func(text):
        
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", str(text).lower())).strip()

DUMMY = True   # True = model tiruan untuk menguji tampilan. Ubah ke False setelah model asli terpasang.


def muat_model(nama: str):
    # TODO (Ferry): muat model sesuai `nama` ("IndoBERT (utama)" atau "Baseline TF-IDF + Logistic Regression")
    return None


def _prediksi_model(model, text_clean: str) -> tuple:
    """TODO (Ferry): kembalikan (kategori, sentimen, confidence) dari model asli.
    Input memakai text_clean (BUKAN hasil stemming, kecuali baseline TF-IDF dilatih dengan stem_text)."""
    raise NotImplementedError("Model asli belum dipasang. Set DUMMY = True atau isi _prediksi_model().")


def _prediksi_dummy(t: str) -> tuple:
    """Model tiruan berbasis kata kunci, hanya untuk menguji tampilan."""
    # Urutan penting: yang paling spesifik lebih dulu
    if re.search(r"login|akun|otp|password|sandi|blokir|banned|hack|retas|verifikasi", t):
        kategori = "Akun"
    elif re.search(r"force close|error|eror|lemot|\blag\b|crash|\bbug\b|blank|layar putih|loading|update", t):
        kategori = "Teknis_Aplikasi"
    elif re.search(r"saldo|refund|paylater|spaylater|spinjam|transfer|top ?up|shopeepay|tagihan|limit|terpotong|gagal bayar|dana belum", t):
        kategori = "Pembayaran"
    elif re.search(r"voucher|promo|diskon|cashback|gratis ongkir|flash sale|rusak|retur|pengembalian barang|warna|ukuran|salah|cacat|palsu|tidak sesuai", t):
        kategori = "Produk_dan_Promo"
    elif re.search(r"resi|paket|kurir|kirim|ongkir|ekspedisi|spx|jne|j t", t):
        kategori = "Pengiriman"
    else:
        kategori = "Lainnya"

    negatif = re.search(r"tidak|gagal|error|rusak|lama|lambat|palsu|tipu|kecewa|parah|hilang|salah|belum|force close|lag", t)
    positif = re.search(r"terima kasih|bagus|mantap|puas|bagus banget|recommended", t)
    berat = re.search(r"parah|kecewa banget|sangat kecewa|kapok|rugi besar|tolong segera|secepatnya|penipuan|ditipu", t)
    if berat:
        sentimen = "Negatif Berat"
    elif negatif:
        sentimen = "Negatif"
    elif positif:
        sentimen = "Positif"
    else:
        sentimen = "Netral"

    return kategori, sentimen, round(0.6 + (len(t) % 35) / 100, 4)


def predict(model, text: str, rating: int = None) -> dict:
    """Kontrak keluaran, dipakai app.py:
    {"kategori": "Pengiriman|Teknis_Aplikasi|Pembayaran|Produk_dan_Promo|Akun|Lainnya",
     "sentimen": "Negatif Berat|Negatif|Netral|Positif",
     "urgensi": "Tinggi|Menengah|Rendah",
     "confidence": float antara 0 dan 1,
     "detail_urgensi": {"level","badge","sla_target","kata_pemicu","divisi"}}   # tambahan dari business_logic
    """
    text_clean = clean_text_func(text)
    if DUMMY:
        kategori, sentimen, confidence = _prediksi_dummy(text_clean)
    else:
        kategori, sentimen, confidence = _prediksi_model(model, text_clean)

    detail = hitung_urgensi(kategori, sentimen, text_clean, rating)
    return {"kategori": kategori, "sentimen": sentimen, "urgensi": detail["level"],
            "confidence": confidence, "detail_urgensi": detail}


def predict_batch(model, texts, ratings=None):
    ratings = ratings if ratings is not None else [None] * len(texts)
    return [predict(model, t, r) for t, r in zip(texts, ratings)]