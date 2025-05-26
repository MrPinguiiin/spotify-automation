# Spotify Automation Script - EDUKASI SAJA

## ⚠️ PERINGATAN PENTING

**Script ini dibuat untuk keperluan EDUKASI dan PENELITIAN saja!**

### 🚨 LARANGAN PENGGUNAAN:
- ❌ Jangan gunakan untuk membuat akun Spotify secara massal
- ❌ Jangan gunakan untuk bypass sistem pembayaran
- ❌ Jangan gunakan untuk tujuan komersial
- ❌ Jangan gunakan untuk melanggar Terms of Service

### ⚖️ KONSEKUENSI HUKUM:
Penggunaan script ini untuk tujuan melanggar ToS dapat berakibat:
- Pemblokiran akun permanen
- Tindakan hukum dari Spotify
- Pelanggaran kebijakan payment processor
- Masalah dengan pihak berwenang

## 📋 Deskripsi

Script Python ini mendemonstrasikan konsep automation web menggunakan Selenium untuk:
- Simulasi pengisian form signup
- Demonstrasi interaksi dengan web elements
- Contoh penggunaan undetected-chromedriver
- Pembelajaran tentang web automation

## 🛠️ Instalasi

### 1. Clone atau Download Project
```bash
git clone <repository-url>
cd spotify-automation
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Chrome Browser
Pastikan Google Chrome sudah terinstall di sistem Anda.

## 📁 Struktur File

```
spotify-automation/
├── spotify_automation.py    # Script utama
├── requirements.txt         # Dependencies Python
├── vcc_data.txt            # Data VCC untuk demo (fake)
├── README.md               # Dokumentasi ini
├── created_accounts.csv    # Output hasil simulasi (auto-generated)
└── spotify_automation.log  # Log file (auto-generated)
```

## 🎯 Fitur

### ✅ Yang Dilakukan Script:
- Setup Chrome driver dengan stealth options
- Generate fake user data untuk demo
- Navigasi ke halaman signup Spotify
- Simulasi pengisian form signup
- Load data VCC dari file untuk demo
- Logging semua aktivitas
- Save hasil simulasi ke CSV

### ❌ Yang TIDAK Dilakukan (untuk keamanan):
- Submit form signup yang sebenarnya
- Proses pembayaran aktual
- Bypass captcha atau security
- Verifikasi email otomatis

## 🔧 Konfigurasi

### Format Data VCC (vcc_data.txt):
```
4111111111111111,12,2025,123,John Doe
4222222222222222,06,2026,456,Jane Smith
```

Format: `nomor_kartu,bulan,tahun,cvv,nama_pemegang`

**Catatan:** Data VCC di atas adalah contoh fake dan tidak akan berfungsi!

## 🚀 Cara Menjalankan

### 1. Mode Demo (Aman):
```bash
python spotify_automation.py
```

### 2. Input yang Diperlukan:
- Konfirmasi bahwa ini untuk edukasi saja
- Jumlah akun yang akan disimulasi (max 3)

### 3. Output:
- Log di terminal dengan warna
- File `created_accounts.csv` dengan data simulasi
- File `spotify_automation.log` dengan log detail

## 📊 Output Files

### created_accounts.csv:
```csv
Email,Password,Name,Status,Timestamp
user1234@gmail.com,Pass5678!,Ahmad Rahman,Success,2024-01-15 10:30:45
```

### spotify_automation.log:
```
2024-01-15 10:30:45 - INFO - Starting automation process...
2024-01-15 10:30:46 - INFO - Chrome driver setup complete
```

## 🔍 Teknologi yang Digunakan

- **Python 3.7+**: Bahasa pemrograman utama
- **Selenium**: Web automation framework
- **undetected-chromedriver**: Stealth Chrome driver
- **fake-useragent**: Random user agent generator
- **colorama**: Colored terminal output
- **webdriver-manager**: Automatic driver management

## 🎓 Tujuan Edukasi

Script ini dibuat untuk mempelajari:
1. **Web Automation**: Cara menggunakan Selenium
2. **Stealth Techniques**: Bypass deteksi automation
3. **Data Handling**: Membaca/menulis file CSV
4. **Error Handling**: Exception handling yang proper
5. **Logging**: Sistem logging yang baik
6. **Code Structure**: Organisasi kode OOP

## 🛡️ Keamanan & Etika

### Langkah Keamanan yang Diimplementasikan:
- Submit form di-disable secara default
- Maksimal 3 akun untuk demo
- Peringatan jelas di setiap langkah
- Tidak menyimpan data sensitif
- Disclaimer yang jelas

### Prinsip Etika:
- Transparansi tujuan edukasi
- Tidak merugikan platform
- Menghormati Terms of Service
- Edukasi tentang risiko hukum

## 🚨 Disclaimer Legal

1. **Penulis tidak bertanggung jawab** atas penyalahgunaan script ini
2. **Pengguna bertanggung jawab penuh** atas konsekuensi penggunaan
3. **Script ini melanggar ToS Spotify** jika digunakan secara aktual
4. **Gunakan hanya untuk pembelajaran** dan penelitian

## 🤝 Kontribusi

Jika Anda ingin berkontribusi untuk tujuan edukasi:
1. Fork repository
2. Buat branch untuk fitur edukasi baru
3. Tambahkan disclaimer yang jelas
4. Submit pull request

## 📞 Support

Untuk pertanyaan terkait edukasi dan pembelajaran:
- Buka issue di GitHub
- Diskusi hanya untuk tujuan pembelajaran
- Tidak memberikan support untuk penggunaan ilegal

## 📚 Referensi Pembelajaran

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Python Ethics in Web Scraping](https://docs.python.org/3/library/robotparser.html)
- [Web Automation Best Practices](https://selenium.dev/documentation/guidelines/)

---

**🎯 Ingat: Script ini HANYA untuk pembelajaran! Gunakan pengetahuan ini secara bertanggung jawab dan etis.** 