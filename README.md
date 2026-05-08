# UDB SSO Telegram Bot Automation

Proyek ini adalah bot Telegram yang dirancang untuk mengotomatisasi proses autentikasi *Single Sign-On* (SSO) pada portal mahasiswa Universitas Duta Bangsa (UDB). Melalui bot ini, pengguna dapat dengan mudah berinteraksi dengan portal akademis untuk mengekstrak dan menampilkan informasi seperti biodata serta status angket langsung melalui antarmuka pesan Telegram.

## Fitur Utama

- **Autentikasi SSO**: Mengotomatisasi proses login ke sistem portal mahasiswa.
- **Penyelesaian CAPTCHA Otomatis**: Menggunakan teknologi Optical Character Recognition (OCR) dengan pustaka `ddddocr`, yang dipadukan dengan pemrosesan gambar (*image processing*) melalui `OpenCV` untuk membersihkan derau (*noise*) dan membaca teks CAPTCHA secara cerdas.
- **Penyelesaian Altcha PoW**: Mengidentifikasi dan memecahkan tantangan kriptografi *Proof-of-Work* (Altcha) yang diperlukan saat proses login secara mulus.
- **Manajemen Sesi dan Jaringan Lanjutan**: Menggunakan `curl_cffi` yang mampu memalsukan TLS *fingerprint*, sehingga membuat request nampak seperti dari peramban (browser) asli untuk mencegah pemblokiran sesi.
- **Menu Ekstraksi Data**:
  - **Biodata**: Menarik informasi profil mahasiswa yang sedang login.
  - **Cek Angket**: Mengecek ketersediaan angket yang ada pada portal.

## Persyaratan Sistem

- Python 3.8 atau yang lebih baru.
- Token API Bot Telegram (bisa Anda dapatkan dari [BotFather](https://t.me/BotFather)).

## Instalasi

1. **Unduh Repositori**
   Pastikan seluruh file skrip (seperti `main.py` dan `requirements.txt`) berada dalam satu direktori kerja Anda.

2. **Instalasi Pustaka/Dependensi**
   Buka *Command Prompt* atau terminal pada direktori proyek, lalu jalankan perintah berikut untuk menginstal semua *requirements*:
   ```bash
   pip install -r requirements.txt
   ```

## Konfigurasi dan Penggunaan

1. **Konfigurasi Token**
   Buka file `main.py` menggunakan teks editor Anda, lalu pastikan Anda menyesuaikan variabel `BOT_TOKEN` dengan token bot milik Anda.
   ```python
   BOT_TOKEN = "YOUR TELEGRAM BOT TOKEN"
   ```

2. **Menjalankan Bot**
   Jalankan skrip utama melalui terminal:
   ```bash
   python main.py
   ```
   Jika sukses, akan muncul pesan `Bot Telegram berjalan...` di terminal.

3. **Interaksi via Telegram**
   - Cari bot Anda di aplikasi Telegram dan kirimkan perintah `/start`.
   - Bot akan memproses pengunduhan dan pemecahan *captcha*, lalu akan meminta **NIM** dan **Password** portal SSO Anda.
   - Jika autentikasi berhasil, menu *inline* akan ditampilkan. Anda dapat menekan tombol menu yang ada untuk melihat Biodata atau mengecek Angket.
