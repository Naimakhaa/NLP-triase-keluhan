# Sistem Triase Keluhan Pelanggan Otomatis

Tugas Akhir Project-Based Learning (PjBL), Mata Kuliah Natural Language Processing (NLP), Program Studi Sistem Informasi.

Prototipe sistem yang membaca teks tiket keluhan pelanggan e-commerce, lalu menghasilkan:

- Kategori keluhan (5 kategori)
- Sentimen (mendeteksi sentimen negatif)
- Tingkat urgensi (Tinggi / Menengah / Rendah) untuk menentukan eskalasi
- Confidence prediksi

## Tim

| Nama | Peran | Fokus | Branch |
|---|---|---|---|
| Rizma | Ketua dan Analis Bisnis | Desain label, aturan urgensi, UI, analisis dampak bisnis, penggabungan laporan | `rizma` |
| Ghina | Data Scientist | Sampling, weak labeling, praproses, split data, evaluasi | `ghina` |
| Ferry | AI Engineer | Baseline, fine-tuning IndoBERT, model sentimen, `predict()`, logika aplikasi | `ferry` |

## Data

- Sumber: ulasan Shopee 12.12 (hasil scraping), `scrapped_Shopee_12_12_ID_.csv`.
- Sampel: 3.000 ulasan, `reviewId` unik, rating hanya 1-2 (ulasan bernada keluhan).
- Lima kategori keluhan muncul di sampel, dengan aturan khusus untuk kasus ambigu (lihat `docs/panduan_pelabelan.md`).
- Label dibuat dengan weak labeling (aturan), lalu dikoreksi manual pada gold set.

| File | Isi | Ukuran |
|---|---|---|
| `data/sampel_3000.csv` | Sampel awal, termasuk 300 baris gold | 3.000 |
| `data/sampel_proc.csv` | Hasil praproses (`text_clean`, `text_stem`) | 3.000 |
| `data/train.csv` | Data latih | 2.160 |
| `data/val.csv` | Data validasi | 540 |
| `data/gold_final.csv` | Gold set berlabel manual (tidak ikut training) | 300 |
| `data/test_tiket_cs.csv` | 90 contoh tiket CS buatan sendiri (30 per anggota) | 90 |

**Aturan penting:**

- Tidak ada `reviewId` gold di `train.csv` maupun `val.csv`.
- Skor utama dilaporkan pada gold set, bukan pada val.
- Test set tiket CS dipakai untuk menguji kemampuan model pada gaya tiket asli (nomor resi, kronologi). Penurunan skor di sini dicatat sebagai temuan, bukan disembunyikan.
- Aturan pelabelan tidak boleh disetel berulang sambil melihat skor gold.

## Pipeline

```
Ulasan/tiket -> praproses.py -> [Model kategori] ----\
                                [Model sentimen]  ----+-> urgensi() -> kategori, sentimen, urgensi, confidence
                                                      /
```

- **Baseline:** TF-IDF + Logistic Regression
- **Model utama:** fine-tuning IndoBERT (input `text_clean`)
- **Sentimen:** model pre-trained (Hugging Face)
- **Urgensi:** fungsi aturan `urgensi(kategori, sentimen, teks)`

## Struktur Repositori

```
.
├── data/                       # Dataset (hanya CSV kecil yang diunggah)
├── notebooks/
│   ├── 01_sampling_praproses.ipynb      # Ghina
│   ├── 02_baseline_indobert.ipynb       # Ferry
│   └── 03_evaluasi.ipynb                # Ghina
├── src/
│   ├── praproses.py            # Satu file praproses, dipakai training DAN aplikasi
│   ├── urgensi.py              # Rizma
│   └── predict.py              # Ferry
├── docs/
│   ├── panduan_pelabelan.md
│   └── catatan_kontribusi.md
├── app.py                      # Antarmuka (Streamlit/Gradio)
├── requirements.txt
└── README.md
```

# Panduan Kolaborasi Git

## Aturan Utama

- Dilarang commit/push langsung ke `main`. Semua pekerjaan lewat branch masing-masing, lalu digabung dengan Pull Request.
- Satu orang satu branch dan satu orang satu file utama. Jangan mengedit file milik anggota lain tanpa koordinasi.
- Setiap Pull Request direview minimal 1 anggota lain sebelum di-merge.
- Commit sering dengan pesan yang jelas. Riwayat commit dipakai sebagai bukti kontribusi untuk peer review.
- Jangan mengunggah file besar atau rahasia (API key, token, model besar).
- Gunakan seed tetap (`random_state=42`) pada semua proses acak agar hasil bisa direproduksi.

## Langkah Kerja

### Rizma (branch `rizma`)

```bash
# 1. Clone (sekali saja)
git clone https://github.com/USERNAME/NLP_triase_keluhan.git
cd NLP_triase_keluhan

# 2. Buat branch sendiri (sekali saja)
git checkout -b rizma

# 3. Sebelum mulai bekerja, ambil versi terbaru
git checkout main
git pull origin main
git checkout rizma
git merge main

# 4. Commit dan push
git add .
git commit -m "feat: tambah fungsi urgensi"
git push origin rizma
```

### Ghina (branch `ghina`)

```bash
# 1. Clone (sekali saja)
git clone https://github.com/USERNAME/NLP_triase_keluhan.git
cd NLP_triase_keluhan

# 2. Buat branch sendiri (sekali saja)
git checkout -b ghina

# 3. Sebelum mulai bekerja, ambil versi terbaru
git checkout main
git pull origin main
git checkout ghina
git merge main

# 4. Commit dan push
git add .
git commit -m "data: tambah sampel 3000 dan weak labeling"
git push origin ghina
```

### Ferry (branch `ferry`)

```bash
# 1. Clone (sekali saja)
git clone https://github.com/USERNAME/NLP_triase_keluhan.git
cd NLP_triase_keluhan

# 2. Buat branch sendiri (sekali saja)
git checkout -b ferry

# 3. Sebelum mulai bekerja, ambil versi terbaru
git checkout main
git pull origin main
git checkout ferry
git merge main

# 4. Commit dan push
git add .
git commit -m "feat: baseline TF-IDF dan Logistic Regression"
git push origin ferry
```

### Setelah push

1. Di GitHub, klik **Compare & pull request**, isi deskripsi singkat, pilih 1 reviewer, lalu **Create pull request**.
2. Reviewer memeriksa tab **Files changed**, memberi komentar bila perlu, lalu **Approve** dan **Merge pull request**.
3. Semua anggota kembali ke langkah 3 untuk menyinkronkan branch.
